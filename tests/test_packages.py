import json
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import warnings
import zipfile
from ctf_author.packaging import package_challenge
from ctf_author.runtime import ContractError, file_hash
from ctf_author.runner import Runner
from ctf_author.sources import REQUIRED, source_files
from ctf_author.validation import read_spec, validate
from ctf_author.verification import verify_package

ROOT = Path(__file__).resolve().parents[1]


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='ctf-package-tests-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.spec = json.loads((ROOT/'examples/forensics/challenge.json').read_text(encoding='utf-8'))
        self.members = {'challenge/'+name: (ROOT/'examples/forensics'/name).read_bytes() for name in REQUIRED}
        self.members.update({'VALIDACION.json': b'{"status":"APROBADO"}', 'ENTREGA_PRIVADA.txt': b'Private delivery'})

    def archive(self, changes=None, remove=(), extra=()):
        members = dict(self.members)
        members.update(changes or {})
        for name in remove:
            members.pop(name, None)
        path = self.root/'delivery.zip'
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            with zipfile.ZipFile(path, 'w') as z:
                for name, data in members.items():
                    z.writestr(name, data)
                for name, data in extra:
                    z.writestr(name, data)
        return path

    def spec_bytes(self, **changes):
        return json.dumps(dict(self.spec, **changes)).encode()

    def test_static_check_never_executes_and_ignores_claimed_approval(self):
        code = b'raise RuntimeError("THIS MUST NEVER EXECUTE")'
        path = self.archive({'challenge/generate.py': code, 'VALIDACION.json': b'{"status":"RECHAZADO"}'})
        with patch('subprocess.run', side_effect=AssertionError('No execution')):
            result = verify_package(path)
        self.assertEqual(result['status'], 'VERIFICADO', result)

    def test_missing_required_files_rejected_even_if_report_says_approved(self):
        for name in REQUIRED:
            with self.subTest(name=name):
                self.assertEqual(verify_package(self.archive(remove=['challenge/'+name]))['status'], 'RECHAZADO')

    def test_protocol_and_environment_schema_checked(self):
        path = self.archive({'challenge/challenge.json': self.spec_bytes(schema_version=2)})
        self.assertEqual(verify_package(path)['status'], 'RECHAZADO')
        path = self.archive({'challenge/environment.json': b'{"python":"arbitrary"}'})
        self.assertEqual(verify_package(path)['status'], 'RECHAZADO')

    def test_declared_resources_and_auxiliary_scripts_preserved(self):
        source = self.root/'source'
        shutil.copytree(ROOT/'examples/forensics', source)
        (source/'assets').mkdir()
        (source/'assets/image.bin').write_bytes(b'synthetic image')
        (source/'build').mkdir()
        (source/'build/fixture.bin').write_bytes(b'needed prebuilt resource')
        (source/'cleanup.py').write_text('# cleanup reference\n', encoding='utf-8')
        (source/'environment.json').write_text(json.dumps({'python':'3.13','system_requirements':[], 'setup_notes':''}), encoding='utf-8')
        spec = dict(self.spec, source_paths=['build/fixture.bin'])
        (source/'challenge.json').write_text(json.dumps(spec), encoding='utf-8')
        path = self.root/'complete.zip'
        report = package_challenge(source, path, Runner('local'))
        self.assertEqual(report['status'], 'APROBADO')
        self.assertEqual(report['package_verification'], 'VERIFICADO')
        with zipfile.ZipFile(path) as z:
            for name in ('assets/image.bin', 'build/fixture.bin', 'cleanup.py', 'environment.json', 'WRITEUP_PRIVADO.md'):
                self.assertIn('challenge/'+name, z.namelist())
        self.assertEqual(verify_package(path, report['package_sha256'])['status'], 'VERIFICADO')

    def test_missing_declared_resource_rejected(self):
        path = self.archive({'challenge/challenge.json': self.spec_bytes(source_paths=['missing.bin'])})
        self.assertEqual(verify_package(path)['status'], 'RECHAZADO')

    def test_dangerous_and_ambiguous_paths_rejected(self):
        names = ('../escape', '/absolute', 'C:/escape', 'challenge/../escape',
                 'challenge/assets/../x', 'challenge/assets\\x', 'challenge/assets/CON.txt',
                 'challenge/assets/x.', 'challenge/assets/x ', 'challenge/assets//x',
                 'challenge/assets/x:stream', 'challenge/assets/\x00hidden')
        for name in names:
            with self.subTest(name=name):
                # ZipFile normaliza estos nombres al escribir en Windows. Construir
                # el encabezado adversarial real sin perder ni sustituir sus bytes.
                safe = name.replace('\\', '@').replace('\x00', '@')
                path = self.archive(extra=[(safe, b'x')])
                if safe != name:
                    path.write_bytes(path.read_bytes().replace(safe.encode(), name.encode()))
                self.assertEqual(verify_package(path)['status'], 'RECHAZADO')

    def test_duplicate_entries_and_case_aliases_rejected(self):
        for name in ('challenge/generate.py','challenge/GENERATE.PY'):
            with self.subTest(name=name):
                self.assertEqual(verify_package(self.archive(extra=[(name,b'other')]))['status'],'RECHAZADO')
        path=self.archive(extra=[('challenge/assets/A/a.bin',b'1'),('challenge/assets/a/b.bin',b'2')])
        self.assertEqual(verify_package(path)['status'],'RECHAZADO')

    def test_symlink_rejected(self):
        link = zipfile.ZipInfo('challenge/assets/link')
        link.create_system = 3
        link.external_attr = (stat.S_IFLNK | 0o777) << 16
        self.assertEqual(verify_package(self.archive(extra=[(link,b'../../outside')]))['status'],'RECHAZADO')

    def test_file_directory_conflict_rejected(self):
        path=self.archive(extra=[('challenge/assets',b'file'),('challenge/assets/a',b'child')])
        self.assertEqual(verify_package(path)['status'],'RECHAZADO')

    def test_file_count_and_decompression_limits(self):
        path=self.archive(extra=[('challenge/assets/large.bin',b'0'*4096)])
        self.assertEqual(verify_package(path,max_files=2)['status'],'RECHAZADO')
        self.assertEqual(verify_package(path,max_bytes=100)['status'],'RECHAZADO')

    def test_crc_corruption_detected(self):
        path=self.archive({'challenge/generate.py':b'UNIQUE_TEST_PAYLOAD'})
        data=path.read_bytes()
        self.assertEqual(data.count(b'UNIQUE_TEST_PAYLOAD'),1)
        path.write_bytes(data.replace(b'UNIQUE_TEST_PAYLOAD',b'BROKEN_TEST_PAYLOAD'))
        self.assertEqual(verify_package(path)['status'],'RECHAZADO')

    def test_rewritten_zip_detected_with_external_sha256(self):
        original=file_hash(self.archive())
        path=self.archive({'challenge/generate.py':b'pass # changed with valid CRC\n'})
        self.assertEqual(verify_package(path)['status'],'VERIFICADO')
        self.assertEqual(verify_package(path,original)['status'],'RECHAZADO')

    def test_unlisted_files_and_caches_rejected(self):
        for name in ('challenge/secret.txt','challenge/.env','challenge/assets/.git/config'):
            with self.subTest(name=name):
                self.assertEqual(verify_package(self.archive(extra=[(name,b'x')]))['status'],'RECHAZADO')

    def test_requirements_options_rejected(self):
        path=self.archive({'challenge/requirements.txt':b'--index-url https://example.invalid\n',
                           'challenge/challenge.json':self.spec_bytes(requirements=['requirements.txt'])})
        self.assertEqual(verify_package(path)['status'],'RECHAZADO')

    def test_declared_exclusion_no_longer_silently_omitted(self):
        source=self.root/'source'
        shutil.copytree(ROOT/'examples/forensics',source)
        (source/'.venv').mkdir()
        (source/'.venv/important.bin').write_bytes(b'important')
        spec=dict(self.spec,source_paths=['.venv/important.bin'])
        with self.assertRaises(ContractError):
            source_files(source,spec)

    def test_source_validation_rejects_missing_resource(self):
        source=self.root/'source'
        shutil.copytree(ROOT/'examples/forensics',source)
        (source/'challenge.json').write_bytes(self.spec_bytes(source_paths=['missing.bin']))
        self.assertEqual(validate(source)['status'],'RECHAZADO')

    def test_manual_service_package_includes_cleanup(self):
        path=self.root/'manual.zip'
        report=package_challenge(ROOT/'templates/service',path,allow_manual=True)
        self.assertEqual(report['status'],'REVISIÓN MANUAL')
        self.assertEqual(verify_package(path)['status'],'VERIFICADO')
        with zipfile.ZipFile(path) as z:
            self.assertIn('challenge/cleanup.py',z.namelist())

    def test_cli_verifier_exit_codes(self):
        path=self.archive()
        for expected,extra in ((0,[]),(1,['--sha256','0'*64])):
            result=subprocess.run([sys.executable,str(ROOT/'tools/verify_package.py'),str(path),'--json',*extra],
                                  capture_output=True,text=True,encoding='utf-8',timeout=30)
            self.assertEqual(result.returncode,expected,result.stdout+result.stderr)


if __name__ == '__main__':
    unittest.main()

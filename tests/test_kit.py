import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from ctf_author.runtime import ContractError, parse_context, safe_name, file_hash
from ctf_author.runner import Runner
from ctf_author.validation import validate, schema_check, check_outputs

ROOT = Path(__file__).resolve().parents[1]


class KitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.work = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def clone(self):
        target = self.work/'challenge'
        shutil.copytree(ROOT/'examples/forensics', target)
        return target

    def edit_spec(self, source, transform):
        spec = json.loads((source/'challenge.json').read_text(encoding='utf-8'))
        transform(spec)
        (source/'challenge.json').write_text(json.dumps(spec), encoding='utf-8')

    def test_three_real_examples(self):
        for category in ('forensics', 'cryptography', 'reverse'):
            with self.subTest(category=category):
                result = validate(ROOT/'examples'/category, Runner('local'), bundle=self.work/category)
                self.assertEqual(result['status'], 'APROBADO', result)
                self.assertTrue((self.work/category/'private/answer.json').is_file())
                self.assertFalse((self.work/category/'public/answer.json').exists())

    def test_no_execution_by_default(self):
        report = validate(ROOT/'examples/forensics')
        self.assertEqual(report['status'], 'REVISIÓN MANUAL')

    def test_unverified_services_and_mobile_are_manual(self):
        for category in ('mobile','web','blockchain'):
            self.assertEqual(validate(ROOT/'examples'/category, Runner('local'))['status'], 'REVISIÓN MANUAL')

    def test_empty_template_cannot_pass(self):
        source = self.work/'source'
        shutil.copytree(ROOT/'templates/artifact-generated', source)
        self.edit_spec(source, lambda s: s.update(readiness='ready'))
        self.assertEqual(validate(source, Runner('local'))['status'], 'RECHAZADO')

    def test_unknown_category_and_extra_fields_rejected(self):
        source = self.clone()
        self.edit_spec(source, lambda s: s.update(category='anything', user_id='123'))
        self.assertEqual(validate(source)['status'], 'RECHAZADO')

    def test_v1_request_rejected(self):
        with self.assertRaises(ContractError):
            parse_context({'schema_version': 1, 'flag': 'CTF{abc}'})

    def test_overlapping_directories_rejected(self):
        public = self.work/'public'
        public.mkdir()
        req = dict(schema_version=2, challenge_id='a', challenge_version=1, seed='s', output_dir=str(public), private_dir=str(public))
        with self.assertRaises(ContractError):
            parse_context(req)
        req['flag'] = 'not-allowed'
        with self.assertRaises(ContractError):
            parse_context(req)

    def test_portable_names(self):
        for name in ('../file', 'a/b', 'a\\b', 'CON.txt', 'answer.json', 'x.', '/etc/passwd'):
            with self.subTest(name=name), self.assertRaises(ContractError):
                safe_name(name)

    def test_nonreproducible_rejected(self):
        source = self.clone()
        script = source/'generate.py'
        script.write_text(script.read_text().replace("answer = 'archivo_recuperado'", "import secrets\n    answer = secrets.token_hex(16)"))
        self.assertEqual(validate(source, Runner('local'))['status'], 'RECHAZADO')

    def test_individual_flag_rejected(self):
        source = self.clone()
        script = source/'generate.py'
        script.write_text(script.read_text().replace('archivo_recuperado', 'CTF{abc123}'))
        report = validate(source, Runner('local'))
        self.assertEqual(report['status'], 'RECHAZADO')
        self.assertNotIn('abc123', json.dumps(report))

    def test_generator_error_does_not_leak(self):
        source = self.clone()
        (source/'generate.py').write_text('raise RuntimeError("TOP_SECRET_TEST")')
        report = validate(source, Runner('local'))
        self.assertEqual(report['status'], 'RECHAZADO')
        self.assertNotIn('TOP_SECRET_TEST', json.dumps(report))

    def test_static_artifact_without_generator(self):
        source = self.clone()
        bundle = self.work/'prepared'
        self.assertEqual(validate(source, Runner('local'), bundle=bundle)['status'], 'APROBADO')
        shutil.copytree(bundle/'public', source/'public')
        shutil.copytree(bundle/'private', source/'private')
        (source/'generate.py').unlink()
        self.edit_spec(source, lambda s: s['delivery'].update(build='static'))
        self.assertEqual(validate(source, Runner('local'))['status'], 'APROBADO')
        (source/'public/extra.txt').write_text('undeclared')
        self.assertEqual(validate(source, Runner('local'))['status'], 'RECHAZADO')

    def test_output_checksum_tampering(self):
        bundle = self.work/'prepared'
        validate(ROOT/'examples/forensics', Runner('local'), bundle=bundle)
        manifest = json.loads((bundle/'manifest.json').read_text())
        spec = json.loads((bundle/'challenge.json').read_text())
        manifest['files'][0]['sha256'] = '0'*64
        with self.assertRaises(ContractError):
            check_outputs(bundle/'public', bundle/'private', manifest, spec)

    def test_missing_solution_rejected(self):
        source = self.clone()
        (source/'SOLUCION_PRIVADA.md').unlink()
        self.assertEqual(validate(source)['status'], 'RECHAZADO')

    def test_private_material_inside_archive_rejected(self):
        source = self.clone()
        script = source/'generate.py'
        script.write_text(script.read_text().replace("'nota.txt'", "'answer.json'"))
        self.assertEqual(validate(source, Runner('local'))['status'], 'RECHAZADO')

    def test_author_test_must_run(self):
        source = self.clone()
        (source/'test_generate.py').write_text('raise RuntimeError("failing solver")')
        self.assertEqual(validate(source, Runner('local'))['status'], 'RECHAZADO')


if __name__ == '__main__':
    unittest.main()

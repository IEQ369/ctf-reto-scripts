import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from ctf_author.environments import prepare_environment, checked_python
from ctf_author.runner import Runner
from ctf_author.runtime import ContractError
from ctf_author.validation import validate

ROOT = Path(__file__).resolve().parents[1]


def teaching_wheel(destination, version):
    """Dependencia de prueba local: dos versiones incompatibles, sin red ni builds."""
    info = f'audit_dependency-{version}.dist-info'
    files = {
        'audit_dependency/__init__.py': f'VERSION = {version!r}\n'.encode(),
        f'{info}/METADATA': f'Metadata-Version: 2.1\nName: audit-dependency\nVersion: {version}\n'.encode(),
        f'{info}/WHEEL': b'Wheel-Version: 1.0\nGenerator: ctf-test\nRoot-Is-Purelib: true\nTag: py3-none-any\n'
    }
    records = []
    for name, data in files.items():
        digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b'=').decode()
        records.append(f'{name},sha256={digest},{len(data)}')
    records.append(f'{info}/RECORD,,')
    files[f'{info}/RECORD'] = ('\n'.join(records)+'\n').encode()
    with zipfile.ZipFile(destination/f'audit_dependency-{version}-py3-none-any.whl', 'w') as archive:
        for name, data in files.items():
            archive.writestr(name, data)


class EnvironmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='ctf-env-tests-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        cls.wheels = cls.root/'wheels'
        cls.wheels.mkdir()
        cls.sources, cls.envs = [], []
        for index, version in enumerate(('1.0.0', '2.0.0')):
            teaching_wheel(cls.wheels, version)
            source, env = cls.root/f'challenge-{index}', cls.root/f'env-{index}'
            shutil.copytree(ROOT/'examples/forensics', source)
            spec = json.loads((source/'challenge.json').read_text(encoding='utf-8'))
            spec.update(id=f'environment-{index}', requirements=['requirements.txt: dependencia de prueba local'])
            (source/'challenge.json').write_text(json.dumps(spec), encoding='utf-8')
            (source/'requirements.txt').write_text(f'audit-dependency=={version}\n', encoding='utf-8')
            (source/'environment.json').write_text(json.dumps({'python': f'{sys.version_info.major}.{sys.version_info.minor}', 'system_requirements': [], 'setup_notes': 'Solo fixture sintético'}), encoding='utf-8')
            for script in ('generate.py', 'test_generate.py'):
                p = source/script
                p.write_text(f'import audit_dependency\nassert audit_dependency.VERSION == {version!r}\n'+p.read_text(encoding='utf-8'), encoding='utf-8')
            prepare_environment(source, env, trusted=True, wheelhouse=cls.wheels, no_index=True)
            cls.sources.append(source)
            cls.envs.append(env)

    def test_two_conflicting_dependencies_resolve_in_separate_environments(self):
        for source, env in zip(self.sources, self.envs):
            with self.subTest(source=source.name):
                report = validate(source, Runner('local', environment=env))
                self.assertEqual(report['status'], 'APROBADO', report)
        self.assertIsNone(importlib.util.find_spec('audit_dependency'))

    def test_wrong_environment_rejected(self):
        with self.assertRaises(ContractError):
            checked_python(self.envs[0], self.sources[1])

    def test_changed_requirements_invalidate_environment(self):
        path = self.sources[0]/'requirements.txt'
        original = path.read_bytes()
        try:
            path.write_bytes(original+b'# changed\n')
            with self.assertRaises(ContractError):
                checked_python(self.envs[0], self.sources[0])
        finally:
            path.write_bytes(original)

    def test_no_install_without_trust_and_no_overwrite(self):
        with self.assertRaises(ContractError):
            prepare_environment(self.sources[0], self.root/'untrusted')
        self.assertFalse((self.root/'untrusted').exists())
        with self.assertRaises(ContractError):
            prepare_environment(self.sources[0], self.envs[0], trusted=True)

    def test_python_mismatch_prevents_creation(self):
        path = self.sources[0]/'environment.json'
        original = path.read_bytes()
        try:
            path.write_text(json.dumps({'python': '3.99', 'system_requirements': [], 'setup_notes': ''}), encoding='utf-8')
            with self.assertRaises(ContractError):
                prepare_environment(self.sources[0], self.root/'wrong-python', trusted=True)
            self.assertFalse((self.root/'wrong-python').exists())
        finally:
            path.write_bytes(original)

    def test_cli_uses_requested_environment(self):
        result = subprocess.run([sys.executable, str(ROOT/'tools/validate_challenge.py'),
            str(self.sources[1]), '--trusted-local', '--environment', str(self.envs[1]), '--json'],
            cwd=ROOT, capture_output=True, text=True, encoding='utf-8', timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'APROBADO')

    def test_environment_requires_local_mode(self):
        with self.assertRaises(ContractError):
            Runner(environment=self.envs[0])


if __name__ == '__main__':
    unittest.main()

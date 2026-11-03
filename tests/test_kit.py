import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from ctf_author.runtime import ContractError, parse_context, safe_name, decode_json
from ctf_author.runner import Runner
from ctf_author.validation import validate, read_spec, build_once, verify_instance, resolve_instance, check_outputs, schema_check
from ctf_author.packaging import package_challenge

ROOT = Path(__file__).resolve().parents[1]
LOCAL = Runner('local')


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

    def edit_spec(self, source, **updates):
        spec = json.loads((source/'challenge.json').read_text(encoding='utf-8'))
        spec.update(updates)
        (source/'challenge.json').write_text(json.dumps(spec), encoding='utf-8')

    def mutate(self, source, old, new):
        script = source/'generate.py'
        data = script.read_text(encoding='utf-8')
        self.assertIn(old, data)
        script.write_text(data.replace(old, new), encoding='utf-8')

    def build(self, flag='CTF{A123}', name='instance', source=None):
        source = source or ROOT/'examples/forensics'
        spec = read_spec(source)
        req, manifest = build_once(source, spec, LOCAL, self.work/name, 'same-seed', flag)
        return source, spec, req, manifest

    def cli(self, script, *args):
        env = dict(os.environ, PYTHONIOENCODING='utf-8')
        return subprocess.run([sys.executable, str(ROOT/'tools'/script), *map(str,args)], cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8', timeout=60)

    def test_three_examples_resolve_two_flags_and_repeat(self):
        for category in ('forensics','cryptography','reverse'):
            with self.subTest(category=category):
                report = validate(ROOT/'examples'/category, LOCAL)
                self.assertEqual(report['status'], 'APROBADO', report)

    def test_two_instances_contain_only_respective_flags(self):
        first = self.build()
        second = self.build('CTF{B987}', 'other')
        for built, expected, foreign in ((first,'CTF{A123}','CTF{B987}'),(second,'CTF{B987}','CTF{A123}')):
            source,spec,request,manifest = built
            recovered = resolve_instance(source,spec,LOCAL,request,manifest)
            self.assertEqual(recovered,expected)
            with zipfile.ZipFile(Path(request['output_dir'])/'evidencia.zip') as archive:
                self.assertEqual(archive.comment.decode(),expected)
                self.assertNotIn(foreign.encode(),archive.comment)
            self.assertNotIn(expected,json.dumps(manifest))
            self.assertEqual({p.name for p in Path(request['output_dir']).iterdir()},{'evidencia.zip'})

    def test_reproducible_bytes(self):
        first = self.build()
        repeat = self.build(name='repeat')
        self.assertEqual(first[3],repeat[3])
        self.assertEqual((self.work/'instance/evidencia.zip').read_bytes(),(self.work/'repeat/evidencia.zip').read_bytes())

    def test_foreign_flag_is_rejected(self):
        source,spec,request,manifest = self.build()
        with self.assertRaises(ContractError):
            verify_instance(source,spec,LOCAL,request,manifest,'CTF{OTHER}')

    def test_solver_cannot_read_expected_flag(self):
        source = self.clone()
        (source/'test_generate.py').write_text("import json,sys\nr=json.load(sys.stdin)\nprint(json.dumps({'schema_version':3,'recovered_flag':r['flag']}))",encoding='utf-8')
        self.assertEqual(validate(source,LOCAL)['status'],'RECHAZADO')

    def test_generator_ignoring_flag_rejected(self):
        source = self.clone()
        self.mutate(source,'answer = contexto.flag',"answer = 'CTF{FIXED}'")
        self.assertEqual(validate(source,LOCAL)['status'],'RECHAZADO')

    def test_wrong_solver_rejected(self):
        source = self.clone()
        (source/'test_generate.py').write_text("print('{\"schema_version\":3,\"recovered_flag\":\"CTF{WRONG}\"}')",encoding='utf-8')
        self.assertEqual(validate(source,LOCAL)['status'],'RECHAZADO')

    def test_nondeterministic_generator_rejected(self):
        source = self.clone()
        self.mutate(source,"archive.comment = answer.encode('ascii')", "import secrets\n        archive.comment = answer.encode('ascii') + secrets.token_bytes(16)")
        self.assertEqual(validate(source,LOCAL)['status'],'RECHAZADO')

    def test_reproducibility_exception_never_auto_approved(self):
        source=self.clone()
        self.edit_spec(source,reproducible=False,reproducibility_notes='Requiere entorno externo')
        self.assertEqual(validate(source,LOCAL)['status'],'REVISIÓN MANUAL')

    def test_private_filename_in_archive_rejected(self):
        source=self.clone()
        self.mutate(source,"'nota.txt'","'WRITEUP_PRIVADO.md'")
        self.assertEqual(validate(source,LOCAL)['status'],'RECHAZADO')

    def test_undeclared_output_rejected(self):
        source=self.clone()
        self.mutate(source,"return ['evidencia.zip']", "(contexto.output_dir/'extra.txt').write_text('private')\n    return ['evidencia.zip']")
        self.assertEqual(validate(source,LOCAL)['status'],'RECHAZADO')

    def test_hash_tampering_rejected(self):
        source,spec,request,manifest=self.build()
        manifest['files'][0]['sha256']='0'*64
        with self.assertRaises(ContractError):
            check_outputs(Path(request['output_dir']),manifest,spec)

    def test_wrong_challenge_identity_rejected(self):
        source,spec,request,manifest=self.build()
        manifest['challenge_id']='another'
        with self.assertRaises(ContractError):
            check_outputs(Path(request['output_dir']),manifest,spec)

    def test_solver_modifying_artifacts_rejected(self):
        source=self.clone()
        p=source/'test_generate.py'
        p.write_text(p.read_text(encoding='utf-8')+"\n(public/'evidencia.zip').write_bytes(b'changed')\n",encoding='utf-8')
        self.assertEqual(validate(source,LOCAL)['status'],'RECHAZADO')

    def test_error_does_not_leak(self):
        source=self.clone()
        (source/'generate.py').write_text("raise RuntimeError('TOP_SECRET_TEST')",encoding='utf-8')
        report=validate(source,LOCAL)
        self.assertEqual(report['status'],'RECHAZADO')
        self.assertNotIn('TOP_SECRET_TEST',json.dumps(report))

    def test_no_execution_by_default(self):
        self.assertEqual(validate(ROOT/'examples/forensics')['status'],'REVISIÓN MANUAL')

    def test_special_categories_are_manual(self):
        for category in ('mobile','web','blockchain'):
            self.assertEqual(validate(ROOT/'examples'/category,LOCAL)['status'],'REVISIÓN MANUAL')

    def test_shared_service_rejected(self):
        source=self.work/'service'
        shutil.copytree(ROOT/'templates/service',source)
        spec=json.loads((source/'challenge.json').read_text(encoding='utf-8'))
        spec['delivery']['service']['isolation']='shared-readonly'
        self.edit_spec(source,delivery=spec['delivery'])
        self.assertEqual(validate(source)['status'],'RECHAZADO')

    def test_template_cannot_pass_unimplemented(self):
        source=self.work/'template'
        shutil.copytree(ROOT/'templates/artifact-generated',source)
        self.edit_spec(source,readiness='ready')
        self.assertEqual(validate(source,LOCAL)['status'],'RECHAZADO')

    def test_missing_writeup_rejected(self):
        source=self.clone()
        (source/'WRITEUP_PRIVADO.md').unlink()
        self.assertEqual(validate(source)['status'],'RECHAZADO')

    def test_unknown_category_rejected(self):
        source=self.clone()
        self.edit_spec(source,category='osint')
        self.assertEqual(validate(source)['status'],'RECHAZADO')

    def test_request_contract_rejects_v2_identity_and_invalid_flags(self):
        output=self.work/'output'; output.mkdir()
        valid=dict(schema_version=3,challenge_id='one',challenge_version=1,flag='CTF{A123}',seed='seed',output_dir=str(output),parameters={})
        schema_check(valid,'generation-request')
        self.assertEqual(parse_context(valid).flag,'CTF{A123}')
        for updates in ({'schema_version':2},{'user_id':'alice'},{'flag':''},{'flag':'line\nbreak'},{'flag':42},{'challenge_version':True},{'private_dir':str(output)}):
            with self.subTest(updates=updates),self.assertRaises((ContractError,ValueError)):
                parse_context(dict(valid,**updates))

    def test_rng_has_state(self):
        output=self.work/'output'; output.mkdir()
        req=dict(schema_version=3,challenge_id='one',challenge_version=1,flag='CTF{A}',seed='seed',output_dir=str(output),parameters={})
        first=parse_context(req); second=parse_context(req)
        values=[first.rng.random(),first.rng.random()]
        self.assertNotEqual(values[0],values[1])
        self.assertEqual(values,[second.rng.random(),second.rng.random()])

    def test_json_duplicate_keys_and_nan_rejected(self):
        for payload in ('{"flag":"first","flag":"second"}', '{"value": NaN}'):
            with self.assertRaises(ContractError):
                decode_json(payload)

    def test_cli_parameters_and_private_flag_file(self):
        source=self.clone()
        self.mutate(source, 'answer = contexto.flag', "assert contexto.parameters['mode'] == 'demo'\n    answer = contexto.flag")
        params=self.work/'parameters.json'
        params.write_text('{"mode":"demo"}',encoding='utf-8')
        flagfile=self.work/'flag.txt'
        flagfile.write_text('CTF{FILE_INPUT}\n',encoding='utf-8')
        p=self.cli('generate_instance.py',source,'--flag-file',flagfile,'--parameters',params,
                   '--output',self.work/'fromfile','--trusted-local')
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        self.assertNotIn('CTF{FILE_INPUT}',p.stdout+p.stderr)
        p=self.cli('validate_challenge.py',source,'--parameters',params,'--trusted-local')
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)

    def test_no_overwrite(self):
        self.build()
        with self.assertRaises(ContractError):
            self.build('CTF{B987}')

    def test_portable_private_names(self):
        for name in ('../x','a/b','CON.txt','WRITEUP_PRIVADO.md','answer.json','test_generate.py','x.'):
            with self.subTest(name=name),self.assertRaises(ContractError): safe_name(name)

    def test_source_package_roundtrip_and_public_separation(self):
        source=self.clone()
        (source/'.env').write_text('LOCAL_SECRET',encoding='utf-8')
        (source/'unlisted.txt').write_text('not included',encoding='utf-8')
        destination=self.work/'delivery.zip'
        report=package_challenge(source,destination,LOCAL)
        self.assertEqual(report['status'],'APROBADO')
        with zipfile.ZipFile(destination) as archive:
            names=archive.namelist()
            self.assertIn('challenge/WRITEUP_PRIVADO.md',names)
            self.assertNotIn('challenge/.env',names)
            self.assertNotIn('challenge/unlisted.txt',names)
            archive.extractall(self.work/'unpacked')
        self.assertEqual(validate(self.work/'unpacked/challenge',LOCAL)['status'],'APROBADO')

    def test_package_refuses_traversal_source(self):
        source=self.clone()
        self.edit_spec(source,source_paths=['../outside'])
        with self.assertRaises(ContractError): package_challenge(source,self.work/'delivery.zip',LOCAL)

    def test_packaging_preserves_declared_forensic_and_crypto_assets(self):
        source=self.clone()
        assets=source/'assets'
        assets.mkdir()
        names=('evidence.db','events.log','sample.pyc','synthetic.key')
        for name in names:
            (assets/name).write_bytes(b'synthetic teaching fixture')
        destination=self.work/'with-assets.zip'
        package_challenge(source,destination,LOCAL)
        with zipfile.ZipFile(destination) as archive:
            for name in names:
                self.assertEqual(archive.read('challenge/assets/'+name),b'synthetic teaching fixture')

    def test_direct_protocol_success_and_redacted_error(self):
        source,spec,request,manifest=self.build()
        output=self.work/'direct'; output.mkdir(); request['output_dir']=str(output)
        proc=subprocess.run([sys.executable,str(source/'generate.py')],input=json.dumps(request),capture_output=True,text=True,encoding='utf-8',cwd=source)
        self.assertEqual(proc.returncode,0,proc.stderr)
        schema_check(json.loads(proc.stdout),'generation-result')
        self.assertNotIn(request['flag'],proc.stdout+proc.stderr)
        request['user_id']='NO_ID_ALLOWED'
        proc=subprocess.run([sys.executable,str(source/'generate.py')],input=json.dumps(request),capture_output=True,text=True,encoding='utf-8',cwd=source)
        self.assertNotEqual(proc.returncode,0)
        schema_check(json.loads(proc.stdout),'generation-error')
        self.assertNotIn('NO_ID_ALLOWED',proc.stdout+proc.stderr)

    def test_cli_create_generate_validate_package(self):
        created=self.work/'new-challenge'
        p=self.cli('create_challenge.py',created,'--id','new-forensic','--category','forensics')
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertTrue((created/'generate.py').is_file())
        source=ROOT/'examples/forensics'
        for flag,name in [('CTF{A123}','a'),('CTF{B987}','b')]:
            p=self.cli('generate_instance.py',source,'--flag',flag,'--output',self.work/name,'--trusted-local')
            self.assertEqual(p.returncode,0,p.stdout+p.stderr)
            schema_check(json.loads(p.stdout),'generation-result')
        p=self.cli('validate_challenge.py',source,'--trusted-local','--json')
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        p=self.cli('package_challenge.py',source,'--output',self.work/'cli.zip','--trusted-local')
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)

    def test_service_descriptor_schema_and_no_fake_success(self):
        schema_check(dict(schema_version=3,status='ok',kind='service',challenge_id='web-01',challenge_version=1,service={'endpoint':'http://127.0.0.1:8080','instance_ref':'opaque-123'}),'service-result')
        source=ROOT/'templates/service'
        output=self.work/'service'; output.mkdir()
        req=dict(schema_version=3,challenge_id='service-01',challenge_version=1,flag='CTF{A123}',seed='s',output_dir=str(output),parameters={})
        proc=subprocess.run([sys.executable,str(source/'generate.py')],input=json.dumps(req),capture_output=True,text=True,encoding='utf-8',cwd=source)
        self.assertNotEqual(proc.returncode,0)
        self.assertEqual(json.loads(proc.stdout)['status'],'error')


if __name__ == '__main__':
    unittest.main()

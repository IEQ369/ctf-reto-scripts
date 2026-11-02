"""Validación y preparación offline. Nunca llamar desde rutas de participantes."""
import json
from pathlib import Path
import re
import shutil
import tempfile
import urllib.request
import zipfile
from jsonschema import Draft202012Validator, FormatChecker
from .runtime import ContractError, load_json, safe_name, file_hash, manifest_for, normalize
from .runner import Runner


def schema_check(value, name):
    schema = load_json(Path(__file__).parent / 'schemas' / (name + '.schema.json'))
    errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value))
    if errors:
        # Solo posición de campos, nunca valores privados ni mensajes del proveedor.
        location = '/'.join(str(x) for x in errors[0].absolute_path) or '(raíz)'
        raise ContractError(f'Esquema {name} inválido en {location}')


def check_tree(root):
    root = Path(root)
    if root.is_symlink():
        raise ContractError('No se permiten enlaces')
    for path in root.rglob('*'):
        if path.is_symlink() or getattr(path, 'is_junction', lambda: False)():
            raise ContractError('No se permiten enlaces ni junctions')
        if not path.is_dir() and not path.is_file():
            raise ContractError('Tipo especial de archivo no permitido')


def inspect_public(path, budget):
    # Heurística defensiva, no demuestra ausencia de secretos ofuscados.
    def scan(data):
        if re.search(rb'CTF\{[^}\r\n]{1,256}\}', data):
            raise ContractError('Posible flag individual en material compartido')
    scan(path.read_bytes())
    if path.suffix.lower() in ('.zip', '.apk'):
        try:
            with zipfile.ZipFile(path) as archive:
                if len(archive.infolist()) > 1000 or sum(i.file_size for i in archive.infolist()) > budget:
                    raise ContractError('Archivo comprimido excede límites de inspección')
                for item in archive.infolist():
                    if item.filename.startswith(('/', '\\')) or '..' in item.filename.replace('\\', '/').split('/'):
                        raise ContractError('Ruta peligrosa dentro del archivo comprimido')
                    if Path(item.filename).name.lower() in ('answer.json', 'solucion_privada.md'):
                        raise ContractError('Material privado dentro del archivo comprimido')
                    if (item.external_attr >> 16) & 0o170000 == 0o120000:
                        raise ContractError('Enlace dentro del archivo comprimido')
                    scan(archive.read(item))
        except (zipfile.BadZipFile, RuntimeError):
            raise ContractError('ZIP/APK inválido o cifrado; necesita revisión especializada') from None


def check_outputs(public, private, manifest, spec):
    check_tree(public)
    check_tree(private)
    schema_check(manifest, 'generation-result')
    names = [safe_name(f['name']) for f in manifest['files']]
    if len({n.casefold() for n in names}) != len(names):
        raise ContractError('Nombres públicos duplicados')
    if set(names) != set(spec['public_files']) or {p.name for p in public.iterdir()} != set(names):
        raise ContractError('Archivos públicos no declarados o faltantes')
    limits = spec['limits']
    if len(names) > limits['max_files'] or sum(p.stat().st_size for p in public.iterdir()) > limits['max_bytes']:
        raise ContractError('Límites de archivos o almacenamiento excedidos')
    for record in manifest['files']:
        path = public / record['name']
        if not path.is_file() or path.stat().st_nlink > 1:
            raise ContractError('Salida no regular o hardlink')
        if path.stat().st_size != record['size'] or file_hash(path) != record['sha256']:
            raise ContractError('Tamaño o SHA-256 incorrecto')
        inspect_public(path, limits['max_bytes'])
    if {p.name for p in private.iterdir()} != {'answer.json'}:
        raise ContractError('La salida privada debe contener exclusivamente answer.json')
    if (private / 'answer.json').stat().st_size > 16384:
        raise ContractError('Respuesta privada demasiado grande')
    answer = load_json(private / 'answer.json')
    schema_check(answer, 'answer')
    if not normalize(answer['answer'], answer['comparison']):
        raise ContractError('Respuesta vacía después de normalizar')
    if 'CTF{' in answer['answer']:
        raise ContractError('La respuesta común no debe usar el formato de flags personales')
    return answer


def read_spec(source):
    source = Path(source).resolve()
    check_tree(source)
    for name in ('challenge.json', 'README.md', 'SOLUCION_PRIVADA.md'):
        if not (source / name).is_file() or not (source / name).stat().st_size:
            raise ContractError('Falta archivo obligatorio: ' + name)
    spec = load_json(source / 'challenge.json')
    schema_check(spec, 'challenge')
    for name in spec['public_files']:
        safe_name(name)
    deps = source / 'requirements.txt'
    if deps.exists():
        if not any('requirements.txt' in entry for entry in spec['requirements']):
            raise ContractError('Documentar requirements.txt en requirements')
        for line in deps.read_text(encoding='utf-8').splitlines():
            if line.strip() and not line.startswith('#') and not re.fullmatch(r'[A-Za-z0-9_.-]+==[A-Za-z0-9_.+-]+', line):
                raise ContractError('Dependencias deben fijar versión exacta; instalación siempre externa')
    return spec


def build_once(source, spec, runner, destination, seed):
    public, private = destination / 'public', destination / 'private'
    public.mkdir(parents=True)
    private.mkdir()
    # Contenedor no-root necesita escribir en directorios de trabajo dedicados.
    if runner.mode == 'docker':
        public.chmod(0o777)
        private.chmod(0o777)
    request = {'schema_version': 2, 'challenge_id': spec['id'], 'challenge_version': spec['version'],
               'seed': seed, 'output_dir': str(public.resolve()), 'private_dir': str(private.resolve())}
    if spec['delivery']['build'] == 'static':
        static = source / 'public'
        if not static.is_dir() or {p.name for p in static.iterdir()} != set(spec['public_files']):
            raise ContractError('Entrega estática contiene archivos no declarados o faltantes')
        for name in spec['public_files']:
            shutil.copyfile(static / name, public / name)
        shutil.copyfile(source / 'private' / 'answer.json', private / 'answer.json')
        manifest = manifest_for(public, spec['public_files'])
    else:
        if not (source / 'generate.py').is_file():
            raise ContractError('Falta generate.py')
        manifest = json.loads(runner.execute(source, 'generate.py', request, spec['limits']))
    answer = check_outputs(public, private, manifest, spec)
    return request, manifest, answer


def validate(source, runner=None, seed='ctf-preparation-v2', bundle=None, check_service=False):
    runner = runner or Runner()
    report = {'status': 'RECHAZADO', 'errors': [], 'warnings': [], 'checks': []}
    try:
        source = Path(source).resolve()
        spec = read_spec(source)
        report['checks'].append('Estructura, metadatos, categorías y esquema v2')
        if spec['readiness'] != 'ready':
            report['status'] = 'REVISIÓN MANUAL'
            report['warnings'].append('Autor declara infraestructura o compilación pendiente')
            return report
        if spec['delivery']['kind'] == 'service':
            service = spec['delivery']['service']
            if service['state'] == 'mutable' and service['isolation'] == 'shared-readonly':
                raise ContractError('Estado mutable incompatible con aislamiento declarado')
            report['status'] = 'REVISIÓN MANUAL'
            report['warnings'].append('Servicio requiere comprobación funcional y revisión de aislamiento por su responsable')
            if check_service:
                # Solo por acción administrativa explícita; nunca al importar metadatos desde HTTP.
                with urllib.request.urlopen(service['health_url'], timeout=5) as response:
                    if response.status != 200:
                        raise ContractError('Comprobación de salud fallida')
                report['checks'].append('Salud HTTP 200 comprobada; no equivale a solución funcional')
            return report
        if not (source / 'test_generate.py').is_file():
            raise ContractError('Falta test_generate.py')
        if runner.mode == 'none':
            report['status'] = 'REVISIÓN MANUAL'
            report['warnings'].append('No se ejecutó código del autor. Elegir sandbox o --trusted-local tras revisión')
            return report
        if runner.mode == 'local':
            report['warnings'].append('Código confiable ejecutado localmente: sin aislamiento ni cuotas duras de memoria/disco')
        else:
            report['warnings'].append('Docker limita memoria/CPU/procesos; configurar cuota de disco del trabajador')
        with tempfile.TemporaryDirectory(prefix='ctf-author-') as folder:
            root = Path(folder)
            first = build_once(source, spec, runner, root / 'first', seed)
            second = build_once(source, spec, runner, root / 'second', seed)
            if first[1:] != second[1:]:
                raise ContractError('Generación no reproducible')
            # Comprobar también bytes privados: formatos o timestamps variables cuentan.
            if (root / 'first/private/answer.json').read_bytes() != (root / 'second/private/answer.json').read_bytes():
                raise ContractError('Respuesta privada no reproducible')
            report['checks'].extend(['Manifiesto, checksums, rutas y separación público/privado',
                                     'Reproducibilidad y respuesta común válida', 'Inspección heurística de flags'])
            before = first[1]
            result = json.loads(runner.execute(source, 'test_generate.py', first[0], spec['limits']))
            if set(result) != {'tests_passed'} or type(result['tests_passed']) is not int or result['tests_passed'] < 1:
                raise ContractError('La prueba del autor debe declarar tests_passed positivo')
            check_outputs(root / 'first/public', root / 'first/private', before, spec)
            if load_json(root / 'first/private/answer.json') != first[2]:
                raise ContractError('La prueba modificó la respuesta privada')
            report['checks'].append('Prueba de resolución del autor ejecutada')
            report['status'] = 'APROBADO'
            if bundle:
                destination = Path(bundle).resolve()
                if destination.exists():
                    raise ContractError('El destino del paquete preparado ya existe')
                shutil.copytree(root / 'first', destination)
                for name, data in [('challenge.json', spec), ('manifest.json', first[1]), ('validation.json', report)]:
                    (destination / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        return report
    except ContractError as error:
        report['errors'].append(str(error))
    except Exception:
        report['errors'].append('Error de estructura, ejecución o infraestructura; detalles privados suprimidos')
    report['status'] = 'RECHAZADO'
    return report

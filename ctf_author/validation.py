"""Validación y preparación offline. Nunca llamar desde rutas de participantes."""
import json
from pathlib import Path
import re
import tempfile
import zipfile
from jsonschema import Draft202012Validator, FormatChecker
from .runtime import ContractError, load_json, decode_json, safe_name, file_hash, parse_context
from .runner import Runner
from .sources import source_files, REQUIRED
from .dependencies import check_requirements


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
    if path.suffix.lower() in ('.zip', '.apk'):
        try:
            with zipfile.ZipFile(path) as archive:
                if len(archive.infolist()) > 1000 or sum(i.file_size for i in archive.infolist()) > budget:
                    raise ContractError('Archivo comprimido excede límites de inspección')
                for item in archive.infolist():
                    if item.filename.startswith(('/', '\\')) or '..' in item.filename.replace('\\', '/').split('/'):
                        raise ContractError('Ruta peligrosa dentro del archivo comprimido')
                    if Path(item.filename).name.lower() in ('answer.json', 'solucion_privada.md', 'writeup_privado.md', 'test_generate.py', 'generate.py', 'challenge.json'):
                        raise ContractError('Material privado dentro del archivo comprimido')
                    if (item.external_attr >> 16) & 0o170000 == 0o120000:
                        raise ContractError('Enlace dentro del archivo comprimido')
                    archive.read(item)  # Comprueba integridad; no busca flags, que aquí son válidas.
        except (zipfile.BadZipFile, RuntimeError):
            raise ContractError('ZIP/APK inválido o cifrado; necesita revisión especializada') from None


def check_outputs(public, manifest, spec):
    check_tree(public)
    schema_check(manifest, 'generation-result')
    if manifest['status'] != 'ok' or manifest['kind'] != 'artifact' or manifest['challenge_id'] != spec['id'] or manifest['challenge_version'] != spec['version']:
        raise ContractError('El resultado no corresponde al reto solicitado')
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


def read_spec(source):
    source = Path(source).resolve()
    check_tree(source)
    for name in REQUIRED:
        if not (source / name).is_file() or not (source / name).stat().st_size:
            raise ContractError('Falta archivo obligatorio: ' + name)
    spec = load_json(source / 'challenge.json')
    schema_check(spec, 'challenge')
    for name in spec['public_files']:
        safe_name(name)
    deps = source / 'requirements.txt'
    if deps.exists():
        check_requirements(deps.read_text(encoding='utf-8'), spec)
    if (source / 'environment.json').exists():
        schema_check(load_json(source / 'environment.json'), 'environment')
    source_files(source, spec)
    return spec


def build_once(source, spec, runner, destination, seed, flag, parameters=None):
    # Cada invocación utiliza un directorio nuevo: nunca sobrescribe otra instancia.
    destination = Path(destination).absolute()
    if destination.exists():
        raise ContractError('El destino de la instancia ya existe')
    destination.mkdir(parents=True)
    if runner.mode == 'docker':
        destination.chmod(0o777)
    request = {'schema_version': 3, 'challenge_id': spec['id'], 'challenge_version': spec['version'],
               'seed': seed, 'flag': flag, 'parameters': parameters if parameters is not None else {},
               'output_dir': str(destination)}
    parse_context(request)
    manifest = decode_json(runner.execute(source, 'generate.py', request, spec['limits']))
    check_outputs(destination, manifest, spec)
    return request, manifest


def resolve_instance(source, spec, runner, request, manifest):
    # El solucionador NO recibe la flag esperada. Debe extraerla del material público.
    solver_request = {key: value for key, value in request.items() if key != 'flag'}
    result = decode_json(runner.execute(source, 'test_generate.py', solver_request, spec['limits']))
    schema_check(result, 'resolution-result')
    check_outputs(Path(request['output_dir']), manifest, spec)
    return result['recovered_flag']


def verify_instance(source, spec, runner, request, manifest, expected):
    if resolve_instance(source, spec, runner, request, manifest) != expected:
        raise ContractError('La resolución no recuperó exactamente la flag esperada')


def validate(source, runner=None, seed='ctf-validation-v3', parameters=None):
    runner = runner or Runner()
    report = {'status': 'RECHAZADO', 'errors': [], 'warnings': [], 'checks': []}
    try:
        source = Path(source).resolve()
        spec = read_spec(source)
        report['checks'].append('Estructura y contrato v3 de un único reto')
        if spec['delivery']['kind'] == 'service':
            service = spec['delivery']['service']
            if service['isolation'] != 'per-participant':
                raise ContractError('El servicio personalizado requiere aislamiento por instancia')
            report['status'] = 'REVISIÓN MANUAL'
            report['warnings'].append('Adaptador de servicio: desplegar, resolver, verificar aislamiento y limpiar externamente; no ejecutado por este kit')
            return report
        if spec['readiness'] != 'ready':
            report['status'] = 'REVISIÓN MANUAL'
            report['warnings'].append('Implementación o infraestructura declarada pendiente')
            return report
        if runner.mode == 'none':
            report['status'] = 'REVISIÓN MANUAL'
            report['warnings'].append('Seleccionar --trusted-local para código revisado o --docker-image')
            return report
        report['warnings'].append('La prueba del autor requiere revisión humana; no certifica seguridad ni dificultad')
        if runner.mode == 'local':
            report['warnings'].append('Ejecución local sin aislamiento ni cuotas duras de memoria/disco')
        else:
            report['warnings'].append('Docker requiere imagen preparada y cuota externa de disco; no probado en la entrega')
        # Flags ficticias de prueba creadas por el validador, nunca por el generador.
        import secrets
        flags = ['CTF{test_' + secrets.token_hex(16) + '}' for _ in range(2)]
        with tempfile.TemporaryDirectory(prefix='ctf-author-') as folder:
            root = Path(folder)
            first = build_once(source, spec, runner, root/'first', seed, flags[0], parameters)
            repeat = build_once(source, spec, runner, root/'repeat', seed, flags[0], parameters)
            other = build_once(source, spec, runner, root/'other', seed, flags[1], parameters)
            if spec['reproducible'] and first[1] != repeat[1]:
                raise ContractError('Generación no reproducible con iguales entradas')
            if not spec['reproducible']:
                report['warnings'].append('Reproducibilidad exceptuada: requiere revisión manual del entorno y justificación')
            if first[1] == other[1]:
                raise ContractError('Flags distintas produjeron material idéntico')
            for request, manifest in (first, repeat, other):
                verify_instance(source, spec, runner, request, manifest, request['flag'])
            # Verificación negativa por el mismo camino usado para aceptar una instancia.
            try:
                verify_instance(source, spec, runner, first[0], first[1], flags[1])
            except ContractError:
                pass
            else:
                raise ContractError('La prueba aceptó una flag ajena')
            report['checks'].extend(['Tres ejecuciones independientes del mismo generador',
                'Dos flags ficticias distintas recuperadas desde sus respectivos archivos',
                'Repetición con iguales parámetros comprobada', 'Flag ajena rechazada',
                'Manifiesto, hashes, tamaños y separación de material privado'])
            report['status'] = 'APROBADO' if spec['reproducible'] else 'REVISIÓN MANUAL'
    except ContractError as error:
        report['errors'].append(str(error))
        report['status'] = 'RECHAZADO'
    except Exception:
        report['errors'].append('Error de estructura, ejecución o infraestructura; detalles privados suprimidos')
        report['status'] = 'RECHAZADO'
    return report

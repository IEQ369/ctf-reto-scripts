"""Infraestructura común de generadores. Solo biblioteca estándar."""
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
import random
import re
import sys


class ContractError(ValueError):
    pass


def decode_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ContractError('JSON contiene claves duplicadas')
            result[key] = value
        return result
    def invalid_constant(value):
        raise ContractError('JSON contiene un número no finito')
    return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid_constant)


def load_json(path):
    return decode_json(Path(path).read_text(encoding='utf-8'))


def safe_name(name):
    if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,99}', name):
        raise ContractError('Nombre de archivo no portable')
    if name.endswith('.') or name.split('.')[0].upper() in {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(10)), *(f'LPT{i}' for i in range(10))}:
        raise ContractError('Nombre reservado')
    if name.lower() in {'answer.json', 'solucion_privada.md', 'writeup_privado.md', 'challenge.json', 'requirements.txt', 'generate.py', 'test_generate.py'}:
        raise ContractError('Material privado o de control en salida pública')
    return name


def file_hash(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


@dataclass
class Context:
    challenge_id: str
    challenge_version: int
    seed: str
    output_dir: Path
    flag: str = field(repr=False)
    parameters: dict
    rng: random.Random = field(init=False, repr=False)

    def __post_init__(self):
        self.rng = random.Random(self.seed)


def parse_context(request):
    fields = {'schema_version', 'challenge_id', 'challenge_version', 'seed', 'output_dir', 'flag', 'parameters'}
    if not isinstance(request, dict) or set(request) != fields or type(request['schema_version']) is not int or request['schema_version'] != 3:
        raise ContractError('Entrada v3 inválida; no se permiten identidades ni campos adicionales')
    if not isinstance(request['challenge_id'], str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', request['challenge_id']):
        raise ContractError('ID inválido')
    if type(request['challenge_version']) is not int or request['challenge_version'] < 1:
        raise ContractError('Versión inválida')
    if not isinstance(request['seed'], str) or not 1 <= len(request['seed']) <= 128:
        raise ContractError('Semilla inválida')
    if not isinstance(request['flag'], str) or not re.fullmatch(r'[\x21-\x7e]{1,512}', request['flag']):
        raise ContractError('Flag inválida: usar de 1 a 512 caracteres ASCII imprimibles sin espacios')
    if not isinstance(request['parameters'], dict) or len(json.dumps(request['parameters'], allow_nan=False)) > 16384:
        raise ContractError('Parámetros inválidos o demasiado grandes')
    if not isinstance(request['output_dir'], str):
        raise ContractError('Ruta inválida')
    path = Path(request['output_dir'])
    if not path.is_absolute() or not path.is_dir() or any(path.iterdir()):
        raise ContractError('Se requiere directorio absoluto, vacío y existente')
    if any(p.is_symlink() or getattr(p, 'is_junction', lambda: False)() for p in (path, *path.parents)):
        raise ContractError('No se permiten enlaces en la ruta de salida')
    return Context(request['challenge_id'], request['challenge_version'], request['seed'], path.resolve(), request['flag'], request['parameters'])


def manifest_for(context, names):
    output = context.output_dir
    if not isinstance(names, list) or not names:
        raise ContractError('El reto no produjo archivos')
    files = []
    for name in names:
        path = output / safe_name(name)
        if path.is_symlink() or not path.is_file() or path.resolve().parent != output.resolve():
            raise ContractError('Archivo inválido')
        files.append({'name': name, 'size': path.stat().st_size, 'sha256': file_hash(path)})
    return {'schema_version': 3, 'status': 'ok', 'challenge_id': context.challenge_id,
            'challenge_version': context.challenge_version, 'kind': 'artifact',
            'files': sorted(files, key=lambda f: f['name'])}


def run(builder):
    configure_stdio()
    try:
        context = parse_context(decode_json(sys.stdin.read()))
        names = builder(context)
        manifest = manifest_for(context, names)
        if any(context.flag == item['name'] for item in manifest['files']):
            raise ContractError('No incluir la flag en nombres o metadatos públicos')
        print(json.dumps(manifest, sort_keys=True))
    except Exception:
        # No reproducir entradas, tracebacks o excepciones del autor en informes.
        print('Generación fallida: revisar implementación y prueba privada.', file=sys.stderr)
        print(json.dumps({'schema_version': 3, 'status': 'error', 'code': 'generation_failed'}))
        raise SystemExit(1)


def run_service(builder):
    """Protocolo de adaptadores externos; no despliega ni supervisa servicios."""
    configure_stdio()
    try:
        context = parse_context(decode_json(sys.stdin.read()))
        descriptor = builder(context)
        from .validation import schema_check
        result = {'schema_version': 3, 'status': 'ok', 'kind': 'service',
                  'challenge_id': context.challenge_id, 'challenge_version': context.challenge_version,
                  'service': descriptor}
        schema_check(result, 'service-result')
        if context.flag in descriptor.values() or any(context.output_dir.iterdir()):
            raise ContractError('El adaptador no debe publicar secretos ni archivos auxiliares')
        print(json.dumps(result, sort_keys=True))
    except Exception:
        print('Servicio fallido: revisar adaptador y limpieza privada.', file=sys.stderr)
        print(json.dumps({'schema_version': 3, 'status': 'error', 'code': 'generation_failed'}))
        raise SystemExit(1)


def configure_stdio():
    # El protocolo es UTF-8 también bajo PowerShell con una página de códigos distinta.
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')

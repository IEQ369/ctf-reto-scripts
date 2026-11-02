"""Infraestructura común de generadores. Solo biblioteca estándar."""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import random
import re
import sys


class ContractError(ValueError):
    pass


def load_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ContractError('JSON contiene claves duplicadas')
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=pairs)


def safe_name(name):
    if not isinstance(name, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,99}', name):
        raise ContractError('Nombre de archivo no portable')
    if name.endswith('.') or name.split('.')[0].upper() in {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(10)), *(f'LPT{i}' for i in range(10))}:
        raise ContractError('Nombre reservado')
    if name.lower() in {'answer.json', 'solucion_privada.md', 'challenge.json', 'requirements.txt'}:
        raise ContractError('Material privado o de control en salida pública')
    return name


def file_hash(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def normalize(value, rules):
    # Solo transformaciones explícitas, sin normalización Unicode implícita.
    if rules['strip']:
        value = value.strip()
    if rules['casefold']:
        value = value.casefold()
    return value


@dataclass
class Context:
    challenge_id: str
    challenge_version: int
    seed: str
    output_dir: Path
    private_dir: Path

    @property
    def rng(self):
        return random.Random(self.seed)

    def answer(self, value, *, strip=False, casefold=False):
        if not isinstance(value, str) or not 1 <= len(value) <= 512:
            raise ContractError('Respuesta común vacía o demasiado larga')
        rules = {'strip': strip, 'casefold': casefold}
        if not normalize(value, rules):
            raise ContractError('Respuesta vacía después de normalizar')
        (self.private_dir / 'answer.json').write_text(json.dumps({
            'schema_version': 2, 'answer': value, 'comparison': rules
        }, ensure_ascii=False, sort_keys=True), encoding='utf-8')


def parse_context(request):
    fields = {'schema_version', 'challenge_id', 'challenge_version', 'seed', 'output_dir', 'private_dir'}
    if not isinstance(request, dict) or set(request) != fields or request['schema_version'] != 2:
        raise ContractError('Entrada v2 inválida; no se permiten usuarios ni flags')
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', request['challenge_id']):
        raise ContractError('ID inválido')
    if type(request['challenge_version']) is not int or request['challenge_version'] < 1:
        raise ContractError('Versión inválida')
    if not isinstance(request['seed'], str) or not 1 <= len(request['seed']) <= 128:
        raise ContractError('Semilla inválida')
    paths = []
    for field in ('output_dir', 'private_dir'):
        path = Path(request[field])
        if not path.is_absolute() or path.is_symlink() or not path.is_dir() or any(path.iterdir()):
            raise ContractError('Se requieren directorios absolutos, vacíos y existentes')
        paths.append(path.resolve())
    public, private = paths
    if public == private or public in private.parents or private in public.parents:
        raise ContractError('Las rutas pública y privada deben ser independientes')
    return Context(request['challenge_id'], request['challenge_version'], request['seed'], public, private)


def manifest_for(output, names):
    if not isinstance(names, list) or not names:
        raise ContractError('El reto no produjo archivos')
    files = []
    for name in names:
        path = output / safe_name(name)
        if path.is_symlink() or not path.is_file() or path.resolve().parent != output.resolve():
            raise ContractError('Archivo inválido')
        files.append({'name': name, 'size': path.stat().st_size, 'sha256': file_hash(path)})
    return {'schema_version': 2, 'files': sorted(files, key=lambda f: f['name'])}


def run(builder):
    try:
        context = parse_context(json.load(sys.stdin))
        names = builder(context)
        if not (context.private_dir / 'answer.json').is_file():
            raise ContractError('Falta respuesta común privada')
        print(json.dumps(manifest_for(context.output_dir, names), sort_keys=True))
    except Exception:
        # No reproducir entradas, tracebacks o excepciones del autor en informes.
        print('Generación fallida: revisar implementación y prueba privada.', file=sys.stderr)
        raise SystemExit(1)

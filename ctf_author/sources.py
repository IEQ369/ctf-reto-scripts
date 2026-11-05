"""Selección común de fuentes privadas, sin importar ni ejecutar código del autor."""
from pathlib import Path, PurePosixPath
import re
import unicodedata
from .runtime import ContractError

REQUIRED = ('challenge.json', 'generate.py', 'test_generate.py', 'README.md', 'WRITEUP_PRIVADO.md')
OPTIONAL = ('assets', 'requirements.txt', 'environment.json', 'cleanup.py')
EXCLUDED = {'.git', '.codex', '.venv', 'venv', '.gradle', '__pycache__', 'node_modules'}


def portable_path(name):
    """Ruta relativa canónica válida también al extraer en Windows."""
    if not isinstance(name, str) or not name or len(name) > 240:
        raise ContractError('Ruta de fuente inválida')
    if unicodedata.normalize('NFC', name) != name or '\\' in name or ':' in name:
        raise ContractError('Ruta de fuente no portable')
    parts = name.split('/')
    for part in parts:
        if part in ('', '.', '..') or part.endswith(('.', ' ')) or re.search(r'[\x00-\x1f\x7f<>"|?*]', part):
            raise ContractError('Ruta de fuente peligrosa o ambigua')
        if part.split('.')[0].upper() in {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(10)), *(f'LPT{i}' for i in range(10))}:
            raise ContractError('Nombre de fuente reservado')
    return PurePosixPath(name)


def excluded(name):
    return any(p.casefold() in EXCLUDED or p.casefold().endswith('.egg-info') for p in PurePosixPath(name).parts)


def source_files(source, spec):
    source = Path(source).resolve()
    names = list(REQUIRED) + list(spec['source_paths'])
    names += [name for name in OPTIONAL if (source / name).exists()]
    files, cases = {}, {}
    for name in names:
        relative = portable_path(name)
        if excluded(name):
            raise ContractError('Una fuente declarada está dentro de una carpeta excluida')
        path = source.joinpath(*relative.parts)
        if not path.exists() or not path.resolve().is_relative_to(source):
            raise ContractError('Fuente declarada ausente o fuera del reto')
        if any(p.is_symlink() or getattr(p, 'is_junction', lambda: False)() for p in (path, *path.parents) if p != source.parent):
            raise ContractError('No empaquetar enlaces ni junctions')
        candidates = [path] if path.is_file() else path.rglob('*')
        found = False
        for item in candidates:
            if item.is_symlink() or getattr(item, 'is_junction', lambda: False)():
                raise ContractError('No empaquetar enlaces ni junctions')
            if not item.is_file():
                continue
            rel = item.relative_to(source).as_posix()
            if excluded(rel):
                continue
            portable_path(rel)
            if item.name.casefold().startswith('.env') and item.name != 'environment.json':
                raise ContractError('Configuración local privada en fuentes declaradas')
            if rel.casefold() in cases and cases[rel.casefold()] != rel:
                raise ContractError('Fuentes con nombres ambiguos por mayúsculas/minúsculas')
            cases[rel.casefold()] = rel
            files[rel] = item
            found = True
        if not found and name in spec['source_paths']:
            raise ContractError('Una fuente declarada no aporta archivos; revisar exclusiones o directorio vacío')
    return files

"""Entrega privada de fuentes de UN reto, no descarga para participantes."""
import json
from pathlib import Path, PurePosixPath
import zipfile
from .runtime import ContractError
from .validation import read_spec, validate

REQUIRED = ('challenge.json', 'generate.py', 'test_generate.py', 'README.md', 'WRITEUP_PRIVADO.md')
EXCLUDED = {'.git', '.codex', '.venv', 'venv', '.gradle', '__pycache__', 'build', 'dist', 'node_modules'}


def source_files(source, spec):
    source = Path(source).resolve()
    names = list(REQUIRED) + list(spec['source_paths'])
    for optional in ('assets', 'requirements.txt'):
        if (source / optional).exists():
            names.append(optional)
    files = {}
    for name in names:
        relative = PurePosixPath(name)
        if relative.is_absolute() or '\\' in name or ':' in name or '..' in relative.parts or name in ('.', ''):
            raise ContractError('Ruta de fuente inválida')
        path = source.joinpath(*relative.parts)
        if not path.exists() or not path.resolve().is_relative_to(source):
            raise ContractError('Fuente declarada ausente o fuera del reto')
        candidates = [path] if path.is_file() else path.rglob('*')
        for item in candidates:
            if item.is_symlink() or getattr(item, 'is_junction', lambda: False)():
                raise ContractError('No empaquetar enlaces')
            if not item.is_file():
                continue
            rel = item.relative_to(source)
            if any(part in EXCLUDED or part.endswith('.egg-info') for part in rel.parts):
                continue
            # Bases, logs, claves sintéticas y bytecode pueden ser assets legítimos
            # de forense/crypto/reverse. No bloquearlos por extensión.
            if item.name.startswith('.env'):
                raise ContractError('Posible material local privado en fuentes declaradas')
            files[rel.as_posix()] = item
    return files


def package_challenge(source, destination, runner=None, allow_manual=False, parameters=None):
    source = Path(source).resolve()
    destination = Path(destination).absolute()
    if destination.exists() or destination.is_relative_to(source):
        raise ContractError('Elegir un ZIP nuevo fuera de la carpeta del reto')
    spec = read_spec(source)
    files = source_files(source, spec)
    report = validate(source, runner, parameters=parameters)
    if report['status'] != 'APROBADO' and not (allow_manual and report['status'] == 'REVISIÓN MANUAL'):
        raise ContractError('Entrega no aprobada; completar implementación y validación')
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Modo x: nunca sobrescribir. Solo fuentes explícitas; no copiar instancias ni cachés.
    with zipfile.ZipFile(destination, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, path in sorted(files.items()):
            archive.write(path, 'challenge/' + name)
        archive.writestr('VALIDACION.json', json.dumps(report, ensure_ascii=False, indent=2))
        archive.writestr('ENTREGA_PRIVADA.txt', 'Fuentes y write-up para el organizador. NO distribuir a participantes.\n')
    return report

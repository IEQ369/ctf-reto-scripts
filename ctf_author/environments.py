"""Entornos Python separados por reto. No son sandboxes ni despliegan servicios."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from .runtime import ContractError, file_hash, load_json

RECORD = 'ctf-environment.json'


def python_in(folder):
    folder = Path(folder)
    return folder / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')


def fingerprints(source):
    return {name: file_hash(source/name) if (source/name).is_file() else None
            for name in ('requirements.txt', 'environment.json')}


def command(args, cwd, timeout=300):
    # La salida de pip/herramientas puede contener rutas o configuración privada.
    env = {k: v for k, v in os.environ.items() if k in ('SYSTEMROOT', 'WINDIR', 'PATH', 'TEMP', 'TMP', 'HOME', 'USERPROFILE')}
    env.update(PYTHONIOENCODING='utf-8', PYTHONNOUSERSITE='1')
    try:
        result = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True,
                                encoding='utf-8', timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        raise ContractError('No se pudo ejecutar la preparación del entorno o excedió el tiempo') from None
    if result.returncode:
        raise ContractError('Preparación fallida; revisar intérprete, red, requisitos y wheels compatibles. No usar el entorno incompleto')
    return result.stdout


def prepare_environment(source, destination, python=None, trusted=False, wheelhouse=None, no_index=False):
    if not trusted:
        raise ContractError('La instalación requiere --trusted-local tras revisar fuentes y dependencias')
    from .validation import read_spec
    source = Path(source).resolve()
    spec = read_spec(source)
    destination = Path(destination).absolute()
    resolved = destination.resolve()
    if destination.exists() or resolved.is_relative_to(source) or source.is_relative_to(resolved):
        raise ContractError('Elegir un entorno NUEVO fuera de las fuentes del reto')
    if any(p.is_symlink() or getattr(p, 'is_junction', lambda: False)() for p in (destination, *destination.parents)):
        raise ContractError('No crear entornos a través de enlaces')
    executable = shutil.which(str(python or sys.executable))
    if not executable:
        raise ContractError('No se encontró el intérprete solicitado')
    version = json.loads(command([executable, '-I', '-c', 'import sys,json; print(json.dumps(list(sys.version_info[:3])))'], source, 30))
    if tuple(version[:2]) < (3, 11):
        raise ContractError('El runtime requiere Python 3.11 o superior')
    config = load_json(source/'environment.json') if (source/'environment.json').exists() else None
    if config:
        expected = tuple(map(int, config['python'].split('.')))
        if tuple(version[:len(expected)]) != expected:
            raise ContractError('El intérprete no coincide con environment.json; indicar otro con --python')
    before = fingerprints(source)
    command([executable, '-I', '-m', 'venv', str(destination)], source)
    env_python = python_in(destination)
    if (source/'requirements.txt').is_file():
        args = [str(env_python), '-I', '-m', 'pip', '--isolated', 'install', '--disable-pip-version-check',
                '--no-input', '-r', str(source/'requirements.txt')]
        if no_index:
            args.append('--no-index')
        if wheelhouse:
            wheels = Path(wheelhouse).resolve()
            if not wheels.is_dir():
                raise ContractError('Wheelhouse inexistente')
            args += ['--find-links', str(wheels)]
        command(args, source)
    command([str(env_python), '-I', '-m', 'pip', '--isolated', 'check'], source)
    packages = json.loads(command([str(env_python), '-I', '-m', 'pip', '--isolated', 'list', '--format=json', '--disable-pip-version-check'], source))
    if fingerprints(source) != before:
        raise ContractError('Los requisitos cambiaron durante la preparación; crear un entorno nuevo')
    record = {'format_version': 1, 'source': str(source), 'challenge_id': spec['id'],
              'challenge_version': spec['version'], 'python_version': version,
              'inputs': before, 'packages': packages}
    (destination/RECORD).write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    warnings = ['Este entorno separa bibliotecas Python; no aísla código ni herramientas del sistema']
    if not config:
        warnings.append('Sin environment.json: se utilizó el intérprete indicado; revisar requisitos del README')
    elif config['system_requirements']:
        warnings.append('Herramientas externas declaradas: preparación y verificación manual pendientes')
    return {'status': 'PREPARADO', 'environment': str(destination), 'python': str(env_python),
            'python_version': '.'.join(map(str, version)), 'warnings': warnings}


def checked_python(environment, source):
    """Evitar reutilizar por accidente el entorno de otro reto o requisitos viejos."""
    folder, source = Path(environment).resolve(), Path(source).resolve()
    try:
        record = load_json(folder/RECORD)
        spec = load_json(source/'challenge.json')
        if (record['format_version'] != 1 or record['source'] != str(source)
                or record['challenge_id'] != spec['id'] or record['challenge_version'] != spec['version']
                or record['inputs'] != fingerprints(source)):
            raise ValueError
        executable = python_in(folder)
        if not executable.is_file():
            raise ValueError
    except (OSError, ValueError, KeyError, TypeError):
        raise ContractError('Entorno incompleto, de otro reto o desactualizado; preparar uno nuevo') from None
    return executable

"""Lectura estructural de dependencias; no instala ni ejecuta nada."""
import re
from .runtime import ContractError


def check_requirements(text, spec):
    if not any('requirements.txt' in entry for entry in spec['requirements']):
        raise ContractError('Documentar requirements.txt en requirements')
    packages = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if not re.fullmatch(r'[A-Za-z0-9_.-]+==[A-Za-z0-9_.+-]+', line):
            raise ContractError('Dependencias deben fijar nombre==versión; no se admiten opciones, URLs ni scripts')
        name = re.sub(r'[-_.]+', '-', line.split('==')[0]).casefold()
        if name in packages:
            raise ContractError('Dependencia duplicada; declarar una sola versión por paquete')
        packages.add(name)

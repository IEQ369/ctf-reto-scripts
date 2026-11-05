"""Prepara un venv nuevo por reto; la instalación requiere código y dependencias confiables."""
import argparse
import json
from ctf_author.environments import prepare_environment
from ctf_author.runtime import ContractError, configure_stdio


def main():
    configure_stdio()
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('challenge')
    p.add_argument('--output', required=True, help='Carpeta NUEVA del entorno fuera del reto')
    p.add_argument('--python', help='Ruta a la versión de Python requerida, ya instalada')
    p.add_argument('--trusted-local', action='store_true', help='Confirma revisión de dependencias antes de instalarlas')
    p.add_argument('--wheelhouse', help='Carpeta local de wheels preparados')
    p.add_argument('--no-index', action='store_true', help='No consultar índices de paquetes')
    a = p.parse_args()
    try:
        result = prepare_environment(a.challenge, a.output, a.python, a.trusted_local, a.wheelhouse, a.no_index)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except ContractError as error:
        print(json.dumps({'status': 'RECHAZADO', 'errors': [str(error)]}, ensure_ascii=False))
        return 1
    except Exception:
        print(json.dumps({'status': 'RECHAZADO', 'errors': ['No se pudo preparar el entorno; revisar configuración']}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

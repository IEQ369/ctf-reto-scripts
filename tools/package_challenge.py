"""Empaqueta fuentes privadas para el organizador, nunca para participantes."""
import argparse
import json
from ctf_author.packaging import package_challenge
from ctf_author.runner import Runner
from ctf_author.runtime import load_json, configure_stdio, ContractError
from ctf_author.verification import DEFAULT_MAX_BYTES, DEFAULT_MAX_FILES


def main():
    configure_stdio()
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('challenge')
    p.add_argument('--output', required=True)
    p.add_argument('--parameters', help='Archivo JSON de opciones no secretas para validar')
    p.add_argument('--environment', help='Entorno preparado para este reto')
    p.add_argument('--max-files', type=int, default=DEFAULT_MAX_FILES)
    p.add_argument('--max-bytes', type=int, default=DEFAULT_MAX_BYTES)
    p.add_argument('--allow-manual', action='store_true', help='Entregar borrador marcado REVISIÓN MANUAL')
    group = p.add_mutually_exclusive_group()
    group.add_argument('--trusted-local', action='store_true')
    group.add_argument('--docker-image')
    a = p.parse_args()
    if a.environment and not a.trusted_local:
        p.error('--environment requiere --trusted-local')
    try:
        runner = Runner('local' if a.trusted_local else 'docker' if a.docker_image else 'none', a.docker_image, a.environment)
        parameters = load_json(a.parameters) if a.parameters else {}
        report = package_challenge(a.challenge, a.output, runner, a.allow_manual, parameters, a.max_files, a.max_bytes)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except ContractError as error:
        print(json.dumps({'status': 'RECHAZADO', 'errors': [str(error)]}, ensure_ascii=False))
        return 1
    except Exception:
        print('No se pudo empaquetar: comprobar validación, fuentes declaradas y destino nuevo.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

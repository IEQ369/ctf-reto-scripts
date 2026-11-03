import argparse
import json
from ctf_author.runner import Runner
from ctf_author.validation import validate
from ctf_author.runtime import load_json, configure_stdio

def main():
    configure_stdio()
    p = argparse.ArgumentParser(description='Valida un reto v3 con dos flags ficticias y repetición')
    p.add_argument('challenge')
    group = p.add_mutually_exclusive_group()
    group.add_argument('--trusted-local', action='store_true')
    group.add_argument('--docker-image')
    p.add_argument('--seed', default='ctf-validation-v3')
    p.add_argument('--json', action='store_true')
    p.add_argument('--parameters', help='Archivo JSON de opciones no secretas del reto')
    a = p.parse_args()
    runner = Runner('local' if a.trusted_local else 'docker' if a.docker_image else 'none', a.docker_image)
    try:
        parameters = load_json(a.parameters) if a.parameters else {}
    except Exception:
        p.exit(1, 'Archivo de parámetros inválido.\n')
    report = validate(a.challenge, runner, a.seed, parameters)
    if a.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(report['status'])
        for field in ('checks', 'warnings', 'errors'):
            for entry in report[field]:
                print(f'{field}: {entry}')
    return {'APROBADO': 0, 'RECHAZADO': 1, 'REVISIÓN MANUAL': 2}[report['status']]

if __name__ == '__main__':
    raise SystemExit(main())

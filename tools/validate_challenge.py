import argparse
import json
from ctf_author.runner import Runner
from ctf_author.validation import validate

def main():
    p = argparse.ArgumentParser(description='Valida entregas v2; ejecución desactivada por defecto')
    p.add_argument('challenge')
    group = p.add_mutually_exclusive_group()
    group.add_argument('--trusted-local', action='store_true')
    group.add_argument('--docker-image')
    p.add_argument('--seed', default='ctf-preparation-v2')
    p.add_argument('--bundle', help='Directorio nuevo para la entrega validada; contiene material PRIVADO')
    p.add_argument('--json', action='store_true')
    p.add_argument('--check-service', action='store_true', help='Permite consulta de salud a la URL declarada')
    a = p.parse_args()
    runner = Runner('local' if a.trusted_local else 'docker' if a.docker_image else 'none', a.docker_image)
    report = validate(a.challenge, runner, a.seed, a.bundle, a.check_service)
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

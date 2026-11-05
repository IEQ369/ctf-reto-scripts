"""Revisa un ZIP privado de entrega sin extraer ni ejecutar scripts."""
import argparse
import json
from ctf_author.runtime import configure_stdio
from ctf_author.verification import verify_package, DEFAULT_MAX_BYTES, DEFAULT_MAX_FILES


def main():
    configure_stdio()
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('package')
    p.add_argument('--sha256', help='Hash recibido por un canal confiable independiente del ZIP')
    p.add_argument('--max-files', type=int, default=DEFAULT_MAX_FILES)
    p.add_argument('--max-bytes', type=int, default=DEFAULT_MAX_BYTES)
    p.add_argument('--json', action='store_true')
    a = p.parse_args()
    report = verify_package(a.package, a.sha256, a.max_files, a.max_bytes)
    if a.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(report['status'])
        for field in ('checks', 'warnings', 'errors'):
            for entry in report[field]:
                print(f'{field}: {entry}')
        if 'sha256' in report:
            print('SHA-256: '+report['sha256'])
    return 0 if report['status'] == 'VERIFICADO' else 1


if __name__ == '__main__':
    raise SystemExit(main())

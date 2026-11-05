"""Ejecuta UN reto sin backend. Usar --flag solo con datos ficticios."""
import argparse
import json
from pathlib import Path
from ctf_author.runtime import ContractError, load_json, configure_stdio
from ctf_author.runner import Runner
from ctf_author.validation import read_spec, build_once, verify_instance


def main():
    configure_stdio()
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('challenge')
    flags = p.add_mutually_exclusive_group(required=True)
    flags.add_argument('--flag', help='Flag ficticia; queda en historial del shell')
    flags.add_argument('--flag-file', help='Archivo privado UTF-8 de una línea')
    p.add_argument('--seed', default='demo-v3')
    p.add_argument('--parameters', help='Archivo JSON de opciones no secretas')
    p.add_argument('--environment', help='Entorno preparado para este reto')
    p.add_argument('--output', required=True, help='Directorio NUEVO para una instancia')
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument('--trusted-local', action='store_true')
    group.add_argument('--docker-image')
    a = p.parse_args()
    if a.environment and not a.trusted_local:
        p.error('--environment requiere --trusted-local')
    try:
        source = Path(a.challenge).resolve()
        spec = read_spec(source)
        if spec['delivery']['kind'] != 'artifact' or spec['readiness'] != 'ready':
            raise ContractError('Solo artefactos listos; servicios requieren un integrador externo')
        output = Path(a.output).absolute()
        if output.is_relative_to(source) or source.is_relative_to(output):
            raise ContractError('Usar una salida independiente de las fuentes')
        flag = a.flag if a.flag is not None else Path(a.flag_file).read_text(encoding='utf-8').rstrip('\r\n')
        runner = Runner('local' if a.trusted_local else 'docker', a.docker_image, a.environment)
        parameters = load_json(a.parameters) if a.parameters else {}
        request, manifest = build_once(source, spec, runner, output, a.seed, flag, parameters)
        verify_instance(source, spec, runner, request, manifest, flag)
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 0
    except Exception:
        print(json.dumps({'schema_version': 3, 'status': 'error', 'code': 'generation_failed'}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())

"""Ejecutores explícitos. Local solo para código confiable; Docker es opcional."""
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile
from .runtime import ContractError


class Runner:
    def __init__(self, mode='none', image=None):
        self.mode, self.image = mode, image
        if mode == 'docker' and not image:
            raise ContractError('Indicar imagen preparada para ejecución aislada')

    def execute(self, source, script, request, limits):
        if self.mode == 'none':
            raise ContractError('Ejecución no autorizada: seleccionar ejecutor')
        source = Path(source).resolve()
        kit = Path(__file__).resolve().parent.parent
        environment = {k: v for k, v in os.environ.items() if k in ('SYSTEMROOT', 'WINDIR', 'PATH', 'TEMP', 'TMP')}
        environment.update(PYTHONPATH=str(kit), PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1')
        container = 'ctf-check-' + secrets.token_hex(8)
        payload = dict(request)
        if self.mode == 'docker':
            cmd = ['docker', 'run', '--rm', '--name', container, '--network=none',
                   '--read-only', '--cap-drop=ALL', '--security-opt=no-new-privileges',
                   '--memory', f"{limits['memory_mb']}m", '--memory-swap', f"{limits['memory_mb']}m",
                   '--cpus=1', '--pids-limit=64', '--user=65534:65534',
                   '--tmpfs', '/tmp:rw,noexec,nosuid,size=64m',
                   '-v', f'{source}:/challenge:ro', '-v', f'{kit}:/kit:ro',
                   '-v', f"{request['output_dir']}:/public:rw",
                   '-v', f"{request['private_dir']}:/private:rw",
                   '-e', 'PYTHONPATH=/kit', '-e', 'PYTHONDONTWRITEBYTECODE=1',
                   '-w', '/challenge', '-i', self.image, 'python', script]
            payload.update(output_dir='/public', private_dir='/private')
        else:
            cmd = [sys.executable, '-B', str(source / script)]
        # Archivos temporales evitan almacenar salida ilimitada en memoria.
        # La cuota de disco del trabajador es responsabilidad del sandbox externo.
        with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
            try:
                result = subprocess.run(cmd, input=json.dumps(payload).encode(), stdout=out,
                                        stderr=err, cwd=source, env=environment,
                                        timeout=limits['seconds'])
            except subprocess.TimeoutExpired:
                if self.mode == 'docker':
                    subprocess.run(['docker', 'rm', '-f', container], capture_output=True, timeout=15)
                raise ContractError('Tiempo de ejecución excedido') from None
            if result.returncode:
                raise ContractError('Falló el programa del autor; salida privada suprimida')
            if out.tell() > 1024 * 1024 or err.tell() > 1024 * 1024:
                raise ContractError('Salida de diagnóstico excesiva')
            out.seek(0)
            return out.read().decode('utf-8')

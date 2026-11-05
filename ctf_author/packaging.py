"""Entrega privada de fuentes de UN reto, verificada antes de publicarla en disco."""
import json
from pathlib import Path
import shutil
import tempfile
import zipfile
from .runtime import ContractError, file_hash
from .validation import read_spec, validate
from .sources import source_files, REQUIRED, EXCLUDED
from .verification import verify_package, DEFAULT_MAX_FILES, DEFAULT_MAX_BYTES


def package_challenge(source, destination, runner=None, allow_manual=False, parameters=None,
                      max_files=DEFAULT_MAX_FILES, max_bytes=DEFAULT_MAX_BYTES):
    source = Path(source).resolve()
    destination = Path(destination).absolute()
    if destination.exists() or destination.resolve().is_relative_to(source):
        raise ContractError('Elegir un ZIP nuevo fuera de la carpeta del reto')
    spec = read_spec(source)
    files = source_files(source, spec)
    before = {name: file_hash(path) for name, path in files.items()}
    report = validate(source, runner, parameters=parameters)
    if report['status'] != 'APROBADO' and not (allow_manual and report['status'] == 'REVISIÓN MANUAL'):
        raise ContractError('Entrega no aprobada; completar implementación y validación')
    current = source_files(source, read_spec(source))
    if before != {name: file_hash(path) for name, path in current.items()}:
        raise ContractError('La validación modificó las fuentes; no se empaqueta una entrega diferente')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='ctf-package-') as temporary:
        prepared = Path(temporary)/'delivery.zip'
        with zipfile.ZipFile(prepared, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
            for name, path in sorted(current.items()):
                archive.write(path, 'challenge/' + name)
            archive.writestr('VALIDACION.json', json.dumps(report, ensure_ascii=False, indent=2))
            archive.writestr('ENTREGA_PRIVADA.txt', 'Fuentes y write-up para el organizador. NO distribuir a participantes.\n')
        verification = verify_package(prepared, max_files=max_files, max_bytes=max_bytes)
        if verification['status'] != 'VERIFICADO':
            raise ContractError('El paquete generado no supera la verificación: ' + '; '.join(verification['errors']))
        # Nunca sobrescribir una entrega existente, incluso si apareció durante la validación.
        with destination.open('xb') as output, prepared.open('rb') as incoming:
            shutil.copyfileobj(incoming, output)
        report['package_sha256'] = verification['sha256']
        report['package_verification'] = 'VERIFICADO'
    return report

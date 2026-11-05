"""Verificación estática de entregas: nunca extrae ni ejecuta scripts del ZIP."""
from pathlib import Path
import re
import stat
import zipfile
from .dependencies import check_requirements
from .runtime import ContractError, decode_json, file_hash, safe_name
from .sources import REQUIRED, OPTIONAL, portable_path, excluded
from .validation import schema_check

DEFAULT_MAX_FILES = 4096
DEFAULT_MAX_BYTES = 512 * 1024 * 1024
METADATA_LIMIT = 1024 * 1024


def verify_package(path, expected_sha256=None, max_files=DEFAULT_MAX_FILES, max_bytes=DEFAULT_MAX_BYTES):
    report = {'status': 'RECHAZADO', 'errors': [], 'warnings': [], 'checks': []}
    try:
        path = Path(path)
        if type(max_files) is not int or max_files < 1 or type(max_bytes) is not int or max_bytes < 1:
            raise ContractError('Límites de paquete inválidos')
        if path.stat().st_size > max_bytes + 16 * 1024 * 1024:
            raise ContractError('ZIP excede el tamaño permitido')
        digest = file_hash(path)
        if expected_sha256 is not None:
            if not re.fullmatch(r'[0-9a-fA-F]{64}', expected_sha256) or digest != expected_sha256.lower():
                raise ContractError('SHA-256 no coincide con el valor esperado')
            report['checks'].append('SHA-256 coincide con el valor externo proporcionado')
        else:
            report['warnings'].append('CRC comprueba corrupción; sin SHA-256 externo confiable no se demuestra autenticidad ni se detecta toda reescritura del ZIP')
        with zipfile.ZipFile(path) as archive:
            entries = archive.infolist()
            if len(entries) > max_files or sum(i.file_size for i in entries) > max_bytes:
                raise ContractError('Paquete excede límites de entradas o descompresión')
            names, namespaces = {}, {}
            for item in entries:
                raw = item.orig_filename
                name = raw[:-1] if item.is_dir() else raw
                portable_path(name)
                if name in names:
                    raise ContractError('Entradas duplicadas en el paquete')
                parts = name.split('/')
                for count in range(1, len(parts)+1):
                    prefix = '/'.join(parts[:count])
                    canonical = prefix.casefold()
                    if canonical in namespaces and namespaces[canonical] != prefix:
                        raise ContractError('Entradas ambiguas por mayúsculas/minúsculas')
                    namespaces[canonical] = prefix
                mode = stat.S_IFMT(item.external_attr >> 16)
                if mode not in (0, stat.S_IFREG, stat.S_IFDIR) or item.external_attr & 0x400:
                    raise ContractError('Enlace o tipo especial dentro del paquete')
                if mode == stat.S_IFDIR and not item.is_dir() or mode == stat.S_IFREG and item.is_dir():
                    raise ContractError('Tipo de entrada inconsistente')
                if item.flag_bits & 1 or item.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
                    raise ContractError('Entrega cifrada o compresión no admitida')
                names[name] = item
            for name, item in names.items():
                for parent in Path(name).parents:
                    key = parent.as_posix()
                    if key in names and not names[key].is_dir():
                        raise ContractError('Colisión entre archivo y directorio')
                if name == 'challenge' and item.is_dir():
                    continue
                if not name.startswith('challenge/') and name not in ('VALIDACION.json', 'ENTREGA_PRIVADA.txt'):
                    raise ContractError('Estructura raíz de entrega inválida')

            def metadata(name, allow_empty=False):
                item = names.get(name)
                if item is None or item.is_dir() or item.file_size > METADATA_LIMIT or (not allow_empty and not item.file_size):
                    raise ContractError('Metadato obligatorio ausente, vacío o demasiado grande')
                return archive.read(item).decode('utf-8')

            spec = decode_json(metadata('challenge/challenge.json'))
            schema_check(spec, 'challenge')
            for name in spec['public_files']:
                safe_name(name)
            for name in REQUIRED:
                item = names.get('challenge/'+name)
                if item is None or item.is_dir() or not item.file_size:
                    raise ContractError('Falta una fuente obligatoria en la entrega')
            # El informe es información del remitente, no evidencia de aprobación.
            if not isinstance(decode_json(metadata('VALIDACION.json')), dict):
                raise ContractError('Reporte de autor inválido')
            metadata('ENTREGA_PRIVADA.txt')
            files = {name[len('challenge/'):]: item for name, item in names.items()
                     if name.startswith('challenge/') and not item.is_dir()}
            declared = []
            for name in spec['source_paths']:
                portable_path(name)
                if excluded(name):
                    raise ContractError('Fuente declarada excluida')
                if name not in files and not any(f.startswith(name+'/') for f in files):
                    raise ContractError('Falta un recurso declarado en source_paths')
                declared.append(name)
            allowed = list(REQUIRED) + list(OPTIONAL) + declared
            for name in files:
                if excluded(name) or Path(name).name.casefold().startswith('.env'):
                    raise ContractError('Configuración local o caché en paquete')
                if not any(name == base or name.startswith(base+'/') for base in allowed):
                    raise ContractError('Fuente no declarada en paquete')
            if 'requirements.txt' in files:
                check_requirements(metadata('challenge/requirements.txt', allow_empty=True), spec)
            if 'environment.json' in files:
                schema_check(decode_json(metadata('challenge/environment.json')), 'environment')
            # Streaming: comprobar CRC y tamaños reales sin expandir el ZIP en disco.
            consumed = 0
            for item in entries:
                size = 0
                with archive.open(item) as stream:
                    while block := stream.read(64 * 1024):
                        size += len(block)
                        consumed += len(block)
                        if consumed > max_bytes or size > item.file_size:
                            raise ContractError('Límite de descompresión excedido')
                if size != item.file_size:
                    raise ContractError('Tamaño real inconsistente')
        report.update(status='VERIFICADO', sha256=digest)
        report['checks'].extend(['Estructura privada y contrato v3', 'Fuentes obligatorias y recursos declarados',
                                 'Rutas, tipos, duplicados, tamaños y CRC de cada entrada'])
        report['warnings'].append('No se ejecutó código ni se comprobó resolución; VALIDACION.json no se considera prueba confiable')
    except ContractError as error:
        report['errors'].append(str(error))
    except Exception:
        report['errors'].append('ZIP inválido, corrupto o ilegible; detalles internos suprimidos')
    return report

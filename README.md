# CTF Reto Scripts — contrato v3

Kit para que cada autor programe **un generador por reto**. Dos retos significan dos
carpetas, cada una con su `generate.py`. Ejecutar el mismo generador con otra flag
produce otra instancia de la misma mecánica; el kit no inventa retos.

El organizador proporciona la flag. El generador no crea flags, no conoce usuarios
y no necesita una web, una base de datos ni un motor de puntuaciones.

## Inicio rápido (PowerShell)

Descarga **Code → Download ZIP** del repositorio y descomprímelo, o clónalo con
`git clone https://github.com/IEQ369/ctf-reto-scripts.git`.

Desde la carpeta del repositorio, con Python 3.11 o superior:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
$py = ".\.venv\Scripts\python.exe"
```

Ejecutar **el mismo reto forense** con dos flags ficticias:

```powershell
& $py tools/generate_instance.py examples/forensics --flag 'CTF{A123}' --output work/a --trusted-local
& $py tools/generate_instance.py examples/forensics --flag 'CTF{B987}' --output work/b --trusted-local
& $py tools/validate_challenge.py examples/forensics --trusted-local
```

`work/a/evidencia.zip` contiene `CTF{A123}` en el comentario del ZIP;
`work/b/evidencia.zip` contiene `CTF{B987}`. Ambos usan la misma mecánica.
El comando de generación también resuelve la instancia y comprueba su flag.
Las salidas deben ser carpetas nuevas: no se sobrescriben instancias existentes.

`--trusted-local` ejecuta código en tu equipo: úsalo con estos ejemplos o código que
hayas revisado. Las flags de este ejemplo son ficticias. Para una flag real usa un
canal privado de entrada, no el historial del shell.

## Crear y entregar tu propio reto

```powershell
& $py tools/create_challenge.py mis-retos/forense-03 --id forense-03 --category forensics
# Completar mecánica, prueba, documentación y metadatos; marcar readiness=ready.
& $py tools/prepare_environment.py mis-retos/forense-03 --output work/env-forense-03 --trusted-local
& $py tools/validate_challenge.py mis-retos/forense-03 --environment work/env-forense-03 --trusted-local
& $py tools/package_challenge.py mis-retos/forense-03 --output bundles/forense-03.zip --environment work/env-forense-03 --trusted-local
& $py tools/verify_package.py bundles/forense-03.zip
```

La plantilla inicialmente **no funciona**: indica exactamente dónde programar.
El ZIP de entrega contiene fuentes y write-up privado; se entrega al organizador,
**no a participantes**. Las descargas del participante son únicamente los archivos
de una instancia generada, enumerados en su manifiesto.

Cada reto puede usar un entorno Python distinto; sus dependencias no se instalan
en el entorno de los demás. `environment.json` declara la versión del intérprete
y las herramientas externas; `requirements.txt` fija las bibliotecas del reto.
Los venv separan dependencias, no aíslan código ni SDK del sistema.
`VERIFICADO` comprueba el ZIP sin ejecutar código; no equivale a `APROBADO` funcional.

## Qué leer

- [Guía de autores](GUIA_AUTORES.md): crear, resolver, probar y entregar un reto.
- [Contrato técnico](CONTRATO_TECNICO.md): JSON, integración externa y servicios.
- [Seguridad](SEGURIDAD.md): separación de material y límites de la validación.
- [Resultados de pruebas](docs/RESULTADOS_PRUEBAS.md): comprobaciones realmente ejecutadas.
- [Historial v2](docs/HISTORIAL_V2.md): información anterior conservada; no es la guía vigente.

## Estructura del repositorio

```text
README.md / GUIA_AUTORES.md / CONTRATO_TECNICO.md / SEGURIDAD.md
ctf_author/              runtime, validación, ejecución y empaquetado
  schemas/              contratos JSON v3
tools/                  crear, preparar entorno, generar, validar, empaquetar y verificar
templates/              artifact-generated, service, blockchain-service
examples/               ejemplos y borradores identificados por categoría
tests/                  pruebas del kit y de CLI
docs/                   resultados actuales e historial anterior
```

Funcionan los ejemplos de archivos **forensics, cryptography y reverse**. Mobile
requiere compilación Android. Web y blockchain incluyen contratos de integración
y adaptadores incompletos, no servicios desplegados. Permanecen en REVISIÓN MANUAL.
OSINT no forma parte de las categorías oficiales del kit.

**Migración:** v3 sustituye la respuesta común de v2 por una flag externa por instancia.
El motor anterior y los retos v2 no son compatibles sin adaptación. No se modificó
el proyecto separado del motor. Un reto existente debe migrarse conscientemente;
no basta con cambiar el número de versión.

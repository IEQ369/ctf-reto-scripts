# CTF Reto Scripts

**Plantillas y herramientas para crear, probar y entregar retos CTF.**

Repositorio: [IEQ369/ctf-reto-scripts](https://github.com/IEQ369/ctf-reto-scripts). Protocolo de autores: v2.

## ¿Por dónde empiezo?

1. Descarga el repositorio con **Code → Download ZIP**, o usa `git clone https://github.com/IEQ369/ctf-reto-scripts.git`.
2. Instala el kit siguiendo los pasos de abajo.
3. Lee [Cómo crear un reto](COMO_CREAR_UN_RETO.md) y copia una plantilla.
4. Valida tu reto y entrega su carpeta al organizador por el canal privado acordado.

Consulta [el contrato de entrega](CONTRATO_AUTORES.md),
[las diferencias por categoría](GUIA_POR_CATEGORIA.md) y
[cómo colaborar en este repositorio](CONTRIBUTING.md).

Entrega para autores de un CTF universitario. Cada reto produce **un mismo material y una
misma respuesta para todos**. La web canjea esa respuesta por una flag personal que
asigna el motor. El generador nunca conoce usuarios ni flags personales.

## Primer uso

Recomendado: Python 3.13, entorno virtual dedicado. El runtime admite Python 3.11+;
el bytecode del ejemplo reverse debe analizarse con la misma versión que lo compiló.
Desde esta carpeta:

```text
python -m venv .venv
```

Windows PowerShell: `.\.venv\Scripts\Activate.ps1` (usar `./.venv/Scripts/python.exe`
directamente si la política de PowerShell impide activar). Linux/macOS:
`source .venv/bin/activate`. Luego:

```text
python -m pip install -e .
python tools/validate_challenge.py examples/forensics --trusted-local
python -m unittest discover -s tests -v
python tools/create_challenge.py mis-retos/forense-02 --template artifact-generated --id forense-02 --category forensics
```

`--trusted-local` autoriza ejecutar el código revisado del ejemplo en tu máquina;
no es seguro para entregas desconocidas. Sin esa opción se hace revisión estructural
y se devuelve REVISIÓN MANUAL antes de ejecutar. Consulta SEGURIDAD.md.

Completa la función `construir_reto(contexto)` y la prueba de resolución. Sigue
COMO_CREAR_UN_RETO.md. No necesitas la plataforma ni el motor para trabajar.

## Archivos del kit

- `templates/`: generated, static, service y blockchain-service.
- `examples/`: seis categorías; los tres primeros ejemplos son ejecutables.
- `ctf_author/runtime.py`: trabajo repetitivo de los generadores.
- `ctf_author/schemas/`: cuatro esquemas JSON Schema 2020-12 instalables junto al código.
- `ctf_author/validation.py`: inspección y preparación offline.
- `tools/`: crear y validar entregas.
- `tests/`: pruebas del contrato y del validador.

Los esquemas están dentro del paquete Python para que funcionen también después de
instalarlo, sin depender de la carpeta actual. Cada entrega depende de este runtime
versionado; no se copian implementaciones del validador a cada reto.

El kit usa jsonschema para validar los contratos, no un validador JSON parcial hecho
a mano. La instalación de dependencias ocurre durante la preparación del entorno,
nunca dentro de un generador. El repositorio incluye el código y los ejemplos, no la .venv.

El paquete instalable conserva el identificador técnico `ctf-author-kit` y los imports
`ctf_author`, para mantener la compatibilidad con los scripts y el motor existentes.
El nombre de la carpeta y del repositorio es `ctf-reto-scripts`.

Los tres ejemplos introductorios muestran la interfaz, no dificultad de torneo.
Ver RESULTADOS_PRUEBAS.md para resultados reales y pendientes.

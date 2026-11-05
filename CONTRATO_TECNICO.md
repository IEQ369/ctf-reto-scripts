# Contrato técnico v3

## Alcance

Un directorio identifica un reto y una versión. Su `generate.py` construye una sola
instancia por ejecución. Otro programa selecciona la flag; el generador no recibe
usuario, cuenta, autenticación ni clave maestra. No se implementan backend, caché,
registro, puntuación o asignación de flags en este repositorio.

## Entrada del generador

Invocar `python generate.py`, con cwd en la carpeta del reto y el kit instalado.
Enviar exactamente un objeto JSON UTF-8 por stdin y cerrar stdin:

```json
{
  "schema_version": 3,
  "challenge_id": "forense-01",
  "challenge_version": 1,
  "flag": "CTF{A123}",
  "seed": "demo-v3",
  "output_dir": "C:/ctf/work/instancia-a",
  "parameters": {}
}
```

El ID y versión reales deben coincidir con `challenge.json`. `output_dir` debe ser absoluto, existente, vacío
y exclusivo de la ejecución, sin enlaces en su ruta. La herramienta CLI crea ese
directorio; quien llame directamente al generador debe crearlo antes.

Flag: 1–512 caracteres ASCII imprimibles, sin espacios; no se impone un prefijo.
Semilla: texto de 1–128 caracteres. `parameters`: objeto JSON pequeño, máximo 16 KiB
serializado según el runtime, para opciones no secretas propias del reto. El autor
debe documentarlas y validarlas. No usarlo como canal de identidades o claves maestras.

El esquema es `ctf_author/schemas/generation-request.schema.json`; el runtime añade
comprobaciones de rutas y límites que JSON Schema por sí solo no expresa.
La biblioteca ofrece `construir_reto(contexto)` y `run(construir_reto)`.

## Salida de artefactos

En éxito: código de proceso 0 y un único JSON en stdout:

```json
{
  "schema_version": 3,
  "status": "ok",
  "challenge_id": "forense-01",
  "challenge_version": 1,
  "kind": "artifact",
  "files": [
    {"name": "evidencia.zip", "size": 146, "sha256": "<64 dígitos hexadecimales>"}
  ]
}
```

Tamaño y hash anteriores son ilustrativos. El generador calcula los reales.
Los archivos deben coincidir exactamente con `public_files`. Nombres planos y
portables: sin subdirectorios ni rutas absolutas. Para varios archivos relacionados,
puede entregarse un ZIP. No incluir la flag en nombres ni en el manifiesto.

En fallo, el runtime devuelve código 1 y:

```json
{"schema_version": 3, "status": "error", "code": "generation_failed"}
```

Los diagnósticos genéricos van a stderr. Un fallo puede dejar archivos parciales;
no deben publicarse. La infraestructura externa debe gestionar su limpieza.
El runtime no publica el texto de excepciones del autor.

## Resolución y validación

`test_generate.py` recibe los mismos campos de entrada **excepto `flag`**. Devuelve
`{"schema_version":3,"recovered_flag":"..."}`. Es un canal privado de pruebas, no
una API pública. El validador compara por igualdad exacta y no imprime la flag.

Se ejecutan tres generaciones: flag A, repetición de A y flag B; misma semilla y
parámetros. Se comprueba resolución de las tres, diferencia entre instancias A/B y
rechazo de B como respuesta de A. Para retos reproducibles se comparan manifiestos,
incluidos SHA-256 de todos los archivos. La prueba se ejecuta en otro proceso, pero
su autor sigue siendo responsable de escribir una resolución honesta y suficiente.

`reproducible: false` exige explicación y REVISIÓN MANUAL. Los entornos de compilación
deben fijarse: distintas versiones de Python, SDK o compiladores pueden cambiar bytes.

## Modalidad de servicio: integración explícita, no despliegue implementado

Un reto `service` conserva su propio `generate.py`, pero implementa un adaptador de
infraestructura con `run_service(construir_reto)`. Usa el mismo contexto y recibe la
flag por stdin. Debe aprovisionar UNA instancia aislada e inyectar allí la flag por
un canal privado. No necesita generar archivos descargables.

El builder devuelve un descriptor y el runtime lo envuelve así:

```json
{
  "schema_version": 3,
  "status": "ok",
  "challenge_id": "web-01",
  "challenge_version": 1,
  "kind": "service",
  "service": {
    "endpoint": "https://instancia.example/reto",
    "instance_ref": "referencia-opaca"
  }
}
```

`instance_ref` es una referencia de infraestructura, no un usuario. El descriptor
no contiene flag, credenciales ni tokens de administración. El endpoint permitido
por esta versión es HTTP(S); protocolos diferentes necesitan ampliar el contrato.
`output_dir` permanece vacío en esta modalidad; es compatible con el contexto común.

El integrador debe ejecutar `test_generate.py` contra el descriptor sin darle la
flag esperada y comparar la flag recuperada. Debe ejecutar además pruebas de
aislamiento entre dos instancias. El kit **no automatiza estas pruebas de servicio**.

Se reserva `cleanup.py`: stdin con `schema_version: 3` e `instance_ref`, eliminación
idempotente de esa instancia y salida JSON `{"schema_version":3,"status":"ok"}`
con código 0. El responsable debe documentar también cómo limpiar un despliegue que
falla antes de devolver descriptor. Las plantillas de creación y limpieza están
deliberadamente sin implementar. Un HTTP 200 no demuestra que un reto se resuelve.

Docker no es obligatorio. Puede usarse infraestructura externa con su autorización
y aislamiento. El runner Docker del kit, sin red, sirve para construcción de
artefactos; no es un orquestador de servicios. No montes el socket Docker para
convertir el generador en administrador de la máquina.

Web y blockchain quedan siempre en REVISIÓN MANUAL en el validador actual. Blockchain
mutable requiere cadena de prueba/cuentas/contrato por instancia y política de reset;
un único contrato mutable compartido no cumple este contrato de personalización.

## Entrega al futuro programa del servidor

El formato de entrada/salida v3 no cambia. Se añade un archivo de autor opcional
`environment.json`, validado por `schemas/environment.schema.json`, sin campos nuevos
en el contexto del generador. Los retos existentes que no lo contienen siguen siendo
válidos; su preparación avisa que la versión de Python debe revisarse en el README.

`prepare_environment.py` crea un venv por reto, instala su `requirements.txt`, ejecuta
`pip check` y registra Python, versiones instaladas y hashes de requisitos/configuración
en `ctf-environment.json` dentro del entorno local. No ejecuta el generador ni instala
SDK del sistema. `--environment` selecciona ese intérprete para generar, resolver y
empaquetar; exige `--trusted-local`. Docker continúa usando su propia imagen.

El registro vincula entorno, carpeta, ID y versión; un cambio de requisitos o ubicación
obliga a prepararlo de nuevo. No certifica que nadie haya modificado manualmente el venv.
Las herramientas suministran el runtime del kit mediante PYTHONPATH y desactivan el
site-packages del usuario. No se instala todo el kit dentro del entorno del reto.
La invocación directa fuera de estas herramientas requiere hacer accesible el runtime
en PYTHONPATH. Un adaptador que use `run_service` necesita además `jsonschema` para
validar su descriptor: debe declararlo como dependencia. Sus pruebas son manuales.

`verify_package.py` lee la entrega sin extraerla ni ejecutar código. Acepta ZIP STORED
o DEFLATED, rechaza cifrado, enlaces, entradas duplicadas/ambiguas, recursos faltantes,
rutas peligrosas y archivos ajenos a las fuentes declaradas. Por defecto admite 4096
entradas y 512 MiB descomprimidos; `--max-files` y `--max-bytes` permiten ajustar esos
límites tanto al empaquetar como al verificar. Los metadatos tienen un límite de 1 MiB.
Los directorios declarados en `source_paths` deben aportar archivos; los directorios
vacíos de trabajo deben crearse durante la preparación/generación.

Salida estática: `VERIFICADO` y código 0, o `RECHAZADO` y código 1. No equivale a aprobación
funcional. Se valida CRC y se calcula SHA-256 del ZIP completo; solo `--sha256` con un
valor externo confiable detecta una reescritura coherente de la entrega. No se añade
un manifiesto redundante ni se confía en la aprobación declarada en `VALIDACION.json`.

El organizador recibe el ZIP PRIVADO de fuentes, con el reto, write-up, prueba,
assets, dependencias declaradas y reporte de validación. Después de extraerlo en un
entorno confiable y revisar dependencias, el futuro programa necesita:

1. Ruta del reto y su `challenge.json`.
2. Intérprete/entorno y dependencias preparados.
3. Flag suministrada externamente, semilla y parámetros documentados.
4. Directorio nuevo por ejecución y política de permisos/aislamiento/limpieza.
5. Invocar el proceso, enviar JSON por stdin y validar código de salida y manifiesto.
6. Servir únicamente archivos declarados de la instancia exitosa, o el endpoint
   aprobado de un servicio. Nunca publicar el ZIP privado de entrega.

La ejecución directa no necesita modificar el generador. El servidor deberá hacer
sus propias comprobaciones del resultado; no confiar solo en que stdout dice `ok`.
El motor v2 separado no acepta automáticamente este protocolo y no fue modificado.

## Migración desde v2

- Sustituir `contexto.answer(...)` y la respuesta común por `contexto.flag` dentro
  de la mecánica del reto. Ya no existe `private_dir` ni `answer.json` obligatorio.
- Renombrar la solución a `WRITEUP_PRIVADO.md` y adaptar el solucionador para extraer
  la flag de archivos, devolviéndola por su canal privado.
- Actualizar metadatos v3, reproducibilidad y fuentes adicionales.
- Sustituir artefactos estáticos por assets más un generador que personalice la flag.
- Validar con dos flags. No cambiar solamente `schema_version`.

Las instrucciones y resultados anteriores se conservaron en `docs/HISTORIAL_V2.md`.

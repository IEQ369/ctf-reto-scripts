# Protocolo v2

Fuente normativa: `ctf_author/schemas/*.schema.json`. Objetos cerrados: se rechazan
propiedades desconocidas. Categorías: forensics, cryptography, reverse, mobile,
web, blockchain. Modalidades: artifact y service; artifact.build es generated o
static. Dificultad: intro, easy, medium, hard. Versiones enteras positivas.

## Entrada de generador por stdin

```json
{"schema_version":2,"challenge_id":"forense-01","challenge_version":1,"seed":"preparacion-v1","output_dir":"/job/public","private_dir":"/job/private"}
```

Rutas absolutas, vacías, existentes, distintas y sin anidarse. No hay user_id ni
flag. Windows recibe rutas absolutas de Windows. UTF-8 en todas las interfaces.

## Manifiesto por stdout

```json
{"schema_version":2,"files":[{"name":"evidencia.zip","size":2048,"sha256":"0000000000000000000000000000000000000000000000000000000000000000"}]}
```

Tamaño y hash ilustrativos: siempre se calculan del archivo real. Entre 1 y el
límite configurado de archivos no vacíos. Nombres simples sin carpetas, dos puntos,
rutas absolutas ni nombres reservados de Windows. No se admiten enlaces, hardlinks
en la salida ni archivos no declarados. stdout contiene solo el JSON.

## Respuesta privada: private_dir/answer.json

```json
{"schema_version":2,"answer":"archivo_recuperado","comparison":{"strip":true,"casefold":false}}
```

Una respuesta de 1 a 512 caracteres. strip elimina espacios Unicode iniciales y
finales según Python; casefold aplica str.casefold. Se ejecutan en ese orden. No
se eliminan espacios internos ni se normaliza Unicode automáticamente. Se rechaza
una respuesta normalizada vacía. Si hacen falta variantes, diseñarlas antes de
extender el esquema; v2 no acepta listas, regex ni código de validación arbitrario.

El answer.json original es material organizativo privado. El motor importa un
HMAC con clave del servidor y no necesita conservar la respuesta en claro.

## Metadatos

Consultar ejemplos: contienen todos los campos requeridos. `author` es opcional y
privado. `requirements` describe herramientas; `hints` son pistas públicas;
`public_files` enumera descargas. Servicio tiene URL y health_url, management,
state, isolation y deployment_notes. Blockchain-service añade chain_id, red local,
cuentas, reset y alcance del contrato. Estos datos de infraestructura no se
publican íntegramente: el motor selecciona los campos públicos.

Límites iniciales: 30 s por programa, 256 MiB de memoria, 20 archivos, 50 MiB de
artefactos. El esquema permite como techo 600 s, 4096 MiB, 100 archivos y 512 MiB;
la organización debe revisar cualquier aumento. El runner Docker aplica memoria,
CPU y procesos; la cuota de disco del host se configura externamente. El runner
local no impone memoria ni evita escrituras fuera del contrato. El validador sí
comprueba tamaños finales. No confundir verificación posterior con aislamiento.

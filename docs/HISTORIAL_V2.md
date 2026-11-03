# Historial v2 — NO es el contrato vigente

Conservación de requisitos, decisiones y resultados anteriores. El contrato v3 sustituye el modelo de respuesta común. Las instrucciones y pruebas de esta sección son históricas; no ejecutar sus comandos como guía actual.


---

## Documento anterior: ARQUITECTURA.md

# Responsabilidades y fases

Autor → código, metadatos y solución privada → validador offline → bundle aprobado.
Motor → importa bundle → almacena artefacto común + verificador de respuesta →
asigna flags personales → API para una plataforma independiente.

El motor del evento no necesita ejecutar ni conservar generadores. Durante el
evento, resolver solo lee archivos preparados y realiza operaciones de BD.
Las flags individuales se asignan con anticipación o al registrar tarde una cuenta,
sin reconstruir el reto. Canjear una respuesta no concede puntos; enviar la flag
propia sí. Las respuestas pueden compartirse y este modelo no lo detecta.

Fuentes y bundles contienen secretos y se almacenan fuera del árbol público. El
catálogo público usa una lista explícita de campos. Ni solution ni answer.json ni
metadatos internos de autor o despliegue se sirven como descargas.

Entrega 1: kit completo y probado. Entrega 2: motor por CLI. Entrega 3: API con
autenticación real y adaptable. Entrega 4: pruebas de integración. El directorio
CTF-ENGINE separado documentará su esquema y las decisiones de implementación.


---

## Documento anterior: COMO_CREAR_UN_RETO.md

# Crear tu primer reto

1. Instala el kit siguiendo README.md y prueba el ejemplo de forense.
2. Copia una carpeta de templates o usa create_challenge.py. Usa artifact-generated
   para construir archivos, artifact-static para archivos existentes y service para
   una aplicación administrada aparte. No elijas por categoría solamente.
3. Completa título, enunciado, categoría, dificultad, puntos y public_files en
   challenge.json. El ID no debe contener espacios ni datos personales.
4. En un generado, completa únicamente la mecánica dentro de construir_reto:

```python
def construir_reto(contexto):
    import codecs
    respuesta = 'mensaje_recuperado'
    archivo = contexto.output_dir / 'mensaje.txt'
    archivo.write_text(codecs.encode(respuesta, 'rot_13'), encoding='utf-8')
    contexto.answer(respuesta, strip=True, casefold=False)
    return ['mensaje.txt']
```

5. Declara `mensaje.txt` en public_files. En la prueba, lee mensaje.txt, aplica ROT13
   y compara con answer.json. Copia el patrón de examples/cryptography/test_generate.py.
6. Documenta la solución y las versiones de tus herramientas. `strip=True` admite
   espacios al principio/final; `casefold=False` conserva mayúsculas. Es una decisión
   de diseño explícita; no cambia después de publicar la versión.
7. Cambia readiness a ready cuando hayas terminado. Ejecuta el validador y corrige
   cada error. Comprueba que tu solución no necesita conocer datos de usuarios.
8. Entrega toda la carpeta al organizador, incluido material privado. Él publicará
   únicamente los archivos listados. Nunca subas la carpeta completa a la web.

Para un reto estático, reemplaza el instructivo de public/ por tus archivos y edita
private/answer.json. La preparación no modifica los originales. Para APK, prepara
el APK antes y analiza el resultado real, no solo el proyecto fuente.


---

## Documento anterior: COMO_VALIDAR_UN_RETO.md

# Validación

Desde la carpeta del kit, con el entorno activado:

```text
python tools/validate_challenge.py examples/forensics
python tools/validate_challenge.py examples/forensics --trusted-local --json
python tools/validate_challenge.py examples/forensics --trusted-local --bundle work/preparado-forense
python tools/validate_challenge.py examples/cryptography --trusted-local
python tools/validate_challenge.py examples/reverse --trusted-local
python tools/validate_challenge.py examples/web --json
python -m unittest discover -s tests -v
```

El primer comando devuelve REVISIÓN MANUAL: no ejecuta código. Los siguientes
ejecutan código confiable del kit. Un bundle usa un directorio nuevo y contiene
public/, private/, challenge.json, manifest.json y validation.json; **no es un
paquete para participantes**. La preparación repite la construcción dos veces
para probar reproducibilidad y conserva el primer resultado. El motor reutiliza
ese bundle sin volver a ejecutar el generador al publicarlo.

Estados y códigos de salida: APROBADO=0, RECHAZADO=1, REVISIÓN MANUAL=2.
APROBADO confirma comprobaciones automáticas en el entorno seleccionado; no una
auditoría de seguridad ni calidad pedagógica. Servicio pendiente permanece manual,
incluso si un health check pasa. `--check-service` permite una consulta de red
administrativa a la URL declarada de un servicio ready; no ejecuta ataques ni
demuestra funcionamiento del reto. No usar con URLs de entregas no revisadas.

Para código de terceros, preparar una imagen aislada con las dependencias fijadas
y ejecutar `--docker-image nombre-imagen` en lugar de --trusted-local. Docker es
una opción del validador, independiente del alojamiento del reto web. El adaptador
no instala dependencias y no habilita red. Ver límites en SEGURIDAD.md.

Errores y stdout/stderr del autor no se copian al informe para no revelar respuestas.
Para depurar, el autor puede ejecutar su propio generador en su laboratorio con un
JSON de prueba y directorios vacíos; nunca publicar ese registro.


---

## Documento anterior: CONTRATO_AUTORES.md

# Contrato obligatorio de entrega v2

Una carpeta por reto y versión. Entregar `challenge.json`, `README.md` con entorno y
construcción, y `SOLUCION_PRIVADA.md`. ARTIFACT añade `test_generate.py` y, según el caso,
`generate.py` o las carpetas `public/` y `private/`. Dependencias adicionales en
`requirements.txt` con versiones exactas, mencionadas en `requirements` de metadatos.

El README debe declarar también herramientas ajenas a Python, su versión y pasos de
preparación. No instalarlas al ejecutar. `assets/` es opcional y nunca se publica entero.

## Generados

Implementar `construir_reto(contexto)` en la plantilla. Crear los archivos en
`contexto.output_dir`, guardar la respuesta con `contexto.answer(...)` y retornar
sus nombres. La infraestructura lee stdin, valida campos, calcula hashes, imprime
un JSON y devuelve un código de error sin revelar secretos. El autor puede invocar
un compilador local preparado previamente; la interfaz exterior sigue siendo v2.

No se admiten campos de usuario ni flag. No crear flags personales. No escribir
fuera de los dos directorios asignados. No red ni interacción. No hora actual ni
azar sin semilla. Igual semilla, versión y entorno deben producir iguales bytes.
La plantilla sin implementar falla; readiness también debe cambiar a `ready`.

## Estáticos

Colocar exactamente los archivos declarados en `public/`. Guardar `private/answer.json`
según el esquema. No hace falta generate.py: el validador copia y verifica. Retirar
el instructivo de la plantilla. Implementar una prueba que resuelva el material.

## Prueba del autor

`test_generate.py` recibe por stdin el mismo contexto, con artefactos ya generados.
Debe recuperar la respuesta desde los archivos públicos y comprobar que coincide
con answer.json privado. Si falla, salir con código distinto de cero. Si pasa,
imprimir únicamente `{"tests_passed": 1}` (o un entero mayor). No modificar entradas.
No basta leer la respuesta privada y compararla consigo misma. El equipo revisará
la calidad de la prueba: ninguna herramienta puede demostrar automáticamente que
una prueba escrita por el autor sea honesta o suficiente.

## Solución privada

Incluir objetivo, descubrimiento esperado, procedimiento completo, herramientas,
respuesta común o forma de obtenerla, dificultad y tiempo estimados, dependencias,
entorno fijado, alternativas, vías no intencionales y seguridad/estabilidad.
No empaquetar este documento ni answer.json dentro de un artefacto público.

## Servicios

Entregar URL, salud, gestión externa u opcional por contenedor, estado, aislamiento,
responsable y pasos de despliegue en la documentación. Aportar prueba funcional
de solución para el equipo de infraestructura. Este kit no aprueba automáticamente
servicios por responder HTTP 200. No requiere Docker para web.

## Entrega al organizador

Enviar la carpeta fuente y su informe de validación. El organizador prepara un
bundle privado aprobado. No enviar .venv, cachés, credenciales, bases de datos ni
flags. No cambiar un reto publicado sin subir su versión; el evento congela una
versión por reto. Los autores no implementan usuarios, puntuación ni descargas.


---

## Documento anterior: CONTRIBUTING.md

# Trabajar con CTF Reto Scripts

Este repositorio contiene las herramientas comunes y ejemplos didácticos. El motor
central se mantiene separado. No se necesita modificar este repositorio para crear
cada reto: copia una plantilla a `mis-retos/` y trabaja allí.

## Para autores de retos

1. Instala el kit siguiendo README.md.
2. Crea una carpeta por reto mediante tools/create_challenge.py.
3. Completa metadatos, mecánica, solución y prueba de resolución.
4. Ejecuta tools/validate_challenge.py con tu entrega.
5. Entrega la carpeta completa al organizador por un canal privado.

`mis-retos/`, `retos-evento/`, `work/` y `bundles/` están ignorados por Git para evitar
mezclar trabajo privado del evento con las herramientas compartidas. El informe,
la solución y la respuesta común de cada reto son material organizativo privado.
Los ejemplos de examples/ sí están versionados, incluidas sus soluciones didácticas.

## Para mejorar las herramientas compartidas

Trabaja en una rama y describe el problema y cómo lo verificaste. No cambies el
protocolo v2 sin coordinarlo con el equipo de integración. Antes de proponer cambios:

```text
python -m unittest discover -s tests -v
git diff --check
git status --short
```

No subas entornos virtuales, claves, tokens, bases de datos ni material real del
evento sin revisar. `.gitignore` ayuda, pero no detecta todos los secretos ni
deshace archivos que ya se hayan subido al historial.

Los errores de código ajeno no deben reproducir respuestas o flags en mensajes
públicos. Consulta SEGURIDAD.md antes de ejecutar scripts de terceros.


---

## Documento anterior: ESPECIFICACION_JSON.md

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


---

## Documento anterior: GUIA_POR_CATEGORIA.md

# Elegir modalidad por las necesidades reales

| Categoría | ARTIFACT | SERVICE / atención especial |
|---|---|---|
| forensics | ZIP, PCAP, imagen de disco o memoria sintética | Si requiere un equipo vivo, especificar laboratorio y reset |
| cryptography | Texto, parámetros y datos cifrados/codificados | Oráculos necesitan límites y aislamiento del estado |
| reverse | Ejecutable, bytecode, bibliotecas | Licencias, arquitectura y versión de herramientas fijadas |
| mobile | APK/IPA y recursos preparados | Backend externo si la solución depende de él |
| web | Código fuente para análisis offline, si ese es el objetivo | URL externa válida; Docker opcional, no obligatorio |
| blockchain | Código de contrato, bytecode, trazas exportadas | Red local, RPC, cuentas sintéticas, contrato y alcance de estado |

Un servicio de solo lectura puede compartirse si no contiene credenciales de
otros participantes ni una operación global que complete el reto para todos.
Un servicio mutable necesita revisar cada operación: modificar, vaciar, bloquear,
desplegar o reiniciar puede romper la igualdad. `per-participant` declara un
requisito, no crea automáticamente entornos. `resettable-lab` requiere coordinación;
reiniciar un entorno compartido en mitad de otra resolución no es aceptable.

En blockchain distinguir: contrato compartido de solo lectura, contrato o cadena
por participante, y simulación local. Separar dirección del contrato no basta si
las cuentas, permisos, saldos o resets siguen compartidos. Usar tokens sin valor;
nunca pedir fondos reales. Un RPC no suele contestar GET /health con 200: definir
una sonda JSON-RPC específica en infraestructura y una prueba funcional real.

El modelo B verifica una respuesta común, no automáticamente una transacción ni
el estado on-chain. Si el objetivo requiere demostrar una acción de cada cuenta,
ese verificador y la asociación de cuentas son integración pendiente. No fingir
que canjear una respuesta común demuestra haber ejecutado la acción.

Mobile incluye proyecto Android pendiente de SDK/JDK/Gradle. No hay APK generado.
Web usa example.invalid como marcador. Blockchain incluye Solidity de referencia
y foundry.toml sin despliegue comprobado. Sus estados son REVISIÓN MANUAL.


---

## Documento anterior: INTEGRACION_API.md

# Frontera con la plataforma

Los autores no llaman a la API. Entregan archivos y respuesta común offline.
El motor independiente expondrá catálogo, descargas, canje de respuesta y envío
de flag. La identidad debe venir de autenticación verificable, nunca de user_id
libre enviado por el navegador. La integración concreta se documenta en el
paquete CTF-ENGINE después de completar y probar este kit.

Respuesta común correcta → mostrar flag ya asignada; flag propia → puntos una vez.
Flag ajena → rechazo genérico al participante, auditoría interna con propietario.
El canje y los envíos necesitan controles de frecuencia y transacciones. El flujo
no descubre quién compartió la solución o la respuesta común.


---

## Documento anterior: MIGRACION_V1_V2.md

# Inspección y migración desde kit-ctf.zip

Se leyeron los 10 archivos del ZIP original; se conserva sin modificar.

| Archivo v1 | Decisión v2 |
|---|---|
| core.py | Extraer validación de nombres, tamaños, hashes y reutilización; separar motor y generadores |
| plantilla_autor/generate.py | Sustituir flag/rng/output por contexto público/privado sin usuario |
| plantilla_autor/challenge.json | Esquema estricto v2, modalidades, categorías, puntuación y límites |
| retos/forense-01/generate.py | Reutilizar ZipInfo de fecha fija y comentario; ahora almacena respuesta común |
| retos/forense-01/challenge.json | Metadatos v2 |
| retos/forense-01/SOLUCION_PRIVADA.md | Mantener técnica; actualizar a respuesta común |
| retos/forense-01/test_generate.py | Comprobar igualdad compartida; ya no flags distintas en ZIP |
| test_core.py | Conservar patrones de concurrencia, rollback y estabilidad; dividir pruebas kit/motor |
| CONTRATO_AUTORES.md | Reescribir contrato y añadir servicios/estáticos |
| README.md | Reorganizar responsabilidades y comandos |

V1 tiene una instancia de archivos por (evento, usuario, reto, versión) e introduce
la flag en cada archivo: contradice la igualdad byte por byte. V2 construye una
única versión compartida y mantiene asignaciones personales en una tabla separada.
No migrar automáticamente flags ni instancias v1 a v2. Importar cada reto revisado
como versión nueva y preparar sus archivos comunes. No mezclar protocolos.

Una prueba de v1 que esperaba ZIP diferentes ya no es válida. Las nuevas pruebas
deben probar archivos iguales y flags diferentes, y separar canje de puntuación.


---

## Documento anterior: PENDIENTES_Y_DECISIONES.md

# Decisiones y pendientes

Decidido: contrato v2, Python como envoltorio, un artefacto compartido por versión,
respuesta común privada, seis categorías, modalidades artifact/service y variantes
generated/static. No Docker obligatorio para web. JSON Schema estricto y runtime
instalable compartido evitan versiones divergentes entre autores.

Pendiente de organización: dificultad y puntuación definitivas, categorías de cada
entrega, cuotas mayores, política para archivos comprimidos cifrados, entorno de
construcción fijado por reto, responsable de infraestructura y reglas disciplinarias.

Pendiente de infraestructura: probar runner Docker con cuotas reales, compilar y
analizar APK, compilar/desplegar contrato Solidity, levantar servicios y ejecutar
sus pruebas funcionales. El kit mantiene esos ejemplos en REVISIÓN MANUAL.

El generador Python y sus tests no constituyen prueba matemática de seguridad ni
corrección. La revisión humana de enunciado, dificultad, solución y dependencias
es parte de la aceptación. No hay compatibilidad universal con blockchain mutable.


---

## Documento anterior: PUBLICAR_REPOSITORIO.md

# Publicar el repositorio en GitHub

Nombre propuesto: **ctf-reto-scripts**. Descripción:
"Plantillas, scripts y herramientas para crear y validar retos CTF".

El repositorio local se inicializa en esta carpeta, sin incluir la carpeta hermana
del motor. Crear el remoto en GitHub es el paso posterior; no hace falta hacerlo
antes de preparar los archivos.

## Primera publicación

1. El repositorio público del kit es https://github.com/IEQ369/ctf-reto-scripts.
   Contiene herramientas y ejemplos didácticos; los retos reales del evento se entregan por separado.
2. Déjalo vacío: no agregues README, .gitignore ni licencia desde GitHub, porque
   los archivos de este proyecto ya están preparados.
3. En una terminal abierta en esta carpeta, revisa lo que vas a compartir:

```text
git status --short
git add .
git diff --cached --stat
git diff --cached --check
git commit -m "Preparar kit de scripts para retos CTF"
```

Si Git pide tu identidad, configura tu nombre y el correo que quieras asociar a
los commits con `git config user.name` y `git config user.email`. No inventar una
identidad ni poner contraseñas en esos campos.

4. Conecta la URL que muestra GitHub. Sustituye TU_CUENTA por la cuenta real:

```text
git remote add origin https://github.com/TU_CUENTA/ctf-reto-scripts.git
git push -u origin main
```

GitHub pedirá autenticación mediante el mecanismo configurado en tu computadora.
No escribas tokens en la URL ni los guardes en el repositorio.

5. Comparte el enlace con tus compañeros. Al ser público, pueden clonar o descargar
   el ZIP sin invitación. Concede permisos de escritura solo a quienes mantengan el kit.

No se ha elegido una licencia de reutilización: esa decisión corresponde al equipo.
Que el código sea visible públicamente no equivale a conceder una licencia abierta.


---

## Documento anterior: README.md

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


---

## Documento anterior: RESULTADOS_PRUEBAS.md

# Verificación de la entrega 1

Primera comprobación: 27 de octubre de 2026. Revalidación: 29 de octubre de 2026.
Entorno: Windows, Python 3.13.15, jsonschema 4.26.0.

Comando ejecutado: `python -m unittest discover -s tests -v`.
Resultado: **16 pruebas aprobadas**, sin fallos ni omitidas (5,863 segundos en la revalidación final).

Cobertura: resolución de los ejemplos forense/criptografía/reverse; reproducibilidad;
estático sin generador; plantilla incompleta; categorías y campos inválidos; protocolo
v1 rechazado; separación de directorios; nombres peligrosos; checksums manipulados;
respuesta no reproducible; flag individual en ZIP; material privado en ZIP; solución
faltante; prueba del autor fallida; errores sin secretos; ejecución desactivada por
defecto; servicios y mobile pendientes no aprobados.

Los ejemplos ARTIFACT funcionales quedaron APROBADOS en ejecución local confiable.
Mobile, web y blockchain quedaron REVISIÓN MANUAL. No se compiló un APK, no se
desplegó una cadena, no se levantó un servicio web ni se ejecutó Docker. Linux/macOS
no fueron ensayados aquí. Esas comprobaciones requieren infraestructura adicional.

La aprobación del contrato no sustituye la revisión de calidad del reto ni una
auditoría de seguridad de código de terceros.


---

## Documento anterior: SEGURIDAD.md

# Límites del kit

`subprocess` no aísla. La ejecución local es exclusivamente para código revisado
y se selecciona explícitamente. El filtro de variables de entorno reduce exposición
accidental, pero no impide que código local lea archivos, credenciales o acceda a red.
No ejecutar entregas desconocidas en el servidor del evento ni en un equipo con secretos.

El adaptador Docker monta fuente y kit como solo lectura, dos salidas dedicadas,
elimina capacidades, ejecuta como no-root, deshabilita red, fija memoria/swap, CPU
y cantidad de procesos, usa raíz de solo lectura y elimina el contenedor al vencer
el timeout. Requiere daemon, imagen previamente preparada y permisos de montaje
compatibles. No se ha probado aquí por ausencia de Docker; confirmar comportamiento
en Linux antes de confiar en él. Una VM desechable es otra opción operativa.

Los montajes de salida y logs aún requieren cuota de disco del trabajador. No se
promete aislamiento contra vulnerabilidades del kernel/contenedor. Localmente el
timeout no mata necesariamente procesos nietos: nunca usar ese modo con autores
desconocidos. El tamaño final, cantidad de archivos y checksums se verifican después.

Los bundles son administrativos, no firmas de confianza. Un informe APROBADO no
impide que alguien modifique el bundle después; el motor debe verificar su contenido
al importar y aceptar bundles solo de un canal administrativo revisado.

La inspección busca el patrón CTF{...} en archivos y entradas ZIP/APK, impide incluir
answer.json y SOLUCION_PRIVADA.md con esos nombres, y limita descompresión. Esto no
demuestra ausencia de secretos cifrados, codificados o renombrados. Revisar manualmente
qué se publica; que la respuesta común sea recuperable es el objetivo del reto.
Archivos comprimidos cifrados requieren una política especializada; esta versión
los rechaza en lugar de aprobarlos sin poder inspeccionarlos.

No publicar material personal real. No usar secretos del evento en los ejemplos.
Preservar las claves y la BD del motor con permisos del SO y backups. Windows
requiere ACL adecuadas: chmod no sustituye ACL. El usuario de servicio debe ser
dedicado. Ejecutar API y validación en entornos separados.

Documentación técnica: [JSON Schema](https://python-jsonschema.readthedocs.io/en/stable/validate/),
[restricciones Docker](https://docs.docker.com/engine/containers/resource_constraints/).


## Plantilla estática v2 retirada

Los archivos estáticos pueden ser assets de un generador v3, pero no son por sí solos un reto personalizado. La plantilla anterior queda consultable en el commit 3d46a81.


---

## Referencia anterior de mobile

# Write-up privado — pendiente de adaptación v3

No hay solución individual implementada y probada. Las notas siguientes son referencia
del borrador v2; cualquier respuesta fija debe sustituirse por la flag externa.
No utilizar como evidencia de funcionamiento.

# Solución privada — mobile

## Objetivo y descubrimiento
Recuperar una respuesta común a todos los participantes, sin flags personales.

## Procedimiento completo
Proyecto Android pendiente de compilación. Tras compilar, analizar resources.arsc con JADX/apktool y recuperar el recurso answer_hint: `recurso_android`.
Copiar el APK a public/app-debug.apk, crear private/answer.json y añadir test_generate.py que inspeccione el recurso con una herramienta fijada.
Solo entonces cambiar readiness a ready. No se ha producido ni probado un APK.

## Herramientas y entorno
JDK 17, Android SDK 35, Gradle 8.9 y Android Gradle Plugin 8.7.3; requieren instalación y comprobación externas.. Consultar challenge.json. No se instalan dependencias al generar.

## Dificultad
Introductoria, estimación de 5 a 15 minutos, a validar con estudiantes.

## Alternativas y vías no intencionales
Leer directamente recursos con una herramienta de análisis; es el procedimiento previsto.

## Seguridad y estabilidad
Usar únicamente datos sintéticos. No ejecutar archivos desconocidos fuera del laboratorio.
Las fechas y semillas son fijas; la respuesta privada nunca se distribuye como archivo.
El equipo debe revisar si el mecanismo es suficientemente difícil para el evento.


---

## Referencia anterior de web

# Write-up privado — pendiente de adaptación v3

No hay solución individual implementada y probada. Las notas siguientes son referencia
del borrador v2; cualquier respuesta fija debe sustituirse por la flag externa.
No utilizar como evidencia de funcionamiento.

# Solución privada — web

## Objetivo y descubrimiento
Recuperar una respuesta común a todos los participantes, sin flags personales.

## Procedimiento completo
Referencia pendiente: el equipo web debe implementar la aplicación y documentar cómo recuperar su respuesta común.
No hay servidor funcional en esta entrega. URL example.invalid es un marcador.
Entregar answer.json privado tras verificar la solución y test_service.py contra un entorno de ensayo.

## Herramientas y entorno
Infraestructura externa administrada por el equipo web; Docker no obligatorio.. Consultar challenge.json. No se instalan dependencias al generar.

## Dificultad
Introductoria, estimación de 5 a 15 minutos, a validar con estudiantes.

## Alternativas y vías no intencionales
Revisar acceso accidental a fuentes, backups y paneles de administración antes de publicar.

## Seguridad y estabilidad
Usar únicamente datos sintéticos. No ejecutar archivos desconocidos fuera del laboratorio.
Las fechas y semillas son fijas; la respuesta privada nunca se distribuye como archivo.
El equipo debe revisar si el mecanismo es suficientemente difícil para el evento.


## Revisión de infraestructura conservada

# Comprobaciones pendientes
URL real, responsable de guardia, health check HTTP, prueba funcional de solución,
aislamiento, límites por participante, logs sin secretos, reset, caída y recuperación.
No usar una respuesta en /health. El motor solo muestra la conexión al servicio.


---

## Referencia anterior de blockchain

# Write-up privado — pendiente de adaptación v3

No hay solución individual implementada y probada. Las notas siguientes son referencia
del borrador v2; cualquier respuesta fija debe sustituirse por la flag externa.
No utilizar como evidencia de funcionamiento.

# Solución privada — blockchain

## Objetivo y descubrimiento
Recuperar una respuesta común a todos los participantes, sin flags personales.

## Procedimiento completo
Referencia de infraestructura, no reto desplegado: estudiar Vault.sol y observar que cualquier cuenta puede cambiar unlocked.
Para ensayar: instalar Foundry por separado, iniciar `anvil --chain-id 31337`, compilar y desplegar con herramientas revisadas.
Cada participante requiere un laboratorio/contrato separado si el estado es parte del objetivo.
La respuesta común y una prueba funcional quedan pendientes de definir; no se aprueba esta referencia.

## Herramientas y entorno
Solidity 0.8.24, Foundry/Anvil y cuentas locales sintéticas; no disponibles en el entorno actual.. Consultar challenge.json. No se instalan dependencias al generar.

## Dificultad
Introductoria, estimación de 5 a 15 minutos, a validar con estudiantes.

## Alternativas y vías no intencionales
Si solo se analiza código, convertir a ARTIFACT estático. No confundir conocer una respuesta común con probar una transacción on-chain.

## Seguridad y estabilidad
Usar únicamente datos sintéticos. No ejecutar archivos desconocidos fuera del laboratorio.
Las fechas y semillas son fijas; la respuesta privada nunca se distribuye como archivo.
El equipo debe revisar si el mecanismo es suficientemente difícil para el evento.

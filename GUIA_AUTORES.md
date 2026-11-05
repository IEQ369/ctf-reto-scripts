# Guía de autores

Descarga y prepara el kit siguiendo el [inicio rápido](README.md#inicio-rápido-powershell).
Usa un entorno para las herramientas del kit y otro por reto que tenga dependencias.

## 1. Una carpeta por reto

Cada script implementa exclusivamente
la mecánica de su reto, aunque pueda ejecutarse muchas veces con flags diferentes.

```text
mi-reto/
  challenge.json       identidad, categoría, archivos esperados y requisitos
  generate.py          construye una instancia con la flag recibida
  test_generate.py     resuelve la instancia sin conocer la flag esperada
  README.md            enunciado y requisitos de construcción
  WRITEUP_PRIVADO.md   solución completa para el organizador
  assets/              material base opcional, nunca copiar todo automáticamente
  requirements.txt     dependencias Python opcionales con versiones exactas
  environment.json     versión de Python y herramientas externas (opcional en retos anteriores)
```

Desde la raíz del kit, usando el `$py` preparado en el README:

```powershell
& $py tools/create_challenge.py mis-retos/mi-reto --id mi-reto --category forensics
```

Puedes usar las categorías `forensics`, `cryptography`, `reverse`, `mobile`, `web`
y `blockchain`. La categoría describe el tema; la modalidad describe cómo funciona.
La herramienta copia una plantilla: no diseña la mecánica ni instala herramientas.

## 2. Completar los metadatos

Edita `challenge.json`: título, descripción, dificultad, puntos, requisitos y
`public_files` (lista exacta de archivos que generas). `id` identifica este único
reto; `version` identifica su revisión. El generador no recibe identidades personales.

Conserva `schema_version: 3`. Para archivos usa `delivery.kind: artifact` y
`delivery.build: generated`. Los materiales estáticos sirven de base en `assets/`,
pero el generador debe incorporar la flag de cada ejecución.

Declara `reproducible: true` si puedes repetir los mismos bytes con iguales entradas
y entorno. Fija timestamps, orden de archivos, aleatoriedad y herramientas. Si no
puedes, usa `false` y explica el motivo en `reproducibility_notes`: se exige revisión
manual y no se obtiene aprobación automática.

`source_paths` enumera archivos o carpetas adicionales necesarios para reconstruir
el reto, por ejemplo `["src", "build.sh"]`. Las cinco piezas obligatorias, `assets/`
y `requirements.txt`, `environment.json` y `cleanup.py` se incluyen automáticamente
cuando existen. Declara también binarios, configuraciones y scripts auxiliares que
necesites; por ejemplo `["src", "config", "build/programa.bin"]`. Las bases de datos,
logs y claves sintéticas son assets válidos. Las rutas deben estar dentro del reto.
Si declaras un recurso ausente o excluido, la entrega se rechaza en vez de omitirlo.

No introduzcas claves del servidor en parámetros, fuentes o assets. Las puntuaciones
y pistas son metadatos; este kit no cobra pistas ni concede puntos.

## 3. Programar la mecánica

Completa `construir_reto(contexto)` en `generate.py`:

```python
def construir_reto(contexto):
    # Aplicar aquí TU mecánica, incorporando contexto.flag al desafío.
    # Guardar archivos solo en contexto.output_dir.
    # Devolver sus nombres, por ejemplo ['evidencia.zip'].
    ...
```

`contexto.flag` viene del exterior y debe poder recuperarse resolviendo el reto.
`contexto.rng` es un generador aleatorio reproducible basado en `contexto.seed`.
No generes una nueva flag y no mantengas una flag fija en el código.

Los ejemplos completos están en `examples/forensics`, `examples/cryptography` y
`examples/reverse`. El ejemplo forense guarda la flag en el comentario de un ZIP
con timestamp fijo. Son demostraciones de integración, no retos de dificultad alta.

Puedes usar otras bibliotecas o invocar herramientas de otros lenguajes. Declara sus
versiones y preparación. El wrapper mantiene la misma entrada y salida; no es
obligatorio que todos los autores implementen la misma lógica interna.

## 4. Programar la prueba de resolución

`test_generate.py` recibe por stdin un JSON parecido al del generador, **sin flag**.
Lee `output_dir`, resuelve sus archivos y devuelve por stdout:

```json
{"schema_version": 3, "recovered_flag": "CTF{valor_recuperado}"}
```

Esa salida es privada para el validador. No la imprimas como diagnóstico ni la copies
a un archivo público. El validador compara exactamente, sin quitar espacios ni
cambiar mayúsculas. No basta con comprobar que existe un ZIP o devolver un valor fijo.

Completa el write-up con pasos, herramientas, comandos de resolución y dependencias.
Menciona herramientas como Ghidra; no incluyas sus instaladores en el reto.
El write-up solo se comprueba estructuralmente: una persona revisa su contenido.
No se interpreta como código ni sustituye `test_generate.py`.

## 5. Probar

Antes de probar, completa `environment.json` (las plantillas lo incluyen):

```json
{
  "python": "3.13",
  "system_requirements": [],
  "setup_notes": "Solo Python. No requiere herramientas externas."
}
```

Para reversing con compilador o mobile con SDK, enumera herramientas/versiones en
`system_requirements` y escribe los pasos de instalación en el README del reto.
El kit no instala ni ejecuta esos pasos. Un venv no separa compiladores ni SDK.

Si necesitas bibliotecas, crea `requirements.txt` con una entrada `nombre==versión`
por línea y menciona el archivo en `requirements` de `challenge.json`. Fija también
las dependencias transitivas necesarias para reproducir el entorno. No se admiten
opciones de pip, URLs ni inclusiones de otros requirements en este contrato.

Prepara un entorno NUEVO para este reto después de revisar código y dependencias:

```powershell
& $py tools/prepare_environment.py mis-retos/mi-reto --output work/env-mi-reto --trusted-local
```

Usa `--python RUTA_AL_PYTHON` si requiere otra versión ya instalada. Se admite declarar
`3.13` o una versión exacta como `3.13.15`. No descarga intérpretes. Para paquetes
preparados sin acceso al índice, añade `--wheelhouse RUTA --no-index`.

El entorno instala únicamente bibliotecas del reto. El runtime se facilita mediante
las herramientas del kit, sin imponer sus dependencias al generador. No copies el
venv en la entrega. Si cambias los requisitos, la configuración del entorno, la
ubicación del reto o su versión, prepara un entorno nuevo. Un fallo puede dejar una
carpeta incompleta: el kit no la reutiliza ni sobrescribe.

Cuando la implementación esté lista, cambia `readiness` a `ready` y ejecuta:

```powershell
& $py tools/validate_challenge.py mis-retos/mi-reto --environment work/env-mi-reto --trusted-local
```

El validador genera A, repite A y genera B con dos flags ficticias distintas. Resuelve
las tres, verifica reproducibilidad si está declarada y rechaza la flag B para A.
También revisa tamaños, hashes, archivos declarados y material privado reconocible.

- **APROBADO / salida 0:** superó las comprobaciones automáticas.
- **RECHAZADO / salida 1:** hay un fallo que corregir.
- **REVISIÓN MANUAL / salida 2:** faltan ejecución, infraestructura o revisión especial.

Para producir una instancia concreta:

```powershell
& $py tools/generate_instance.py mis-retos/mi-reto --flag 'CTF{PRUEBA_01}' --output work/mi-reto-a --environment work/env-mi-reto --trusted-local
```

Si tu reto necesita opciones, añade `--parameters opciones.json` al generar, validar
o empaquetar. Ese JSON contiene opciones no secretas; documenta sus campos y valores
en el README del reto. El empaquetador lo usa para validar, no lo añade por sí mismo
a la entrega: declara el archivo en `source_paths` si es necesario para reconstruir.

Cada ejecución necesita un destino nuevo. Si falla, considera inválidos todos sus
archivos; el comando no borra automáticamente material que podría ayudar a depurar.
No vuelvas a usar ese directorio como una instancia válida.

## 6. Entregar al organizador

```powershell
& $py tools/package_challenge.py mis-retos/mi-reto --output bundles/mi-reto.zip --environment work/env-mi-reto --trusted-local
& $py tools/verify_package.py bundles/mi-reto.zip
```

Se valida de nuevo y se empaquetan las fuentes necesarias. Este ZIP es **privado**.
Incluye `challenge/`, `VALIDACION.json` y una advertencia de entrega privada. No incluye
instancias generadas ni flags de validación. No subas soluciones de retos reales al
repositorio público del kit; sus ejemplos sí son material didáctico público.

Un borrador manual puede entregarse con `--allow-manual`, quedando explícitamente
marcado como tal. Esa opción no convierte un reto rechazado en aprobado.

El empaquetador verifica el ZIP antes de entregarlo y muestra `package_sha256`.
El receptor puede comprobar ese valor por un canal confiable y usar
`verify_package.py paquete.zip --sha256 HASH_RECIBIDO`. La revisión estática comprueba
estructura, recursos, rutas, duplicados, límites y CRC sin ejecutar código. Un
`VALIDACION.json` que diga APROBADO no sirve como prueba independiente. Después de
revisar la entrega, el receptor prepara un entorno nuevo y repite la validación.

Checklist de entrega:

- [ ] Generador y solucionador funcionales con flags distintas.
- [ ] README con preparación, versiones y parámetros; write-up completo para revisión humana.
- [ ] Assets, código, configuraciones y limpieza declarados/incluidos.
- [ ] Dependencias probadas en un entorno nuevo, fuera del entorno de otros retos.
- [ ] ZIP final verificado; enviar ese ZIP PRIVADO y su SHA-256 al organizador.
- [ ] Extraer una copia en una carpeta nueva, preparar otro entorno y validar desde esa copia para detectar recursos olvidados.
- [ ] Servicios o compilaciones pendientes identificados como REVISIÓN MANUAL.

El verificador comprueba los recursos declarados, pero no puede deducir del código
todos los archivos que necesita tu mecánica. Esa última prueba desde la entrega
extraída detecta dependencias accidentales de tu carpeta original.

## Categorías especiales

| Categoría | Uso y límite |
|---|---|
| Forense | Archivos y evidencias; adaptar metadatos, PCAP, imágenes o discos exige herramientas y pruebas propias. |
| Criptografía | Incorporar la flag antes de cifrar/codificar; ROT13 solo demuestra el contrato. |
| Reverse | Compilar la flag dentro de la lógica del reto. El ejemplo es bytecode Python dependiente del entorno. |
| Mobile | Una APK puede ser un artefacto generado; requiere SDK/JDK y compilación reproducible. Un backend es un servicio aparte. |
| Web | Usar plantilla `service` si requiere una aplicación activa; no hay Docker obligatorio ni despliegue automático. |
| Blockchain | Usar `blockchain-service` cuando cambie estado; requiere cuentas de prueba, aislamiento y limpieza verificables. |

Crear un borrador web: añadir `--template service` al comando de creación.
Para blockchain: `--template blockchain-service --category blockchain`.
Ambas plantillas fallan deliberadamente hasta implementar los adaptadores.

Los borradores Android y Solidity conservan fuentes de referencia de v2, **todavía
no adaptadas a inyección individual**. No están listos para entregar como retos operativos.

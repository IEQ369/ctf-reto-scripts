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

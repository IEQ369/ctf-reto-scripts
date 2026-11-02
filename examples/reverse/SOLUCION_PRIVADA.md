# Solución privada — reverse

## Objetivo y descubrimiento
Recuperar una respuesta común a todos los participantes, sin flags personales.

## Procedimiento completo
Usar Python 3.13 del entorno fijado. Leer los bytes del .pyc, omitir cabecera de 16 bytes y cargar el código con `marshal.loads`.
Inspeccionar `co_consts` (o `dis.dis`): DATA es un bytes y KEY vale 37. Aplicar XOR 37 a cada byte.
Respuesta: `bytecode_revelado`. La prueba realiza estos pasos sin ejecutar el programa analizado.

## Herramientas y entorno
Python 3.13. Consultar challenge.json. No se instalan dependencias al generar.

## Dificultad
Introductoria, estimación de 5 a 15 minutos, a validar con estudiantes.

## Alternativas y vías no intencionales
Desensamblar con dis; no hay que romper cifrado real. marshal solo se usa con el artefacto sintético confiable de este ejemplo.

## Seguridad y estabilidad
Usar únicamente datos sintéticos. No ejecutar archivos desconocidos fuera del laboratorio.
Las fechas y semillas son fijas; la respuesta privada nunca se distribuye como archivo.
El equipo debe revisar si el mecanismo es suficientemente difícil para el evento.

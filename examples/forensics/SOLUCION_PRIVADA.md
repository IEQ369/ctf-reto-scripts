# Solución privada — forensics

## Objetivo y descubrimiento
Recuperar una respuesta común a todos los participantes, sin flags personales.

## Procedimiento completo
Abrir evidencia.zip con zipfile.ZipFile y leer `.comment.decode('ascii')`.
La respuesta es `archivo_recuperado`. `unzip -z evidencia.zip` también muestra el comentario.

## Herramientas y entorno
Python 3.13. Consultar challenge.json. No se instalan dependencias al generar.

## Dificultad
Introductoria, estimación de 5 a 15 minutos, a validar con estudiantes.

## Alternativas y vías no intencionales
Inspección manual de los bytes; es intencional en estos ejemplos introductorios.

## Seguridad y estabilidad
Usar únicamente datos sintéticos. No ejecutar archivos desconocidos fuera del laboratorio.
Las fechas y semillas son fijas; la respuesta privada nunca se distribuye como archivo.
El equipo debe revisar si el mecanismo es suficientemente difícil para el evento.

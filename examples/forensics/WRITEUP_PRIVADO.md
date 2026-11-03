# Solución privada — forensics

## Objetivo y descubrimiento
Recuperar exactamente la flag recibida por el generador para esta instancia.

## Procedimiento completo
Abrir evidencia.zip con zipfile.ZipFile y leer `.comment.decode('ascii')`.
El comentario contiene la flag individual de esta instancia. `unzip -z evidencia.zip` también muestra el comentario.

## Herramientas y entorno
Python 3.13. Consultar challenge.json. No se instalan dependencias al generar.

## Dificultad
Introductoria, estimación de 5 a 15 minutos, a validar con estudiantes.

## Alternativas y vías no intencionales
Inspección manual de los bytes; es intencional en estos ejemplos introductorios.

## Seguridad y estabilidad
Usar únicamente datos sintéticos. No ejecutar archivos desconocidos fuera del laboratorio.
Los timestamps son deterministas y la flag se incorpora al artefacto. El write-up y el solucionador no se distribuyen al participante.
El equipo debe revisar si el mecanismo es suficientemente difícil para el evento.

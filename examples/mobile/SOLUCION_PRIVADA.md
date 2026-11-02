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

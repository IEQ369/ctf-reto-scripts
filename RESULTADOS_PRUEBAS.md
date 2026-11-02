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

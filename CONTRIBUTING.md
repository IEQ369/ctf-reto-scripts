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

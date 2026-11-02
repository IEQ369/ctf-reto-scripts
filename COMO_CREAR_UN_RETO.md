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

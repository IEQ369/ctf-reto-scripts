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

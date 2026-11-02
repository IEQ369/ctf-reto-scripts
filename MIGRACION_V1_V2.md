# Inspección y migración desde kit-ctf.zip

Se leyeron los 10 archivos del ZIP original; se conserva sin modificar.

| Archivo v1 | Decisión v2 |
|---|---|
| core.py | Extraer validación de nombres, tamaños, hashes y reutilización; separar motor y generadores |
| plantilla_autor/generate.py | Sustituir flag/rng/output por contexto público/privado sin usuario |
| plantilla_autor/challenge.json | Esquema estricto v2, modalidades, categorías, puntuación y límites |
| retos/forense-01/generate.py | Reutilizar ZipInfo de fecha fija y comentario; ahora almacena respuesta común |
| retos/forense-01/challenge.json | Metadatos v2 |
| retos/forense-01/SOLUCION_PRIVADA.md | Mantener técnica; actualizar a respuesta común |
| retos/forense-01/test_generate.py | Comprobar igualdad compartida; ya no flags distintas en ZIP |
| test_core.py | Conservar patrones de concurrencia, rollback y estabilidad; dividir pruebas kit/motor |
| CONTRATO_AUTORES.md | Reescribir contrato y añadir servicios/estáticos |
| README.md | Reorganizar responsabilidades y comandos |

V1 tiene una instancia de archivos por (evento, usuario, reto, versión) e introduce
la flag en cada archivo: contradice la igualdad byte por byte. V2 construye una
única versión compartida y mantiene asignaciones personales en una tabla separada.
No migrar automáticamente flags ni instancias v1 a v2. Importar cada reto revisado
como versión nueva y preparar sus archivos comunes. No mezclar protocolos.

Una prueba de v1 que esperaba ZIP diferentes ya no es válida. Las nuevas pruebas
deben probar archivos iguales y flags diferentes, y separar canje de puntuación.

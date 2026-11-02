# Decisiones y pendientes

Decidido: contrato v2, Python como envoltorio, un artefacto compartido por versión,
respuesta común privada, seis categorías, modalidades artifact/service y variantes
generated/static. No Docker obligatorio para web. JSON Schema estricto y runtime
instalable compartido evitan versiones divergentes entre autores.

Pendiente de organización: dificultad y puntuación definitivas, categorías de cada
entrega, cuotas mayores, política para archivos comprimidos cifrados, entorno de
construcción fijado por reto, responsable de infraestructura y reglas disciplinarias.

Pendiente de infraestructura: probar runner Docker con cuotas reales, compilar y
analizar APK, compilar/desplegar contrato Solidity, levantar servicios y ejecutar
sus pruebas funcionales. El kit mantiene esos ejemplos en REVISIÓN MANUAL.

El generador Python y sus tests no constituyen prueba matemática de seguridad ni
corrección. La revisión humana de enunciado, dificultad, solución y dependencias
es parte de la aceptación. No hay compatibilidad universal con blockchain mutable.

# Responsabilidades y fases

Autor → código, metadatos y solución privada → validador offline → bundle aprobado.
Motor → importa bundle → almacena artefacto común + verificador de respuesta →
asigna flags personales → API para una plataforma independiente.

El motor del evento no necesita ejecutar ni conservar generadores. Durante el
evento, resolver solo lee archivos preparados y realiza operaciones de BD.
Las flags individuales se asignan con anticipación o al registrar tarde una cuenta,
sin reconstruir el reto. Canjear una respuesta no concede puntos; enviar la flag
propia sí. Las respuestas pueden compartirse y este modelo no lo detecta.

Fuentes y bundles contienen secretos y se almacenan fuera del árbol público. El
catálogo público usa una lista explícita de campos. Ni solution ni answer.json ni
metadatos internos de autor o despliegue se sirven como descargas.

Entrega 1: kit completo y probado. Entrega 2: motor por CLI. Entrega 3: API con
autenticación real y adaptable. Entrega 4: pruebas de integración. El directorio
CTF-ENGINE separado documentará su esquema y las decisiones de implementación.

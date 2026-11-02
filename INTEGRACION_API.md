# Frontera con la plataforma

Los autores no llaman a la API. Entregan archivos y respuesta común offline.
El motor independiente expondrá catálogo, descargas, canje de respuesta y envío
de flag. La identidad debe venir de autenticación verificable, nunca de user_id
libre enviado por el navegador. La integración concreta se documenta en el
paquete CTF-ENGINE después de completar y probar este kit.

Respuesta común correcta → mostrar flag ya asignada; flag propia → puntos una vez.
Flag ajena → rechazo genérico al participante, auditoría interna con propietario.
El canje y los envíos necesitan controles de frecuencia y transacciones. El flujo
no descubre quién compartió la solución o la respuesta común.

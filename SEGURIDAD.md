# Límites del kit

`subprocess` no aísla. La ejecución local es exclusivamente para código revisado
y se selecciona explícitamente. El filtro de variables de entorno reduce exposición
accidental, pero no impide que código local lea archivos, credenciales o acceda a red.
No ejecutar entregas desconocidas en el servidor del evento ni en un equipo con secretos.

El adaptador Docker monta fuente y kit como solo lectura, dos salidas dedicadas,
elimina capacidades, ejecuta como no-root, deshabilita red, fija memoria/swap, CPU
y cantidad de procesos, usa raíz de solo lectura y elimina el contenedor al vencer
el timeout. Requiere daemon, imagen previamente preparada y permisos de montaje
compatibles. No se ha probado aquí por ausencia de Docker; confirmar comportamiento
en Linux antes de confiar en él. Una VM desechable es otra opción operativa.

Los montajes de salida y logs aún requieren cuota de disco del trabajador. No se
promete aislamiento contra vulnerabilidades del kernel/contenedor. Localmente el
timeout no mata necesariamente procesos nietos: nunca usar ese modo con autores
desconocidos. El tamaño final, cantidad de archivos y checksums se verifican después.

Los bundles son administrativos, no firmas de confianza. Un informe APROBADO no
impide que alguien modifique el bundle después; el motor debe verificar su contenido
al importar y aceptar bundles solo de un canal administrativo revisado.

La inspección busca el patrón CTF{...} en archivos y entradas ZIP/APK, impide incluir
answer.json y SOLUCION_PRIVADA.md con esos nombres, y limita descompresión. Esto no
demuestra ausencia de secretos cifrados, codificados o renombrados. Revisar manualmente
qué se publica; que la respuesta común sea recuperable es el objetivo del reto.
Archivos comprimidos cifrados requieren una política especializada; esta versión
los rechaza en lugar de aprobarlos sin poder inspeccionarlos.

No publicar material personal real. No usar secretos del evento en los ejemplos.
Preservar las claves y la BD del motor con permisos del SO y backups. Windows
requiere ACL adecuadas: chmod no sustituye ACL. El usuario de servicio debe ser
dedicado. Ejecutar API y validación en entornos separados.

## Qué revisar en este repositorio

- **Secretos y configuración local:** no versionar claves, tokens, bases de datos,
  entornos virtuales ni carpetas de configuración de herramientas. `.gitignore`
  no elimina secretos ya incluidos en commits: si se filtra una credencial, revocarla
  y revisar su historial antes de continuar.
- **Entradas y archivos:** validar el esquema, rechazar campos desconocidos, rutas
  peligrosas y enlaces; comprobar archivos declarados, tamaños y hashes. Esto no
  sustituye el aislamiento al ejecutar código de autores.
- **Salidas públicas:** publicar solo los artefactos declarados; las soluciones
  de los ejemplos son didácticas, pero las soluciones de retos reales del evento
  deben entregarse por un canal privado.
- **Dependencias:** las versiones están fijadas en requirements-lock.txt. Fijar
  versiones no prueba que estén libres de vulnerabilidades. Antes de una entrega,
  se puede ejecutar `python -m pip_audit -r requirements-lock.txt` desde un entorno
  de auditoría con pip-audit instalado. Requiere red y consulta un servicio de avisos;
  no se ejecuta dentro de los generadores. Revisar resultados antes de actualizar.

Este kit no maneja sesiones, cookies, contraseñas, tablas de usuarios ni endpoints
HTTP públicos. Autenticación, autorización, consultas parametrizadas, límites de
intentos, cabeceras HTTP y HTTPS se verifican en el repositorio de la plataforma.
No es necesario agregar esos componentes al generador para cumplir su contrato.

Documentación técnica: [JSON Schema](https://python-jsonschema.readthedocs.io/en/stable/validate/),
[restricciones Docker](https://docs.docker.com/engine/containers/resource_constraints/).

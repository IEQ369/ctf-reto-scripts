# Elegir modalidad por las necesidades reales

| Categoría | ARTIFACT | SERVICE / atención especial |
|---|---|---|
| forensics | ZIP, PCAP, imagen de disco o memoria sintética | Si requiere un equipo vivo, especificar laboratorio y reset |
| cryptography | Texto, parámetros y datos cifrados/codificados | Oráculos necesitan límites y aislamiento del estado |
| reverse | Ejecutable, bytecode, bibliotecas | Licencias, arquitectura y versión de herramientas fijadas |
| mobile | APK/IPA y recursos preparados | Backend externo si la solución depende de él |
| web | Código fuente para análisis offline, si ese es el objetivo | URL externa válida; Docker opcional, no obligatorio |
| blockchain | Código de contrato, bytecode, trazas exportadas | Red local, RPC, cuentas sintéticas, contrato y alcance de estado |

Un servicio de solo lectura puede compartirse si no contiene credenciales de
otros participantes ni una operación global que complete el reto para todos.
Un servicio mutable necesita revisar cada operación: modificar, vaciar, bloquear,
desplegar o reiniciar puede romper la igualdad. `per-participant` declara un
requisito, no crea automáticamente entornos. `resettable-lab` requiere coordinación;
reiniciar un entorno compartido en mitad de otra resolución no es aceptable.

En blockchain distinguir: contrato compartido de solo lectura, contrato o cadena
por participante, y simulación local. Separar dirección del contrato no basta si
las cuentas, permisos, saldos o resets siguen compartidos. Usar tokens sin valor;
nunca pedir fondos reales. Un RPC no suele contestar GET /health con 200: definir
una sonda JSON-RPC específica en infraestructura y una prueba funcional real.

El modelo B verifica una respuesta común, no automáticamente una transacción ni
el estado on-chain. Si el objetivo requiere demostrar una acción de cada cuenta,
ese verificador y la asociación de cuentas son integración pendiente. No fingir
que canjear una respuesta común demuestra haber ejecutado la acción.

Mobile incluye proyecto Android pendiente de SDK/JDK/Gradle. No hay APK generado.
Web usa example.invalid como marcador. Blockchain incluye Solidity de referencia
y foundry.toml sin despliegue comprobado. Sus estados son REVISIÓN MANUAL.

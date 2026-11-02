# Solución privada — blockchain

## Objetivo y descubrimiento
Recuperar una respuesta común a todos los participantes, sin flags personales.

## Procedimiento completo
Referencia de infraestructura, no reto desplegado: estudiar Vault.sol y observar que cualquier cuenta puede cambiar unlocked.
Para ensayar: instalar Foundry por separado, iniciar `anvil --chain-id 31337`, compilar y desplegar con herramientas revisadas.
Cada participante requiere un laboratorio/contrato separado si el estado es parte del objetivo.
La respuesta común y una prueba funcional quedan pendientes de definir; no se aprueba esta referencia.

## Herramientas y entorno
Solidity 0.8.24, Foundry/Anvil y cuentas locales sintéticas; no disponibles en el entorno actual.. Consultar challenge.json. No se instalan dependencias al generar.

## Dificultad
Introductoria, estimación de 5 a 15 minutos, a validar con estudiantes.

## Alternativas y vías no intencionales
Si solo se analiza código, convertir a ARTIFACT estático. No confundir conocer una respuesta común con probar una transacción on-chain.

## Seguridad y estabilidad
Usar únicamente datos sintéticos. No ejecutar archivos desconocidos fuera del laboratorio.
Las fechas y semillas son fijas; la respuesta privada nunca se distribuye como archivo.
El equipo debe revisar si el mecanismo es suficientemente difícil para el evento.

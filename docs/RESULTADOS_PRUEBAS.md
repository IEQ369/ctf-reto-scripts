# Resultados reales — contrato v3

Fecha: 3 de noviembre de 2026, America/La_Paz. Ejecución local en Windows con
Python 3.13.15 y jsonschema 4.26.0. Paquete del kit instalado en modo editable, versión 3.0.0.

## Ejecución final

Desde la raíz del repositorio:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

```text
Ran 33 tests in 74.467s
OK
```

**33 pruebas aprobadas, cero fallos y cero omitidas.** El tiempo corresponde a esta
máquina; no es una estimación de rendimiento del servidor ni de escalabilidad.

La primera ejecución de la suite de 30 pruebas encontró un fallo de codificación
en el canal de error del protocolo directo en Windows. Se corrigió configurando
UTF-8 explícitamente. Se añadieron dos pruebas de JSON estricto y parámetros/entrada
privada de flag. La revisión de empaquetado añadió una prueba para conservar assets
legítimos de forense/crypto/reverse (bases, logs, bytecode y claves sintéticas), sin
bloquearlos por extensión. La ejecución final anterior comprueba todos los cambios.

## Relación con los diez requisitos de la tarea

| Requisito | Comprobación ejecutada |
|---|---|
| Un script representa un reto | CLI y protocolo directo ejecutan un mismo generador con ID/versión constantes; manifiesto identifica ese reto. |
| Acepta flags distintas | Generación de dos instancias con flags ficticias diferentes en tres ejemplos funcionales. |
| Cada instancia contiene su flag | Recuperación desde ZIP, ROT13 y bytecode; inspección explícita de comentarios de ambos ZIP. |
| Cada instancia se resuelve | Solucionador sin flag esperada, ejecutado sobre A, repetición de A y B. |
| Reproducibilidad | Comparación de manifiestos/hashes y bytes del ZIP con iguales entradas; rechazo de generador no determinista. |
| Flag ajena no aceptada | Prueba negativa de igualdad exacta mediante verify_instance; no existe backend de participantes en esta prueba. |
| Contrato estándar | Validación JSON de entrada/salida, esquema v3, identidad del reto, claves duplicadas, NaN y rechazo de entradas v2/usuarios. |
| Privados separados | Rechazo de write-up en ZIP, nombres privados y archivos no declarados; entrega de fuentes excluye .env y material no listado. |
| Defectuosos rechazados | Flag fija, solucionador falso, plantilla incompleta, hashes manipulados, errores, cambios a artefactos y generación no reproducible. |
| CLI sin backend | Crear, generar A/B, validar y empaquetar; extracción del paquete y validación de las fuentes entregadas. |

También se comprobó ausencia de ejecución por defecto, no sobrescritura, estado
del RNG, parámetros personalizados, entrada de flag desde archivo privado, redacción
de errores, categorías pendientes y rechazo de servicio compartido.

## Demostración conservada localmente

Ejecutado con `tools/generate_instance.py`, el mismo `examples/forensics/generate.py`
y la semilla predeterminada `demo-v3`:

| Archivo | Flag ficticia recuperada | Tamaño |
|---|---|---|
| `work/v3-demo-20261103/a/evidencia.zip` | `CTF{A123}` | 153 bytes |
| `work/v3-demo-20261103/b/evidencia.zip` | `CTF{B987}` | 153 bytes |

SHA-256 A: `eb6b8d28d4d04e767d2887362b9366e5620495a4c54d8f8d933e1a1186250905`.

SHA-256 B: `a633f6491b6c35292156e7aa8cc279f147aca32623312c41a4323e22820b2189`.

Se ejecutó `tools/package_challenge.py` y se creó
`bundles/forense-01-v3-demo.zip`, con estado APROBADO. Es una entrega **privada de
fuentes**, no una descarga del participante. Work y bundles son salidas locales
ignoradas por Git; los comandos del README permiten reproducir la demostración.

Se verificó además la validez de todos los esquemas JSON y de los nueve metadatos
de retos/plantillas, y `git diff --check` terminó sin errores.

## Lo que no se probó ni se afirma implementado

- Docker y sus cuotas reales; ejecución de código no confiable aislado.
- Compilación Android o de binarios nativos de reversing.
- Compilación/despliegue Solidity, transacciones o aislamiento real en blockchain.
- Despliegue, resolución y limpieza de un servicio web.
- Integración con backend, autenticación, puntuación o registros de participantes.
- Rendimiento de producción, otros sistemas operativos o auditoría independiente.

Web y blockchain son adaptadores incompletos con contrato explícito; mobile conserva
fuentes pendientes de adaptación/compilación. Permanecen en REVISIÓN MANUAL.
Las pruebas no convierten esa declaración en soporte funcional de esas categorías.

Las 16/36 pruebas del modelo anterior están documentadas en el historial v2 y no se
suman a estos resultados. No se ejecutó ni modificó el motor separado en esta tarea.

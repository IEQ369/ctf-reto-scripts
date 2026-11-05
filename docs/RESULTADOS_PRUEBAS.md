# Resultados reales — contrato v3

## Actualización por capas — 4 de noviembre de 2026

### A. Estado inicial comprobado

Base local: commit `8b51fcc`. Ya existían runtime v3, tres ejemplos funcionales,
generación con flags externas, prueba sin flag esperada, validación de reproducibilidad,
empaquetado de fuentes y 33 tests. La ejecución inicial terminó con **33/33 aprobados
en 22.330 s**. Se conservaron las modificaciones previas y archivos locales ajenos.

### B. Problemas y mejoras

- Faltaba preparar y seleccionar un intérprete/entorno por reto; todos los procesos
  locales utilizaban el Python del kit. Es una carencia para dependencias incompatibles.
- `source_paths` podía omitir silenciosamente recursos bajo carpetas excluidas;
  tampoco se comprobaban todos los recursos declarados al validar la carpeta.
- No existía verificación estática independiente del ZIP recibido.
- La guía no describía el ciclo de preparación por reto y verificación posterior.

### C. Cambios implementados

- `ctf_author/environments.py` y `tools/prepare_environment.py`: venv nuevo, versión
  de intérprete comprobada, instalación explícita de requisitos, pip check y registro
  local de versiones. `--environment` en generar/validar/empaquetar selecciona el
  intérprete del reto y rechaza entornos ajenos o requisitos desactualizados.
- `environment.json` opcional y su esquema, incluido en plantillas nuevas. No se
  añadieron campos al contrato de entrada/salida v3.
- `sources.py` y `dependencies.py`: reglas compartidas de fuentes y requisitos,
  errores por recursos ausentes/excluidos y conservación de binarios, assets,
  configuraciones, environment.json y cleanup.py. No se evalúa semánticamente el write-up.
- `verification.py` y `tools/verify_package.py`: comprobación estática sin extracción
  ni ejecución, con rutas portables, duplicados, enlaces, límites, recursos y CRC.
  SHA-256 externo opcional para detectar reescrituras del ZIP; no se agregó otro manifiesto.
- Empaquetado con comprobación posterior del ZIP antes de guardarlo en su destino;
  no sobrescribe entregas y devuelve su SHA-256.
- Actualización de los cuatro documentos principales y checklist de entrega.

### D. Pruebas realmente ejecutadas

Entorno: Windows, Python 3.13.15, jsonschema 4.26.0. Comandos desde la raíz del kit:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_environments.py -v
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_packages.py -v
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Resultados por capa: **7 pruebas de entornos aprobadas (19.637 s)** y **18 de paquetes
aprobadas (2.431 s)**. La suite conjunta final, que incluye las 33 anteriores:

```text
Ran 58 tests in 41.572s
OK
```

Cero fallos y cero omitidas. Se instalaron dos versiones distintas de una dependencia
de prueba creada localmente, usando wheels y `--no-index`, en dos venv separados.
Ambos generadores/solucionadores comprobaron su versión incompatible y recuperaron
las flags correctas; la dependencia no apareció instalada en el Python principal.
No fue una simulación del runner ni una instalación global de bibliotecas.

Las pruebas del verificador cubren recursos ausentes, reportes de aprobación no
confiables, protocolo incorrecto, rutas peligrosas, nombres ambiguos, entradas
duplicadas, symlinks, CRC corruptos, ZIP reescrito con CRC válido pero SHA distinto,
límites y conservación de material privado. Durante su preparación se ajustaron
dos fixtures para introducir cabeceras adversariales reales: ZipFile en Windows
normalizaba barras/nulos al escribir y eliminaba la condición que queríamos probar.

Piloto completo con código revisado:

1. Preparar entornos nuevos para `mis-retos/forense-04` y `examples/reverse`.
2. Validar y empaquetar con esos intérpretes: ambos APROBADOS.
3. Comprobar ZIP y SHA-256, extraer en carpetas nuevas.
4. Crear otros entornos limpios para las fuentes extraídas, sin dependencias del
   Python principal; repetir validación: ambos APROBADOS.

Evidencia local (ignorada por Git): `work/piloto-entregas/resultados.json`.
Entregas privadas: `bundles/piloto-forense-04.zip` y `bundles/piloto-reverse.zip`.
También se verificó una entrega v3 anterior, los nueve metadatos de plantillas/ejemplos,
todos los esquemas y `git diff --check`.

### E. Compatibilidad

Pasan los ejemplos existentes y el reto forense creado por el usuario sin modificar
sus generadores ni añadir environment.json. Los comandos anteriores siguen funcionando;
`--environment` es opcional. La nueva comprobación rechaza entregas ambiguas o con
recursos declarados ausentes que antes podían pasar; es una corrección estructural.

### F. Pendientes y límites

- Recibir y probar el reto real de Samuel y los de los demás autores. El ejemplo
  de reversing probado pertenece al kit, no es su ejercicio.
- Compiladores/SDK, Android, despliegue web/blockchain y Docker no se probaron.
  Los venv solo separan dependencias Python; no son sandboxes.
- Herramientas externas, transitivas y entorno de construcción deben documentarse
  y fijarse por reto; no hay instalación universal de herramientas del sistema.
- `forense-04` pasa funcionalmente, pero su README seguía siendo la plantilla al
  hacer el piloto: el autor debe completar su documentación y revisión humana.
- El verificador no deduce dependencias ocultas del código ni demuestra autenticidad
  sin un hash externo confiable. Un reporte incluido en el ZIP no certifica resolución.
- No se modificó el motor separado, no se implementó la web y no se hizo commit ni push.

### G. Veredicto

**Listo localmente para un piloto con autores**, con preparación por reto y recepción
verificable. No equivale a declarar todas las categorías listas para producción.
El protocolo v3 se conserva; el siguiente paso de organización es probar entregas
reales de otros autores en sus entornos declarados.

---

## Resultado anterior — 3 de noviembre de 2026

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

# Seguridad y límites

## Material público y privado

- **Participante:** únicamente archivos declarados de su instancia o endpoint aprobado.
- **Organizador:** fuentes, pruebas, write-up y reporte del ZIP de entrega privada.
- **Programa externo:** flag esperada y datos necesarios para su propia administración.

La flag debe existir en la mecánica del desafío: eso es intencional. No debe aparecer
innecesariamente en stdout de generación, errores, nombres de archivo o registros.
El stdout del solucionador contiene la flag recuperada y es estrictamente privado.
Para flags reales, usa stdin del protocolo o `--flag-file`; `--flag` es una comodidad
para datos ficticios y queda visible en historial/argumentos del proceso.

El empaquetador usa una lista de fuentes explícita y excluye cachés/configuraciones
locales conocidas. El ZIP resultante sí contiene soluciones: no distribuirlo a los
participantes. No poner retos reales con sus soluciones en el repositorio público.
Las bases de datos, logs, bytecode y claves sintéticas declaradas como assets son
material válido de retos: el empaquetador no los bloquea por extensión. El autor
debe comprobar que no contienen datos reales ni credenciales operativas.

## Ejecución de código

El modo predeterminado del validador no ejecuta código. `--trusted-local` significa
que confías en el generador y su prueba: ambos pueden acceder a tu equipo. Un
subprocess no es un sandbox. Hay timeout, pero no cuotas duras de memoria/disco ni
garantía de detener procesos descendientes en ejecución local.

`prepare_environment.py` separa las bibliotecas Python por reto. Instalar dependencias
también puede ejecutar código de construcción de paquetes y requiere `--trusted-local`.
Usa código revisado o un entorno aislado externo para entregas desconocidas. El venv
no aísla procesos, red, compiladores ni SDK, y no elimina el acceso a archivos del host.
Las versiones instaladas se registran localmente, pero no se monitorizan cambios
manuales posteriores. No hay garantía de reproducibilidad si las transitivas no se fijan.

El runner Docker opcional limita memoria, CPU, procesos, red, privilegios y montajes.
Requiere imagen preparada con dependencias; no instala herramientas automáticamente.
No fue ejecutado en esta entrega. Hace falta una cuota externa de disco y revisión
del host. No usar servicios de terceros ni credenciales de producción para probar.

## Alcance de las comprobaciones

Se revisan esquema, nombres, enlaces, archivos declarados, tamaños, SHA-256 y
reproducibilidad. Se inspeccionan nombres y límites dentro de ZIP/APK, rechazando
material privado reconocible, rutas peligrosas y enlaces. Los ZIP cifrados no están
admitidos por esta inspección automática. Otros formatos y archivos anidados exigen
revisión específica.

La verificación del ZIP privado de entrega es independiente de la ejecución: no
extrae ni importa código, comprueba todos los CRC por lectura limitada y valida los
recursos declarados. Un tercero puede reescribir un ZIP y actualizar sus CRC; por eso
la comparación SHA-256 requiere un valor recibido por un canal confiable separado.
`VERIFICADO` no afirma que el código sea seguro o que el reto se resuelva. El write-up
se conserva para lectura humana y no se evalúa semánticamente.

No existe detección universal de secretos o write-ups renombrados/ofuscados. Los
límites de archivos se comprueban después de generar y no evitan por sí mismos que
un script llene el disco. La salida de subprocess también requiere cuota externa.

El solucionador recibe archivos sin la flag esperada, pero sigue siendo código del
autor. Podría falsear una prueba o leer otros recursos en modo local: debe revisarse.
APROBADO no certifica ausencia de vulnerabilidades, calidad, dificultad o resistencia
a colaboración. Este repositorio no rastrea participantes ni valida puntuaciones.

## Revisión antes de aceptar un reto

Comprobar enunciado y solución, versiones de herramientas, dependencias fijadas,
contenido público, recuperación de dos flags diferentes y aislamiento de instancias.
En servicios, exigir despliegue, resolución real, limpieza y pruebas de aislamiento.
No aprobar por la mera presencia de un manifiesto o respuesta HTTP 200.

Si falla una generación, no publicar los archivos parciales. El responsable de
ejecución decide su conservación privada o limpieza. Nunca sobrescribir una instancia
previa para intentar corregir otra.

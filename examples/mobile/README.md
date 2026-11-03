# Borrador mobile — REVISIÓN MANUAL

No es un reto operativo v3. Generador y solucionador fallan deliberadamente hasta
implementar la inyección de la flag externa y demostrar la resolución.

Dependencias y entorno: JDK 17, Android SDK 35, Gradle 8.9 y Android Gradle Plugin 8.7.3; requieren instalación y comprobación externas.; instalar el kit antes.

El kit conserva fuentes de referencia cuando existen, pero no compiló Android ni
Solidity, no desplegó servicios y no comprobó aislamiento. No basta cambiar
readiness a ready. Consulta la guía de autores y el contrato de servicios de la raíz.

La modalidad service devuelve un endpoint por instancia y requiere limpieza externa;
no obliga a fabricar archivos ni a usar Docker. Mobile como artifact necesita crear
una APK con la flag recibida antes de poder validarse automáticamente.

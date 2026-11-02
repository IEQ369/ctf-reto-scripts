# Publicar el repositorio en GitHub

Nombre propuesto: **ctf-reto-scripts**. Descripción:
"Plantillas, scripts y herramientas para crear y validar retos CTF".

El repositorio local se inicializa en esta carpeta, sin incluir la carpeta hermana
del motor. Crear el remoto en GitHub es el paso posterior; no hace falta hacerlo
antes de preparar los archivos.

## Primera publicación

1. El repositorio público del kit es https://github.com/IEQ369/ctf-reto-scripts.
   Contiene herramientas y ejemplos didácticos; los retos reales del evento se entregan por separado.
2. Déjalo vacío: no agregues README, .gitignore ni licencia desde GitHub, porque
   los archivos de este proyecto ya están preparados.
3. En una terminal abierta en esta carpeta, revisa lo que vas a compartir:

```text
git status --short
git add .
git diff --cached --stat
git diff --cached --check
git commit -m "Preparar kit de scripts para retos CTF"
```

Si Git pide tu identidad, configura tu nombre y el correo que quieras asociar a
los commits con `git config user.name` y `git config user.email`. No inventar una
identidad ni poner contraseñas en esos campos.

4. Conecta la URL que muestra GitHub. Sustituye TU_CUENTA por la cuenta real:

```text
git remote add origin https://github.com/TU_CUENTA/ctf-reto-scripts.git
git push -u origin main
```

GitHub pedirá autenticación mediante el mecanismo configurado en tu computadora.
No escribas tokens en la URL ni los guardes en el repositorio.

5. Comparte el enlace con tus compañeros. Al ser público, pueden clonar o descargar
   el ZIP sin invitación. Concede permisos de escritura solo a quienes mantengan el kit.

No se ha elegido una licencia de reutilización: esa decisión corresponde al equipo.
Que el código sea visible públicamente no equivale a conceder una licencia abierta.

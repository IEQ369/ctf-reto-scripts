# Ejemplo reverse — un reto, varias instancias

Ejemplo funcional v3. Recupera la flag del material generado; la misma mecánica
se reutiliza con cada flag recibida. No es un generador de retos diferentes.

Desde la raíz del kit, con el entorno activado:

```powershell
python tools/validate_challenge.py examples/reverse --trusted-local
python tools/generate_instance.py examples/reverse --flag 'CTF{A123}' --output work/reverse-a --trusted-local
```

Solo los archivos de esa instancia son públicos. `WRITEUP_PRIVADO.md` explica
la solución para el organizador. Este ejemplo es didáctico y su solución se publica
como parte del kit; no copiar esa práctica para retos reales de la competencia.

Dependencias: Python y el kit instalado. Reversing requiere la misma versión de
Python al generar y analizar el bytecode. Consulta los requisitos en challenge.json.

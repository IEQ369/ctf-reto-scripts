import json
from pathlib import Path
import sys

request = json.load(sys.stdin)
public = Path(request["output_dir"])
private = Path(request["private_dir"])
# Leer los archivos de public, resolverlos y comparar con private/answer.json.
# No basta comprobar que existen ni copiar directamente la respuesta privada.
raise NotImplementedError('Implementar prueba de resolución real')
print(json.dumps({"tests_passed": 1}))

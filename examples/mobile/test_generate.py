import json
from pathlib import Path
import sys

request = json.load(sys.stdin)
public = Path(request['output_dir'])
# Resolver usando SOLO los archivos públicos. No se recibe la flag esperada.
# Al terminar: print(json.dumps({'schema_version': 3, 'recovered_flag': recuperada}))
raise NotImplementedError('Implementar una resolución real')

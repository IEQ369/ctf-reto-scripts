import json
from pathlib import Path
import sys
import codecs

request = json.load(sys.stdin)
public = Path(request["output_dir"])
cipher = json.loads((public/'mensaje.json').read_text())['ciphertext']
recovered = codecs.decode(cipher, 'rot_13')
print(json.dumps({"schema_version": 3, "recovered_flag": recovered}))

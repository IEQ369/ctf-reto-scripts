import json
from pathlib import Path
import sys
import codecs

request = json.load(sys.stdin)
public = Path(request["output_dir"])
private = Path(request["private_dir"])
cipher = json.loads((public/'mensaje.json').read_text())['ciphertext']
answer = codecs.decode(cipher, 'rot_13')
assert answer == json.loads((private/'answer.json').read_text())['answer']
print(json.dumps({"tests_passed": 1}))

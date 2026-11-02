import json
from pathlib import Path
import sys
import importlib.util
import marshal

request = json.load(sys.stdin)
public = Path(request["output_dir"])
private = Path(request["private_dir"])
raw = (public/'verificador.pyc').read_bytes()
assert raw[:4] == importlib.util.MAGIC_NUMBER
code = marshal.loads(raw[16:])
encoded = next(c for c in code.co_consts if isinstance(c, bytes))
key = next(c for c in code.co_consts if type(c) is int)
answer = bytes(x ^ key for x in encoded).decode()
assert answer == json.loads((private/'answer.json').read_text())['answer']
print(json.dumps({"tests_passed": 1}))

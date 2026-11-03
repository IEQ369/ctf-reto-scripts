import json
from pathlib import Path
import sys
import importlib.util
import marshal

request = json.load(sys.stdin)
public = Path(request["output_dir"])
raw = (public/'verificador.pyc').read_bytes()
assert raw[:4] == importlib.util.MAGIC_NUMBER
code = marshal.loads(raw[16:])
encoded = next(c for c in code.co_consts if isinstance(c, bytes))
key = next(c for c in code.co_consts if type(c) is int)
recovered = bytes(x ^ key for x in encoded).decode()
print(json.dumps({"schema_version": 3, "recovered_flag": recovered}))

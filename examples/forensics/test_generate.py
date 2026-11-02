import json
from pathlib import Path
import sys
import zipfile

request = json.load(sys.stdin)
public = Path(request["output_dir"])
private = Path(request["private_dir"])
with zipfile.ZipFile(public / 'evidencia.zip') as archive:
    assert archive.testzip() is None
    recovered = archive.comment.decode('ascii')
assert recovered == json.loads((private/'answer.json').read_text())['answer']
print(json.dumps({"tests_passed": 1}))

import json
from pathlib import Path
import sys
import zipfile

request = json.load(sys.stdin)
public = Path(request["output_dir"])
with zipfile.ZipFile(public / 'evidencia.zip') as archive:
    assert archive.testzip() is None
    recovered = archive.comment.decode('ascii')
print(json.dumps({"schema_version": 3, "recovered_flag": recovered}))

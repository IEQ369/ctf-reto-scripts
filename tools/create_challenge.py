"""Copia una plantilla, sin sobrescribir carpetas existentes."""
import argparse
import json
from pathlib import Path
import shutil
from ctf_author.validation import schema_check

p = argparse.ArgumentParser()
p.add_argument('destination')
p.add_argument('--template', choices=['artifact-generated','artifact-static','service','blockchain-service'], required=True)
p.add_argument('--id', required=True)
p.add_argument('--category', choices=['forensics','cryptography','reverse','mobile','web','blockchain'], required=True)
a = p.parse_args()
template = Path(__file__).resolve().parent.parent / 'templates' / a.template
spec = json.loads((template/'challenge.json').read_text(encoding='utf-8'))
spec.update(id=a.id, category=a.category, title=a.id)
schema_check(spec, 'challenge')
destination = Path(a.destination)
shutil.copytree(template, destination)
(destination/'challenge.json').write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding='utf-8')
print('Plantilla creada. Completar mecánica, solución y prueba; después cambiar readiness a ready.')

from ctf_author.runtime import run
import codecs
import json


def construir_reto(contexto):
    answer = contexto.flag
    cipher = codecs.encode(answer, 'rot_13')
    (contexto.output_dir/'mensaje.json').write_text(json.dumps({'method':'ROT13','ciphertext':cipher}, sort_keys=True), encoding='utf-8')
    return ['mensaje.json']

if __name__ == "__main__":
    run(construir_reto)

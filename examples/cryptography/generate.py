from ctf_author.runtime import run
import codecs
import json


def construir_reto(contexto):
    answer = 'el_desplazamiento_es_trece'
    cipher = codecs.encode(answer, 'rot_13')
    (contexto.output_dir/'mensaje.json').write_text(json.dumps({'method':'ROT13','ciphertext':cipher}, sort_keys=True), encoding='utf-8')
    contexto.answer(answer, strip=True, casefold=True)
    return ['mensaje.json']

if __name__ == "__main__":
    run(construir_reto)

from ctf_author.runtime import run
import py_compile


def construir_reto(contexto):
    answer = 'bytecode_revelado'
    encoded = bytes(value ^ 37 for value in answer.encode())
    source = contexto.output_dir / 'temporal.py'
    source.write_text('DATA = ' + repr(encoded) + '\nKEY = 37\ndef check(value):\n    return bytes(x ^ KEY for x in value.encode()) == DATA\n', encoding='utf-8')
    py_compile.compile(str(source), cfile=str(contexto.output_dir/'verificador.pyc'), dfile='verificador.py', doraise=True, invalidation_mode=py_compile.PycInvalidationMode.CHECKED_HASH)
    source.unlink()
    contexto.answer(answer)
    return ['verificador.pyc']

if __name__ == "__main__":
    run(construir_reto)

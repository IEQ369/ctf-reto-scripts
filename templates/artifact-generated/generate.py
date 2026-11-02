from ctf_author.runtime import run


def construir_reto(contexto):
    # Crear archivos únicamente dentro de contexto.output_dir.
    # Usar contexto.rng si necesitas variación reproducible.
    # Guardar la respuesta común con contexto.answer('respuesta', strip=False, casefold=False).
    # Retornar, por ejemplo, ['evidencia.zip'].
    raise NotImplementedError('Implementar aquí la mecánica del reto')

if __name__ == "__main__":
    run(construir_reto)

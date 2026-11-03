from ctf_author.runtime import run


def construir_reto(contexto):
    # Este archivo implementa UN reto. No crear flags: usar contexto.flag.
    # Escribir solo archivos para el participante en contexto.output_dir.
    # Assets y herramientas propias pueden implementar cualquier mecánica.
    # Usar contexto.rng si necesitas aleatoriedad reproducible.
    # Devolver nombres, por ejemplo: ['evidencia.zip'].
    raise NotImplementedError('Inyectar flag, compilar APK y demostrar resolución con SDK fijado')


if __name__ == '__main__':
    run(construir_reto)

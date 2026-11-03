from ctf_author.runtime import run
import zipfile


def construir_reto(contexto):
    answer = contexto.flag
    with zipfile.ZipFile(contexto.output_dir / 'evidencia.zip', 'w') as archive:
        entry = zipfile.ZipInfo('nota.txt', date_time=(2026,1,1,0,0,0))
        archive.writestr(entry, 'Revisa también el contenedor.'.encode('utf-8'))
        archive.comment = answer.encode('ascii')
    return ['evidencia.zip']

if __name__ == "__main__":
    run(construir_reto)

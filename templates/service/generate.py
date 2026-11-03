"""Adaptador de UNA instancia de servicio; contrato descrito en CONTRATO_TECNICO.md.
No se debe publicar una flag ni compartir estado mutable entre instancias.
El kit no implementa despliegue: completar y probar con el integrador.
"""
from ctf_author.runtime import run_service


def construir_reto(contexto):
    # Recibir contexto.flag; inyectarla por un canal privado al servicio aislado.
    # Devolver endpoint público e identificador opaco de instancia, sin secretos.
    # Implementar limpieza idempotente en cleanup.py (contrato técnico).
    raise NotImplementedError('Requiere infraestructura y prueba funcional externas')


if __name__ == '__main__':
    run_service(construir_reto)

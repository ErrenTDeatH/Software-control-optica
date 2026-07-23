"""
utils/__init__.py — Punto de entrada del paquete utils
"""

# WhatsApp
from utils.whatsapp import (
    wa_link,
    generar_msg_factura,
    generar_msg_hc,
    generar_msg_hc_lc,
    generar_msg_indicaciones,
    generar_msg_indicaciones_lc,
)

# PDF
from utils.pdf import (
    _s,
    generar_pdf_historia,
    generar_pdf_historia_lc,
    generar_pdf_ticket,
    generar_pdf_venta,
)

__all__ = [
    "wa_link",
    "generar_msg_factura",
    "generar_msg_hc",
    "generar_msg_hc_lc",
    "generar_msg_indicaciones",
    "generar_msg_indicaciones_lc",
    "_s",
    "generar_pdf_historia",
    "generar_pdf_historia_lc",
    "generar_pdf_ticket",
    "generar_pdf_venta",
]

# -*- coding: utf-8 -*-
"""
utils/whatsapp.py — Funciones de mensajería WhatsApp para Happy Vision
"""

import urllib.parse


def wa_link(numero: str, mensaje: str) -> str:
    """Genera link para abrir WhatsApp Web con un mensaje preescrito."""
    num = numero.replace(" ", "").replace("+", "").replace("-", "")
    if num.startswith("0"):
        num = "593" + num[1:]
    return f"https://wa.me/{num}?text={urllib.parse.quote(mensaje)}"


def generar_msg_factura(row) -> str:
    """Genera el mensaje WhatsApp para una factura/trabajo."""
    estado = row.get('estado', '')
    return (
        f"*Happy Vision - Detalle de su Servicio*\n\n"
        f"Paciente: {row.get('paciente', '')}\n"
        f"Fecha: {row.get('fecha', '')}\n"
        f"Tipo de Lente: {row.get('tipo_lente', '')}\n"
        f"Laboratorio: {row.get('laboratorio', '')}\n\n"
        f"Total: ${row.get('precio_total', 0):.2f}\n"
        f"Abonado: ${row.get('abono', 0):.2f}\n"
        f"Saldo Pendiente: ${row.get('saldo_pendiente', 0):.2f}\n"
        f"Estado: {estado}\n\n"
        f"Para consultas: +593 96 324 1158 | Happy Vision"
    )


def generar_msg_hc(row, paciente_info) -> str:
    """Genera el mensaje WhatsApp para compartir una historia clínica (resumen)."""
    return (
        f"*Happy Vision - Resumen de Consulta Optometrica*\n\n"
        f"Paciente: {paciente_info.get('nombre', '')}\n"
        f"Fecha: {row.get('fecha', '')}\n"
        f"Motivo: {row.get('motivo', '')}\n\n"
        f"*Rx Final:*\n"
        f"OD: {row.get('rx_od', '')}\n"
        f"OI: {row.get('rx_oi', '')}\n\n"
        f"Recomendaciones:\n{row.get('recomendaciones', '')}\n\n"
        f"Para consultas: +593 96 324 1158 | Happy Vision"
    )


def generar_msg_indicaciones(row, paciente_info) -> str:
    """Genera el mensaje WhatsApp con indicaciones médicas y tratamiento (colirios, etc.)."""
    recom = row.get('recomendaciones', '') or row.get('observaciones', '')
    if not str(recom).strip() or str(recom).strip().lower() in ('nan', 'none', ''):
        recom = 'Ver indicaciones de su optometrista.'
    control = row.get('meses_proximo_control', '')
    control_txt = f"\nProximo control: en {control} mes(es)." if control else ""
    return (
        f"*Happy Vision - Indicaciones Medicas*\n\n"
        f"Paciente: {paciente_info.get('nombre', '')}\n"
        f"Consulta: {row.get('fecha', '')}\n\n"
        f"*Indicaciones / Tratamiento:*\n{recom}"
        f"{control_txt}\n\n"
        f"Consultas: +593 96 324 1158 | Happy Vision"
    )

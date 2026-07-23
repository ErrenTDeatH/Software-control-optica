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

def generar_msg_indicaciones_lc(row, paciente_info) -> str:
    """Genera el mensaje WhatsApp con indicaciones para Lentes de Contacto."""
    recom = row.get('recomendaciones', '') or row.get('lc_observaciones', '')
    if not str(recom).strip() or str(recom).strip().lower() in ('nan', 'none', ''):
        recom = 'Ver indicaciones detalladas en su certificado.'
    
    control = row.get('lc_proximo_control', '')
    control_txt = f"\nPróximo control: {control}" if control else ""
    
    solucion = row.get('lc_solucion_final', '')
    solucion_txt = f"\nSolución recomendada: {solucion}" if solucion else ""
    
    return (
        f"👁️ *Happy Vision - Indicaciones Lentes de Contacto*\n\n"
        f"Estimado/a *{paciente_info.get('nombre', '')}*, a continuación las indicaciones de su adaptación del *{row.get('fecha', '')}*:\n\n"
        f"*Indicaciones / Cuidados:*\n{recom}"
        f"{solucion_txt}"
        f"{control_txt}\n\n"
        f"Ante cualquier duda o molestia, suspenda el uso y comuníquese con nosotros.\n"
        f"📍 *Happy Vision* | 📞 +593 96 324 1158"
    )


def generar_msg_hc_lc(row, paciente_info) -> str:
    """Genera el mensaje WhatsApp para compartir un certificado de Lentes de Contacto."""
    return (
        f"*Happy Vision - Certificado de Lentes de Contacto*\n\n"
        f"Estimado/a *{paciente_info.get('nombre', '')}*, adjunto encontrará su certificado visual de la adaptación de Lentes de Contacto realizada el {row.get('fecha', '')}.\n\n"
        f"*Lente Definitivo:*\n"
        f"OD: {row.get('lc_final_od', '')}\n"
        f"OI: {row.get('lc_final_oi', '')}\n"
        f"Marca: {row.get('lc_marca_final', '')}\n\n"
        f"Por favor, envíenos su correo electrónico si prefiere recibirlo por esa vía, o envíenos un '+', y le enviaremos el documento en formato PDF por aquí.\n\n"
        f"📍 *Happy Vision* | 📞 +593 96 324 1158"
    )


def generar_msg_recordatorio_cita(nombre_paciente: str, fecha: str, hora: str) -> str:
    """Genera mensaje para recordar una cita agendada."""
    return (
        f"👋 Hola *{nombre_paciente}*,\n\n"
        f"Te recordamos tu cita programada en *Happy Vision*:\n"
        f"📅 *Fecha:* {fecha}\n"
        f"⏰ *Hora:* {hora}\n\n"
        f"Por favor, confírmanos tu asistencia respondiendo a este mensaje.\n"
        f"¡Que tengas un excelente día! 👁️✨"
    )


def generar_msg_orden_lista(nombre_paciente: str) -> str:
    """Genera mensaje para avisar que la orden de trabajo está lista."""
    return (
        f"🎉 Hola *{nombre_paciente}*,\n\n"
        f"Te informamos que tus lentes ya se encuentran listos para retirar en nuestra sucursal de *Happy Vision*.\n\n"
        f"📍 Puedes acercarte a retirarlos en nuestro horario habitual.\n"
        f"¡Muchas gracias por tu confianza! 👓✨"
    )

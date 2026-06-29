"""
utils/pdf.py — Generación de PDFs para Happy Vision
Certificado Visual + Informe Médico
"""

import io
import os
from datetime import date, datetime
import pandas as pd
from fpdf import FPDF


# ══════════════════════════════════════════════════════════════
# HELPER: TEXTO SEGURO PARA PDF
# ══════════════════════════════════════════════════════════════
def _s(texto) -> str:
    """Convierte texto a Latin-1 seguro para fpdf (Helvetica), eliminando emojis."""
    if texto is None:
        return ""
    t = str(texto)
    # Latin-1 soporta ñ, tildes y caracteres del español
    return t.encode("latin-1", errors="ignore").decode("latin-1")


# ══════════════════════════════════════════════════════════════
# CERTIFICADO VISUAL (PDF)
# ══════════════════════════════════════════════════════════════
def generar_pdf_historia(row: dict, paciente_info: dict, opto: dict) -> bytes:
    """Genera el Certificado Visual PDF usando fpdf estándar."""
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(18, 10, 18)

    # ─ LOGO ────────────────────────────────────────────────────
    logo_path = None
    for cand in ["logo.png", "logo.jpg", "logo.jpeg"]:
        if os.path.exists(cand):
            logo_path = cand
            break

    if logo_path:
        try:
            watermark_path = logo_path
            try:
                from PIL import Image
                img = Image.open(logo_path).convert("RGBA")
                r, g, b, a = img.split()
                a_faded = a.point(lambda p: p * 0.10)
                img.putalpha(a_faded)
                bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
                bg.paste(img, (0, 0), img)
                watermark_path = "logo_watermark_temp.png"
                bg.convert("RGB").save(watermark_path, format="PNG")
            except Exception:
                pass

            pdf.image(watermark_path, x=5, y=40, w=200)

            header_path = logo_path
            try:
                from PIL import Image, ImageChops
                img_head = Image.open(logo_path).convert("RGBA")
                bbox = img_head.split()[-1].getbbox()
                if bbox:
                    img_head = img_head.crop(bbox)
                bg_white = Image.new("RGBA", img_head.size, (255, 255, 255, 255))
                diff = ImageChops.difference(img_head, bg_white)
                bbox2 = diff.getbbox()
                if bbox2:
                    img_head = img_head.crop(bbox2)
                final_bg = Image.new("RGBA", img_head.size, (255, 255, 255, 255))
                final_bg.paste(img_head, (0, 0), img_head)
                header_path = "logo_header_temp.png"
                final_bg.convert("RGB").save(header_path, format="PNG")
            except Exception:
                pass

            pdf.image(header_path, x=82.5, y=3, w=45)
            pdf.set_y(30)
        except Exception:
            pdf.set_y(20)
    else:
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(0, 160, 180)
        pdf.cell(0, 10, "HAPPY VISION", ln=True, align="C")
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, "Tu optica amiga", ln=True, align="C")

    # ─ LÍNEA + TÍTULO ──────────────────────────────────────────
    pdf.set_draw_color(0, 160, 180)
    pdf.set_line_width(1)
    pdf.line(18, pdf.get_y(), 192, pdf.get_y())
    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 12, "CERTIFICADO VISUAL", ln=True, align="C")
    pdf.ln(3)

    # ─ DATOS PACIENTE ──────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(22, 6, "NOMBRE:", ln=False)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(81, 6, _s(str(paciente_info.get("nombre", "")).upper()), ln=False)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(18, 6, "CEDULA:", ln=False)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, _s(paciente_info.get("identificacion", "")), ln=True)

    # Calcular edad real desde fecha_nacimiento
    edad_display = str(paciente_info.get('edad', ''))
    fnac_raw = paciente_info.get('fecha_nacimiento', '')
    if fnac_raw:
        try:
            _fnac = date.fromisoformat(str(fnac_raw)[:10])
            _hoy = date.today()
            edad_display = str(_hoy.year - _fnac.year - ((_hoy.month, _hoy.day) < (_fnac.month, _fnac.day)))
        except Exception:
            pass

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(14, 6, "EDAD:", ln=False)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(28, 6, _s(f"{edad_display} años"), ln=False)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(17, 6, "FECHA:", ln=False)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(44, 6, _s(row.get("fecha", "")), ln=False)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(24, 6, "TELEFONO:", ln=False)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, _s(paciente_info.get("telefono", "")), ln=True)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(50, 6, "MOTIVO DE LA CONSULTA: ", ln=False)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, _s(row.get("motivo", "")), ln=True)
    pdf.ln(3)

    # ─ AGUDEZA VISUAL ──────────────────────────────────────────
    def _av(v):
        v = _s(v).strip()
        if not v:
            return " "
        if "20/" in v:
            return v
        return f"20/{v}"

    def print_av_double_column(sc_lej_od, sc_lej_oi, sc_cer_od, sc_cer_oi,
                               cc_lej_od, cc_lej_oi, cc_cer_od, cc_cer_oi):
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(90, 5, "AGUDEZA VISUAL S/C", ln=False)
        pdf.cell(90, 5, "AGUDEZA VISUAL C/C", ln=True)
        pdf.ln(1)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(90, 5, "LEJOS:", ln=False)
        pdf.cell(90, 5, "LEJOS:", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(90, 5, f"O.D.: {_av(sc_lej_od)}", ln=False)
        pdf.cell(90, 5, f"O.D.: {_av(cc_lej_od)}", ln=True)
        pdf.cell(90, 5, f"O.I.: {_av(sc_lej_oi)}", ln=False)
        pdf.cell(90, 5, f"O.I.: {_av(cc_lej_oi)}", ln=True)
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(90, 5, "CERCA:", ln=False)
        pdf.cell(90, 5, "CERCA:", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(90, 5, f"O.D. {_s(sc_cer_od)}", ln=False)
        pdf.cell(90, 5, f"O.D. {_s(cc_cer_od)}", ln=True)
        pdf.cell(90, 5, f"O.I. {_s(sc_cer_oi)}", ln=False)
        pdf.cell(90, 5, f"O.I. {_s(cc_cer_oi)}", ln=True)
        pdf.ln(3)

    # ─ TABLAS RX ───────────────────────────────────────────────
    def draw_rx_table(titulo, od_str, oi_str, is_refraccion=False):
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, _s(titulo), ln=True)
        pdf.ln(1)

        def parse_str(s):
            s_val = str(s)
            pts = s_val.split("|") if "|" in s_val else s_val.split()
            while len(pts) < 10:
                pts.append("")
            return [x.strip() if x.strip() not in ("", "None", "nan", "-") else "---" for x in pts]

        pod = parse_str(od_str)
        poi = parse_str(oi_str)

        pdf.set_font("Helvetica", "B", 8)
        if is_refraccion:
            hdrs = ["RX", "ESF", "CYL", "EJE", "ADD", "DNP", "ALT", "D.P.", "A/V"]
            wcol = [22, 19, 19, 19, 19, 19, 19, 19, 19]
        else:
            hdrs = ["RX", "ESF", "CYL", "EJE", "ADD"]
            wcol = [34, 35, 35, 35, 35]

        pdf.set_fill_color(240, 245, 248)
        pdf.set_draw_color(180, 190, 200)
        pdf.set_line_width(0.2)
        for i, h in enumerate(hdrs):
            pdf.cell(wcol[i], 8, h, border=1, align="C", fill=True, ln=(i == len(hdrs) - 1))

        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(wcol[0], 8, "OD", border=1, align="C")
        pdf.set_font("Helvetica", "", 8)
        for i in range(1, len(hdrs)):
            pdf.cell(wcol[i], 8, pod[i - 1] if (i - 1) < len(pod) else "", border=1, align="C")
        pdf.ln()

        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(wcol[0], 8, "OI", border=1, align="C")
        pdf.set_font("Helvetica", "", 8)
        for i in range(1, len(hdrs)):
            pdf.cell(wcol[i], 8, poi[i - 1] if (i - 1) < len(poi) else "", border=1, align="C")
        pdf.ln()
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.2)

    print_av_double_column(
        row.get("lenso_av_lej_od"), row.get("lenso_av_lej_oi"),
        row.get("lenso_av_cer_od"), row.get("lenso_av_cer_oi"),
        row.get("rx_av_lej_od"),   row.get("rx_av_lej_oi"),
        row.get("rx_av_cer_od"),   row.get("rx_av_cer_oi"),
    )
    draw_rx_table("LENSOMETRIA (RX EN USO)", row.get("lenso_od"), row.get("lenso_oi"), is_refraccion=False)
    draw_rx_table("REFRACCION (RX ACTUAL)",  row.get("rx_od"),    row.get("rx_oi"),    is_refraccion=True)
    pdf.ln(5)

    # ─ EXAMEN CLÍNICO ─────────────────────────────────────────
    def _clean(val):
        v = str(val).strip()
        if v.lower() in ("", "nan", "none", "null"):
            return ""
        return v

    def clinico(lbl, val):
        v = _clean(val)
        if v:
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(55, 7, _s(lbl) + ":", ln=False)
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 7, _s(v), ln=True)

    clinico("ESTADO MUSCULAR",  row.get("estado_muscular"))
    clinico("SEGMENTO EXTERNO", row.get("seg_externo"))
    clinico("TEST DE COLORES",  row.get("test_colores"))
    clinico("DIAGNOSTICO",      row.get("diagnostico"))

    lentes_val = _clean(str(row.get("necesita_lentes", "")))
    if lentes_val:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(65, 7, "PACIENTE NECESITA LENTES:", ln=False)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 7, lentes_val.upper(), ln=True)

    color_val = _clean(str(row.get("test_color", "")))
    if color_val:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(55, 7, "TEST DE COLOR:", ln=False)
        pdf.set_font("Helvetica", "", 10)
        display_color = "SE DETECTA DALTONISMO" if "dalton" in color_val.lower() else "NORMAL"
        pdf.cell(0, 7, display_color, ln=True)

    pdf.ln(2)

    # ─ OBSERVACIONES ──────────────────────────────────────────────────
    obs_raw = row.get("observaciones", "")
    obs = _s(_clean(obs_raw))
    if obs:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(42, 7, "OBSERVACIONES:", ln=False)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 7, obs)
        pdf.ln(1)

    # ─ RECOMENDACIONES ────────────────────────────────────────────────
    rec_raw = row.get("recomendaciones", "")
    rec = _s(_clean(rec_raw))
    if rec:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(42, 7, "RECOMENDACIONES:", ln=False)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 7, rec)
        pdf.ln(1)

    # ─ PROXIMO CONTROL ───────────────────────────────────────────────
    proximo_control_raw = row.get("meses_proximo_control", "")
    proximo_control = _s(_clean(proximo_control_raw))
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(42, 7, "PROXIMO CONTROL:", ln=False)
    
    if proximo_control:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(30, 30, 30) # Negro normal
        pdf.multi_cell(0, 7, proximo_control)
    else:
        pdf.set_font("Helvetica", "I", 10)
        pdf.set_text_color(255, 0, 0) # Rojo si falta
        pdf.multi_cell(0, 7, "PROXIMO CONTROL: (No registrado - Edite la historia)")
        
    pdf.set_text_color(30, 30, 30) # Volver al color base
    pdf.ln(2)

    # ─ FIRMA Y PIE DE PÁGINA (posición dinámica) ──────────────
    firma_path = f"firma_{opto.get('username', '')}.png"
    if not os.path.exists(firma_path):
        firma_path = "firma.png"

    espacio_firma = 35
    y_firma_min   = 257 - espacio_firma  # ~222mm
    y_actual      = pdf.get_y()
    y_firma       = max(y_actual + 6, y_firma_min)
    if y_firma + espacio_firma > 277:
        y_firma = 277 - espacio_firma

    # Intentar cargar firma desde Base64 (Base de datos) o archivo local
    firma_base64 = opto.get("firma_base64")
    import base64 as _b64
    if firma_base64:
        try:
            with open("temp_firma.png", "wb") as f:
                f.write(_b64.b64decode(firma_base64))
            pdf.image("temp_firma.png", x=77, y=y_firma, w=55, h=16)
        except Exception: 
            if os.path.exists(firma_path): pdf.image(firma_path, x=77, y=y_firma, w=55, h=16)
    elif os.path.exists(firma_path):
        try:
            pdf.image(firma_path, x=77, y=y_firma, w=55, h=16)
        except Exception:
            pass

    y_linea = y_firma + 17
    pdf.set_y(y_linea)
    pdf.set_draw_color(80, 80, 80)
    pdf.set_line_width(0.4)
    pdf.line(65, pdf.get_y(), 145, pdf.get_y())
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 5, _s(opto.get("nombre", "")), ln=True, align="C")
    pdf.cell(0, 5, _s(opto.get("cargo", "OPTOMETRA")).upper(), ln=True, align="C")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 5, f"Reg.: {_s(opto.get('registro', ''))}  |  Tel.: {_s(opto.get('telefono', ''))}", ln=True, align="C")

    # ─ DIRECCIÓN DE LA SUCURSAL DINÁMICA ────────────────
    pdf.ln(1)
    sucursal_pdf = row.get("sucursal", "Matriz")
    if not sucursal_pdf:
        sucursal_pdf = "Matriz"
        
    # Cargar direcciones desde DB
    from database import cargar_sucursales
    df_s = cargar_sucursales()
    dir_sucursal = "Dirección no registrada"
    
    if not df_s.empty:
        match_suc = df_s[df_s["nombre"] == sucursal_pdf]
        if not match_suc.empty:
            dir_sucursal = match_suc.iloc[0]["direccion"]
    
    
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 4, _s(f"Atendido en: {sucursal_pdf} - {dir_sucursal}"), ln=True, align="C")
    buf = io.BytesIO()
    raw = pdf.output(dest='S')
    if isinstance(raw, (bytes, bytearray)):
        return bytes(raw)
    buf.write(raw.encode("latin-1") if isinstance(raw, str) else bytes(raw))
    return buf.getvalue()

# ══════════════════════════════════════════════════════════════
# TICKET DE VENTA / ÓRDEN DE TRABAJO
# ══════════════════════════════════════════════════════════════
def generar_pdf_ticket(orden: dict, sucursal_info: dict = None) -> bytes:
    """Genera un comprobante de pago / ticket de venta para el cliente."""
    pdf = FPDF(orientation="P", unit="mm", format="A5") # Formato A5 para tickets
    pdf.add_page()
    pdf.set_margins(10, 10, 10)
    
    # Logo si existe
    logo_path = "logo.png" if os.path.exists("logo.png") else None
    if logo_path:
        pdf.image(logo_path, x=58, y=5, w=30)
        pdf.ln(25)
    else:
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "HAPPY VISION", ln=True, align="C")
        pdf.ln(5)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, _s(f"ORDEN DE TRABAJO #{orden['id']}"), ln=True, align="C")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 5, _s(f"Fecha: {pd.to_datetime(orden['creado_el']).strftime('%Y-%m-%d %H:%M')}"), ln=True, align="C")
    pdf.ln(5)

    # Datos del Cliente
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8, " DATOS DEL CLIENTE", ln=True, fill=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(2)
    pdf.cell(0, 6, _s(f"Nombre: {orden['paciente_nombre']}"), ln=True)
    pdf.ln(4)

    # Detalle del Trabajo
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8, " DETALLE DEL PEDIDO", ln=True, fill=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(2)
    pdf.cell(0, 6, _s(f"Producto/Montura: {orden['montura_detalle']}"), ln=True)
    
    # Receta resumida
    rx = orden.get("detalles_receta", {})
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 5, _s(f"OD: {rx.get('od','')} | OI: {rx.get('oi','')}"), ln=True)
    pdf.ln(4)

    # Valores
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8, " RESUMEN DE PAGO", ln=True, fill=True)
    pdf.ln(2)
    
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(80, 8, "VALOR TOTAL:", 0)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, f"${float(orden['total_venta']):.2f}", ln=True, align="R")
    
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(80, 8, "ABONO REALIZADO:", 0)
    pdf.set_text_color(0, 150, 0)
    pdf.cell(0, 8, f"-${float(orden['abono']):.2f}", ln=True, align="R")
    
    pdf.set_text_color(200, 0, 0)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(80, 10, "SALDO PENDIENTE:", 0)
    pdf.cell(0, 10, f"${float(orden['saldo']):.2f}", ln=True, align="R")
    
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)
    
    # Pie de página
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4, _s("Nota: Los trabajos de laboratorio tienen un tiempo estimado de entrega de 3 a 5 días laborables. Favor presentar este ticket para retirar su pedido."), align="C")
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(0, 5, _s(f"📍 Sucursal: {orden['sucursal']} | Happy Vision"), ln=True, align="C")

# ══════════════════════════════════════════════════════════════
# REPORTE DE INVENTARIO FÍSICO (PDF)
# ══════════════════════════════════════════════════════════════
def generar_pdf_inventario(df_inv: pd.DataFrame, sucursal: str, supervisor: str = "") -> bytes:
    """Genera un PDF con formato de tabla tipo Excel para control de inventario físico."""
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=30)
    pdf.set_margins(10, 15, 10)

    # ─ Encabezado ────────────────────────────────────────────────
    logo_path = "logo.png" if os.path.exists("logo.png") else None
    if logo_path:
        pdf.image(logo_path, x=10, y=10, w=35)
    
    pdf.set_y(15)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(0, 160, 180)
    pdf.cell(0, 8, _s("REPORTE PARA CONTROL DE INVENTARIO FÍSICO"), ln=True, align="C")
    
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 116, 139)
    fecha_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    pdf.cell(0, 6, _s(f"Sucursal: {sucursal}   |   Fecha de emisión: {fecha_str}"), ln=True, align="C")
    pdf.ln(10)

    # ─ Encabezados de Tabla ──────────────────────────────────────
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(241, 245, 249)
    pdf.set_text_color(30, 41, 59)
    
    col_widths = [15, 55, 30, 20, 25, 45]
    headers = ["Cód.", "Producto / Descripción", "Categoría", "Stock Sist.", "Físico (Real)", "Observación"]
    
    for w, h in zip(col_widths, headers):
        pdf.cell(w, 8, _s(h), border=1, fill=True, align="C")
    pdf.ln()

    # ─ Filas de la Tabla ─────────────────────────────────────────
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(0, 0, 0)
    
    for _, row in df_inv.iterrows():
        cod = str(row.get("codigo_proveedor", row.get("id", "")))
        nombre = str(row.get("nombre", ""))[:35]
        cat = str(row.get("categoria", ""))[:15]
        stock = str(row.get("stock", row.get("cantidad_disponible", 0)))
        
        pdf.cell(col_widths[0], 7, _s(cod), border=1, align="C")
        pdf.cell(col_widths[1], 7, _s(nombre), border=1, align="L")
        pdf.cell(col_widths[2], 7, _s(cat), border=1, align="C")
        pdf.cell(col_widths[3], 7, _s(stock), border=1, align="C")
        pdf.cell(col_widths[4], 7, "", border=1, align="C") # Espacio para llenar
        pdf.cell(col_widths[5], 7, "", border=1, align="L") # Espacio para observación
        pdf.ln()

    # ─ Zona de Firmas (Footer Fijo) ──────────────────────────────
    # Si queda poco espacio, forzamos un salto de página para la firma
    if pdf.get_y() > 240:
        pdf.add_page()
        pdf.set_y(30)
    else:
        pdf.ln(25)
        
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(90, 8, _s("___________________________________"), ln=False, align="C")
    pdf.cell(90, 8, _s("___________________________________"), ln=True, align="C")
    
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(90, 6, _s("Firma del Responsable / Auditor"), ln=False, align="C")
    pdf.cell(90, 6, _s(f"Firma del Supervisor ({supervisor})" if supervisor else "Firma del Supervisor"), ln=True, align="C")

    return pdf.output(dest="S").encode("latin-1")

def generar_pdf_venta(venta_data: dict) -> bytes:
    """Genera un PDF de factura/ticket para una venta directa."""
    pdf = FPDF(orientation='P', unit='mm', format='A5')
    pdf.add_page()
    
    # Encabezado (Logo si existe)
    if os.path.exists("logo.png"):
        pdf.image("logo.png", 10, 8, 33)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, _s("HAPPY VISION"), ln=True, align="C")
    pdf.set_font("Arial", '', 9)
    pdf.cell(0, 5, _s("RUC: 1726715053001"), ln=True, align="C")
    pdf.cell(0, 5, _s("Dirección: Sucursal " + venta_data.get('sucursal', 'Matriz')), ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, _s("COMPROBANTE DE VENTA"), ln=True, align="C", border="B")
    pdf.ln(2)
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 6, _s(f"Cliente: {venta_data.get('cliente', 'Consumidor Final')}"), ln=True)
    pdf.cell(0, 6, _s(f"Fecha: {pd.to_datetime(venta_data.get('fecha')).strftime('%Y-%m-%d %H:%M')}"), ln=True)
    pdf.ln(4)
    
    # Detalle de productos
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(90, 7, _s("Descripción"), 1, 0, 'C', True)
    pdf.cell(30, 7, _s("Precio"), 1, 1, 'C', True)
    
    pdf.set_font("Arial", '', 9)
    for item in venta_data.get('detalles', []):
        pdf.cell(90, 7, _s(item['detalle']), 1)
        pdf.cell(30, 7, f"${item['precio']:.2f}", 1, 1, 'R')
    
    pdf.ln(2)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(90, 8, _s("TOTAL A PAGAR:"), 0, 0, 'R')
    pdf.cell(30, 8, f"${venta_data.get('total', 0):.2f}", 1, 1, 'C', True)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(0, 4, _s("Gracias por su compra. Recuerde realizar su control visual cada año.\nEste documento no es una factura válida ante el SRI."), align="C")
    
    return pdf.output(dest='S').encode('latin1')

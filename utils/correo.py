import smtplib
import os
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders

def enviar_email(destino: str, asunto: str, cuerpo: str, adjuntos: list[tuple[str, bytes]]) -> bool:
    """Envía un email vía SMTP.
    Params:
        destino: dirección de correo del cliente.
        asunto: asunto del mensaje.
        cuerpo: texto plano o HTML.
        adjuntos: lista de (nombre_archivo, contenido_bytes).
    Returns:
        True si el envío fue exitoso, False en caso contrario.
    """
    # Configuración del servidor SMTP – usar variables de entorno para credenciales
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    if not smtp_user or not smtp_pass:
        raise RuntimeError("Credenciales SMTP no configuradas en variables de entorno.")

    mensaje = MIMEMultipart()
    mensaje["From"] = smtp_user
    mensaje["To"] = destino
    mensaje["Subject"] = asunto
    mensaje.attach(MIMEText(cuerpo, "plain"))

    for nombre, contenido in adjuntos:
        parte = MIMEBase("application", "octet-stream")
        parte.set_payload(contenido)
        encoders.encode_base64(parte)
        parte.add_header("Content-Disposition", f"attachment; filename={nombre}")
        mensaje.attach(parte)

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(mensaje)
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False

# Helper para crear el PDF del RIDE (simplificado, usando fpdf)
def crear_pdf_ride(xml_str: str, nombre_archivo: str = "RIDE.pdf") -> bytes:
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 10, txt=xml_str)
    return pdf.output(dest="S").encode("latin1")

__all__ = ["enviar_email", "crear_pdf_ride"]

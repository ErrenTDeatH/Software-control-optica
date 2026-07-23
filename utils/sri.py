import json
import base64
import hashlib
import datetime
import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import pkcs12

# -----------------------------------------------------------------------------
# Helper functions for SRI electronic invoicing (Ecuador)
# -----------------------------------------------------------------------------

def generar_clave_acceso(fecha_emision: str, tipo_comprobante: str, ruc: str, ambiente: str, numero_secuencial: str, codigo_numerico: str) -> str:
    """Genera la clave de acceso de 49 dígitos según el algoritmo del SRI.
    Parámetros:
        fecha_emision: DDMMYYYY
        tipo_comprobante: 2 dígitos (01=Factura, etc.)
        ruc: 13 dígitos
        ambiente: 1 dígito (1=pruebas, 2=producción)
        numero_secuencial: 9 dígitos (establecimiento-punto-emisión-número)
        codigo_numerico: 8 dígitos aleatorios
    Retorna:
        clave de acceso completa (49 caracteres).
    """
    base = f"{fecha_emision}{tipo_comprobante}{ruc}{ambiente}{numero_secuencial}{codigo_numerico}"
    # cálculo módulo 11
    pesos = list(range(len(base)+1, 1, -1))
    total = sum(int(d) * p for d, p in zip(base, pesos))
    residuo = total % 11
    digito_verificador = 11 - residuo
    if digito_verificador >= 10:
        digito_verificador = 0
    return f"{base}{digito_verificador}"


def generar_xml_factura(datos_factura: dict) -> str:
    """Construye el XML del comprobante de acuerdo al esquema versión 1.1.0 del SRI.
    El diccionario debe contener los campos básicos (cliente, identificacion, items, etc.).
    Esta función devuelve el XML como cadena UTF‑8.
    """
    # Sección de cabecera
    fecha = datetime.datetime.now().strftime("%d/%m/%Y")
    clave_acceso = generar_clave_acceso(
        fecha_emision=datetime.datetime.now().strftime("%d%m%Y"),
        tipo_comprobante="01",  # Factura
        ruc=datos_factura.get("ruc_emisor", "1724219463001"),
        ambiente="2",  # 2 = producción
        numero_secuencial=datos_factura.get("secuencial", "001001000000001"),
        codigo_numerico="12345678"
    )

    xml = f"""<?xml version='1.0' encoding='UTF-8'?>
    <factura id='comprobante' version='1.1.0'>
        <infoTributaria>
            <ambiente>2</ambiente>
            <tipoEmision>1</tipoEmision>
            <razonSocial>{datos_factura.get('razon_social', '')}</razonSocial>
            <nombreComercial>{datos_factura.get('nombre_comercial', '')}</nombreComercial>
            <ruc>{datos_factura.get('ruc_emisor', '')}</ruc>
            <claveAcceso>{clave_acceso}</claveAcceso>
            <codDoc>01</codDoc>
            <estab>{datos_factura.get('establecimiento', '001')}</estab>
            <ptoEmi>{datos_factura.get('punto_emision', '001')}</ptoEmi>
            <secuencial>{datos_factura.get('secuencial', '000000001')}</secuencial>
            <dirMatriz>{datos_factura.get('direccion_matriz', '')}</dirMatriz>
        </infoTributaria>
        <infoFactura>
            <fechaEmision>{fecha}</fechaEmision>
            <dirEstablecimiento>{datos_factura.get('direccion_establecimiento', '')}</dirEstablecimiento>
            <tipoIdentificacionComprador>{datos_factura.get('tipo_identificacion', '05')}</tipoIdentificacionComprador>
            <razonSocialComprador>{datos_factura.get('cliente', '')}</razonSocialComprador>
            <identificacionComprador>{datos_factura.get('identificacion', '')}</identificacionComprador>
            <totalSinImpuestos>{datos_factura.get('subtotal', 0.0):.2f}</totalSinImpuestos>
            <totalDescuento>{datos_factura.get('descuento', 0.0):.2f}</totalDescuento>
            <totalConImpuestos>
                <totalImpuesto>
                    <codigo>2</codigo>
                    <codigoPorcentaje>2</codigoPorcentaje>
                    <baseImponible>{datos_factura.get('subtotal', 0.0):.2f}</baseImponible>
                    <valor>{datos_factura.get('iva', 0.0):.2f}</valor>
                </totalImpuesto>
            </totalConImpuestos>
            <propina>0.00</propina>
            <importeTotal>{datos_factura.get('total', 0.0):.2f}</importeTotal>
            <moneda>USD</moneda>
        </infoFactura>
        <detalles>
"""
    # Items
    for idx, item in enumerate(datos_factura.get('items', []), start=1):
        xml += f"""            <detalle>
                <codigoPrincipal>{item.get('codigo', '')}</codigoPrincipal>
                <descripcion>{item.get('descripcion', '')}</descripcion>
                <cantidad>{item.get('cantidad', 1)}</cantidad>
                <precioUnitario>{item.get('precio', 0.0):.2f}</precioUnitario>
                <descuento>{item.get('descuento', 0.0):.2f}</descuento>
                <precioTotalSinImpuesto>{item.get('precio_total', 0.0):.2f}</precioTotalSinImpuesto>
            </detalle>
"""
    xml += """        </detalles>
    </factura>
"""
    return xml


def firmar_xml_xades(xml_str: str, p12_path: str = "firma.p12", password: str = "") -> str:
    """Firma el XML con XAdES‑BES usando un archivo PKCS#12.
    Retorna el XML completo con el nodo <ds:Signature> añadido.
    """
    # Cargar certificado y llave privada
    with open(p12_path, "rb") as f:
        p12_data = f.read()
    private_key, certificate, additional_certs = pkcs12.load_key_and_certificates(p12_data, password.encode() if password else None)
    # Calcular el digest del XML (SHA256)
    digest = hashlib.sha256(xml_str.encode("utf-8")).digest()
    # Firmar el digest con la llave privada
    signature = private_key.sign(
        digest,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    signature_b64 = base64.b64encode(signature).decode()
    # Insertar la firma en el XML (simplificado)
    firma_xml = f"""<ds:Signature xmlns:ds='http://www.w3.org/2000/09/xmldsig#'>
        <ds:SignedInfo>
            <ds:CanonicalizationMethod Algorithm='http://www.w3.org/TR/2001/REC-xml-c14n-20010315'/>
            <ds:SignatureMethod Algorithm='http://www.w3.org/2000/09/xmldsig#rsa-sha256'/>
            <ds:Reference URI=''>
                <ds:Transforms>
                    <ds:Transform Algorithm='http://www.w3.org/2000/09/xmldsig#enveloped-signature'/>
                </ds:Transforms>
                <ds:DigestMethod Algorithm='http://www.w3.org/2001/04/xmlenc#sha256'/>
                <ds:DigestValue>{base64.b64encode(digest).decode()}</ds:DigestValue>
            </ds:Reference>
        </ds:SignedInfo>
        <ds:SignatureValue>{signature_b64}</ds:SignatureValue>
        <ds:KeyInfo>
            <ds:X509Data>
                <ds:X509Certificate>{base64.b64encode(certificate.public_bytes(serialization.Encoding.DER)).decode()}</ds:X509Certificate>
            </ds:X509Data>
        </ds:KeyInfo>
    </ds:Signature>"""
    # Insertar antes del cierre de la etiqueta factura
    if "</factura>" in xml_str:
        return xml_str.replace("</factura>", firma_xml + "</factura>")
    else:
        return xml_str + firma_xml


def enviar_sri_recepcion(xml_firmado: str) -> dict:
    """Envía el XML firmado al servicio de recepción del SRI (SOAP).
    Retorna el dict con 'estado' y 'mensaje'.
    """
    wsdl = "https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl"
    headers = {"Content-Type": "text/xml; charset=utf-8"}
    response = requests.post(wsdl, data=xml_firmado.encode("utf-8"), headers=headers, timeout=30)
    return {"estado": response.status_code, "texto": response.text}


def autorizar_sri_comprobante(clave_acceso: str) -> dict:
    """Consulta la autorización del comprobante mediante la clave de acceso.
    """
    wsdl = "https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantes?wsdl"
    payload = f"""<soapenv:Envelope xmlns:soapenv='http://schemas.xmlsoap.org/soap/envelope/' xmlns:aut='http://ec.gob.sri.ws.autorizacion'>
       <soapenv:Header/>
       <soapenv:Body>
          <aut:autorizacionComprobante>
             <claveAccesoComprobante>{clave_acceso}</claveAccesoComprobante>
          </aut:autorizacionComprobante>
       </soapenv:Body>
    </soapenv:Envelope>"""
    headers = {"Content-Type": "text/xml; charset=utf-8"}
    response = requests.post(wsdl, data=payload.encode("utf-8"), headers=headers, timeout=30)
    return {"estado": response.status_code, "texto": response.text}

# -----------------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------------
__all__ = [
    "generar_clave_acceso",
    "generar_xml_factura",
    "firmar_xml_xades",
    "enviar_sri_recepcion",
    "autorizar_sri_comprobante",
]

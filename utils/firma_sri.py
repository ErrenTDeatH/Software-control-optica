"""
utils/firma_sri.py — Motor de Firma Electrónica y Envío al SRI Ecuador
Integra la configuración guardada en Supabase con el flujo completo de
generación, firma y envío de comprobantes electrónicos.
"""
import base64
import random
import datetime
from database import supabase


# ══════════════════════════════════════════════════════════════
# CARGA DE CONFIGURACIÓN DEL EMISOR
# ══════════════════════════════════════════════════════════════

def cargar_config_empresa(sucursal: str = "Matriz") -> dict:
    """Carga la configuración del emisor desde Supabase.
    Retorna un diccionario vacío si no hay configuración.
    """
    try:
        if not supabase:
            return {}
        res = supabase.table("configuracion_empresa").select("*").eq("sucursal", sucursal).execute()
        if res.data:
            return res.data[0]
        return {}
    except Exception as e:
        print(f"Error cargar_config_empresa: {e}")
        return {}


def guardar_config_empresa(data: dict) -> bool:
    """Guarda o actualiza la configuración de la empresa / sucursal."""
    try:
        if not supabase:
            return False
        data["actualizado_el"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        # Si tiene id, actualiza; si no, upsert por sucursal
        sucursal = data.get("sucursal", "Matriz")
        existing = supabase.table("configuracion_empresa").select("id").eq("sucursal", sucursal).execute()
        if existing.data:
            supabase.table("configuracion_empresa").update(data).eq("sucursal", sucursal).execute()
        else:
            supabase.table("configuracion_empresa").insert(data).execute()
        return True
    except Exception as e:
        print(f"Error guardar_config_empresa: {e}")
        return False


# ══════════════════════════════════════════════════════════════
# VALIDACIÓN
# ══════════════════════════════════════════════════════════════

def validar_config_sri(config: dict) -> tuple[bool, list]:
    """Valida que la configuración esté completa para poder facturar.
    Retorna (es_valida, lista_de_errores).
    """
    errores = []
    campos_requeridos = {
        "ruc": "RUC del emisor",
        "razon_social": "Razón Social",
        "direccion_matriz": "Dirección Matriz",
        "establecimiento": "Número de Establecimiento",
        "punto_emision": "Punto de Emisión",
    }
    for campo, label in campos_requeridos.items():
        if not config.get(campo, "").strip():
            errores.append(f"Falta: {label}")

    if not config.get("firma_p12_b64"):
        errores.append("Falta: Certificado de Firma Electrónica (.p12)")

    if not config.get("firma_password"):
        errores.append("Falta: Contraseña del certificado .p12")

    # Validar vigencia del certificado
    vigente_hasta = config.get("firma_vigente_hasta")
    if vigente_hasta:
        try:
            fecha_venc = datetime.datetime.strptime(str(vigente_hasta)[:10], "%Y-%m-%d").date()
            hoy = datetime.date.today()
            if fecha_venc < hoy:
                errores.append(f"⛔ Certificado VENCIDO el {fecha_venc.strftime('%d/%m/%Y')}. Renuévalo.")
            elif (fecha_venc - hoy).days <= 30:
                errores.append(f"⚠️ Certificado vence el {fecha_venc.strftime('%d/%m/%Y')} ({(fecha_venc - hoy).days} días restantes).")
        except Exception:
            pass

    return len(errores) == 0, errores


def dias_para_vencimiento_firma(config: dict) -> int | None:
    """Retorna días hasta el vencimiento del certificado, o None si no aplica."""
    vigente_hasta = config.get("firma_vigente_hasta")
    if not vigente_hasta:
        return None
    try:
        fecha_venc = datetime.datetime.strptime(str(vigente_hasta)[:10], "%Y-%m-%d").date()
        return (fecha_venc - datetime.date.today()).days
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════
# FLUJO PRINCIPAL: FIRMAR Y ENVIAR AL SRI
# ══════════════════════════════════════════════════════════════

def firmar_y_enviar_sri(factura_db: dict, config: dict = None) -> dict:
    """
    Flujo completo de facturación electrónica SRI.
    
    Args:
        factura_db: Diccionario con los datos de la factura (de tabla `facturas`).
        config: Configuración del emisor. Si es None, se carga desde Supabase.
    
    Returns:
        dict con campos:
          - success: bool
          - estado: 'AUTORIZADO' | 'RECHAZADO' | 'ERROR'
          - clave_acceso: str (49 dígitos)
          - numero_autorizacion: str
          - mensaje: str (descripción del resultado)
          - xml_firmado: str
          - errores_sri: list
    """
    resultado = {
        "success": False,
        "estado": "ERROR",
        "clave_acceso": "",
        "numero_autorizacion": "",
        "mensaje": "",
        "xml_firmado": "",
        "errores_sri": []
    }

    try:
        from utils.sri import (
            generar_clave_acceso, generar_xml_factura,
            firmar_xml_xades, enviar_sri_recepcion, autorizar_sri_comprobante
        )
        import tempfile
        import os

        # 1. Cargar configuración
        if config is None:
            config = cargar_config_empresa(factura_db.get("sucursal", "Matriz"))

        es_valida, errores_val = validar_config_sri(config)
        if not es_valida:
            resultado["mensaje"] = "Configuración incompleta"
            resultado["errores_sri"] = errores_val
            return resultado

        ambiente = config.get("ambiente_sri", "PRUEBAS")
        amb_cod = "1" if ambiente == "PRUEBAS" else "2"

        # 2. Preparar datos del XML
        fecha_dt = datetime.datetime.now()
        secuencial = str(config.get("secuencial_actual", 1)).zfill(9)
        codigo_numerico = str(random.randint(10000000, 99999999))

        clave_acceso = generar_clave_acceso(
            fecha_emision=fecha_dt.strftime("%d%m%Y"),
            tipo_comprobante="01",  # 01 = Factura
            ruc=config["ruc"],
            ambiente=amb_cod,
            numero_secuencial=f"{config['establecimiento']}{config['punto_emision']}{secuencial}",
            codigo_numerico=codigo_numerico
        )

        # Construir lista de items para el XML
        items_raw = factura_db.get("items", [])
        items_xml = []
        if isinstance(items_raw, list):
            for i, item in enumerate(items_raw):
                precio_unit = float(item.get("precio_unitario", 0))
                cant = int(item.get("cantidad", 1))
                total_item = precio_unit * cant
                items_xml.append({
                    "codigo": str(i + 1).zfill(3),
                    "descripcion": item.get("descripcion", "Producto"),
                    "cantidad": cant,
                    "precio": precio_unit,
                    "descuento": 0.0,
                    "precio_total": total_item
                })

        datos_xml = {
            "ruc_emisor": config["ruc"],
            "razon_social": config["razon_social"],
            "nombre_comercial": config.get("nombre_comercial", config["razon_social"]),
            "direccion_matriz": config["direccion_matriz"],
            "direccion_establecimiento": config.get("direccion_matriz", ""),
            "establecimiento": config["establecimiento"],
            "punto_emision": config["punto_emision"],
            "secuencial": secuencial,
            "cliente": factura_db.get("cliente_nombre", "CONSUMIDOR FINAL"),
            "identificacion": factura_db.get("cliente_cedula", "9999999999999"),
            "tipo_identificacion": _tipo_identificacion(factura_db.get("cliente_cedula", "")),
            "subtotal": float(factura_db.get("subtotal", 0)),
            "descuento": float(factura_db.get("descuento", 0)),
            "iva": float(factura_db.get("iva", 0)),
            "total": float(factura_db.get("total", 0)),
            "items": items_xml
        }

        # 3. Generar XML
        xml_str = generar_xml_factura(datos_xml)

        # 4. Guardar .p12 temporal para firmar
        p12_bytes = base64.b64decode(config["firma_p12_b64"])
        password_firma = config.get("firma_password", "")

        with tempfile.NamedTemporaryFile(suffix=".p12", delete=False) as tmp:
            tmp.write(p12_bytes)
            tmp_path = tmp.name

        try:
            xml_firmado = firmar_xml_xades(xml_str, tmp_path, password_firma)
        finally:
            os.unlink(tmp_path)  # Eliminar archivo temporal siempre

        resultado["xml_firmado"] = xml_firmado

        # 5. Enviar al SRI (recepción)
        resp_recepcion = enviar_sri_recepcion(xml_firmado)
        if resp_recepcion.get("estado") != 200:
            resultado["mensaje"] = f"Error HTTP al enviar al SRI: {resp_recepcion.get('estado')}"
            resultado["errores_sri"] = [resp_recepcion.get("texto", "")]
            return resultado

        # 6. Consultar autorización
        resp_autorizacion = autorizar_sri_comprobante(clave_acceso)
        texto_resp = resp_autorizacion.get("texto", "")

        if "AUTORIZADO" in texto_resp.upper():
            resultado["success"] = True
            resultado["estado"] = "AUTORIZADO"
            resultado["clave_acceso"] = clave_acceso
            resultado["numero_autorizacion"] = clave_acceso  # En SRI, la clave acceso == número de autorización
            resultado["mensaje"] = f"✅ Comprobante AUTORIZADO por el SRI. Clave: {clave_acceso}"

            # Incrementar secuencial en Supabase
            try:
                nuevo_sec = int(config.get("secuencial_actual", 1)) + 1
                supabase.table("configuracion_empresa").update(
                    {"secuencial_actual": nuevo_sec}
                ).eq("sucursal", factura_db.get("sucursal", "Matriz")).execute()
            except Exception:
                pass

        elif "RECHAZADO" in texto_resp.upper():
            resultado["estado"] = "RECHAZADO"
            resultado["mensaje"] = "❌ Comprobante RECHAZADO por el SRI."
            resultado["errores_sri"] = [texto_resp]
        else:
            resultado["estado"] = "EN_PROCESO"
            resultado["mensaje"] = "⏳ Comprobante en proceso de autorización. Consulta más tarde."
            resultado["clave_acceso"] = clave_acceso

    except ImportError as e:
        resultado["mensaje"] = f"Módulo faltante: {e}. Instala: pip install cryptography requests"
        resultado["errores_sri"] = [str(e)]
    except Exception as e:
        resultado["mensaje"] = f"Error inesperado: {str(e)}"
        resultado["errores_sri"] = [str(e)]
        import traceback
        print(traceback.format_exc())

    return resultado


# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════

def _tipo_identificacion(cedula: str) -> str:
    """Determina el tipo de identificación según longitud y formato."""
    if not cedula:
        return "07"  # Consumidor final
    cedula = cedula.strip().replace("-", "")
    if len(cedula) == 13:
        return "04"  # RUC
    elif len(cedula) == 10:
        return "05"  # Cédula
    else:
        return "06"  # Pasaporte


# ══════════════════════════════════════════════════════════════
# EXPORTACIONES
# ══════════════════════════════════════════════════════════════

__all__ = [
    "cargar_config_empresa",
    "guardar_config_empresa",
    "validar_config_sri",
    "dias_para_vencimiento_firma",
    "firmar_y_enviar_sri",
]

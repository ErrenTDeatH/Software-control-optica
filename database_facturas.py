"""
database_facturas.py — Funciones para la tabla facturas y pagos en Supabase.
Importar desde database.py o directamente donde se necesite.
"""
import pandas as pd
from datetime import datetime, date
from database import supabase, registrar_auditoria


def guardar_factura(data: dict) -> dict | None:
    """Crea o actualiza una factura. Si incluye 'id', actualiza. Si no, inserta."""
    try:
        if not supabase:
            return None
        if "id" in data and data["id"]:
            res = supabase.table("facturas").update(data).eq("id", data["id"]).execute()
        else:
            res = supabase.table("facturas").insert(data).execute()
        if res.data:
            return res.data[0]
        return None
    except Exception as e:
        print(f"Error guardar_factura: {e}")
        return None


def cargar_facturas(sucursal: str = None, estado: str = None) -> pd.DataFrame:
    """Carga el historial de facturas con filtros opcionales."""
    try:
        if not supabase:
            return pd.DataFrame()
        query = supabase.table("facturas").select("*")
        if sucursal and sucursal != "Todas":
            query = query.eq("sucursal", sucursal)
        if estado:
            query = query.eq("estado", estado)
        res = query.order("creado_el", desc=True).execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception as e:
        print(f"Error cargar_facturas: {e}")
        return pd.DataFrame()


def anular_factura(factura_id: int, usuario: str, sucursal: str) -> bool:
    """Anula una factura emitida."""
    try:
        if not supabase:
            return False
        supabase.table("facturas").update({"estado": "ANULADA"}).eq("id", factura_id).execute()
        registrar_auditoria(
            accion="Anular Factura",
            entidad="Facturación",
            detalle=f"Factura #{factura_id} anulada.",
            usuario=usuario,
            sucursal=sucursal
        )
        return True
    except Exception as e:
        print(f"Error anular_factura: {e}")
        return False


def registrar_pago(data: dict) -> bool:
    """Registra un pago parcial o total vinculado a una venta/orden/factura."""
    try:
        if not supabase:
            return False
        supabase.table("pagos").insert(data).execute()
        registrar_auditoria(
            accion="Pago Registrado",
            entidad="Ventas",
            detalle=f"Monto: ${data.get('monto', 0)} | Método: {data.get('metodo', '')} | Ref: {data.get('referencia', '')}",
            usuario=data.get("cobrado_por", ""),
            sucursal=data.get("sucursal", "")
        )
        return True
    except Exception as e:
        print(f"Error registrar_pago: {e}")
        return False


def cargar_pagos(venta_id: int = None, orden_id: int = None) -> pd.DataFrame:
    """Carga el historial de pagos de una venta u orden."""
    try:
        if not supabase:
            return pd.DataFrame()
        query = supabase.table("pagos").select("*")
        if venta_id:
            query = query.eq("venta_id", venta_id)
        if orden_id:
            query = query.eq("orden_id", orden_id)
        res = query.order("creado_el", desc=True).execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception as e:
        print(f"Error cargar_pagos: {e}")
        return pd.DataFrame()


def cargar_cuentas_por_cobrar(sucursal: str = None) -> pd.DataFrame:
    """Carga órdenes y ventas con saldo pendiente > 0."""
    try:
        if not supabase:
            return pd.DataFrame()
        # Saldos de órdenes de trabajo
        query = supabase.table("ordenes_trabajo").select("id, paciente_nombre, total_venta, abono, saldo, estado, sucursal, creado_el")
        if sucursal and sucursal != "Todas":
            query = query.eq("sucursal", sucursal)
        res = query.gt("saldo", 0).neq("estado", "Anulado").execute()
        df = pd.DataFrame(res.data) if res.data else pd.DataFrame()
        if not df.empty:
            df["tipo"] = "Orden de Trabajo"
            df["cliente"] = df.get("paciente_nombre", "")
        return df
    except Exception as e:
        print(f"Error cargar_cuentas_por_cobrar: {e}")
        return pd.DataFrame()

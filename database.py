"""
╔══════════════════════════════════════════════════════════════╗
║  HAPPY VISION · database.py                                  ║
║  Capa de acceso a datos Supabase                             ║
║  Todas las operaciones de lectura/escritura en la DB en nube ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar .env si existe (entorno local)
load_dotenv()

# Intentar cargar desde variables de entorno (Streamlit Secrets o .env)
# Nota: Streamlit Cloud usa st.secrets.
try:
    import streamlit as st
    SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL"))
    SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY"))
except ImportError:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Inicializar cliente Supabase solo si hay credenciales (para evitar errores en import)
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Decorador de caché compatible (Streamlit fallback para CLI/scripts)
try:
    import streamlit as st
    cache_data = st.cache_data
except ImportError:
    def cache_data(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

# ══════════════════════════════════════════════════════════════
# AUDITORÍA — Registro inmutable de cambios críticos
# ══════════════════════════════════════════════════════════════
def registrar_auditoria(accion: str, entidad: str = "", detalle: str = "",
                        usuario: str = "", nombre_usuario: str = "", sucursal: str = ""):
    """Registra un evento crítico en la tabla auditoria de Supabase.
    Nunca lanza excepciones para no interrumpir el flujo principal.
    """
    if not supabase:
        return
    try:
        from datetime import datetime, timezone
        supabase.table("auditoria").insert({
            "fecha_hora":    datetime.now(timezone.utc).isoformat(),
            "usuario":       usuario or "desconocido",
            "nombre_usuario": nombre_usuario or usuario,
            "accion":        accion,
            "entidad":       entidad,
            "detalle":       detalle,
            "sucursal":      sucursal,
        }).execute()
        # Confirmación visual opcional
        try:
            import streamlit as st
            st.toast(f"📝 Auditoría: {accion}")
        except: pass
    except Exception as e:
        print(f"[Auditoría] Error registrando evento: {e}")

def cargar_auditoria(limit: int = 500) -> pd.DataFrame:
    """Carga los registros de auditoría más recientes para el Admin."""
    try:
        if not supabase:
            return pd.DataFrame()
        res = supabase.table("auditoria").select("*").order("fecha_hora", desc=True).limit(limit).execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception as e:
        print(f"Error cargar_auditoria: {e}")
        return pd.DataFrame()

def cargar_sucursales() -> pd.DataFrame:
    """Carga todas las sucursales disponibles desde Supabase."""
    try:
        if not supabase: return pd.DataFrame()
        res = supabase.table("sucursales").select("*").order("nombre").execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception as e:
        print(f"Error cargar_sucursales: {e}")
        return pd.DataFrame()

@cache_data(ttl=600, show_spinner=False)
def cargar_optometristas() -> list:
    """Carga la lista de nombres de usuarios (optometristas) activos."""
    try:
        if not supabase: return []
        res = supabase.table("usuarios").select("nombre").execute()
        if res.data:
            nombres = [u["nombre"] for u in res.data if str(u.get("nombre")).strip()]
            return sorted(list(set(nombres)))
        return []
    except Exception as e:
        print(f"Error cargar_optometristas: {e}")
        return []

# ══════════════════════════════════════════════════════════════
# INVENTARIO (MONTURAS)
# ══════════════════════════════════════════════════════════════
@cache_data(ttl=300, show_spinner=False)
def cargar_inventario(sucursal: str = None) -> pd.DataFrame:
    """Carga el inventario de monturas."""
    try:
        if not supabase: return pd.DataFrame()
        query = supabase.table("inventario").select("*")
        if sucursal:
            query = query.eq("sucursal", sucursal)
        res = query.order("marca").execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception as e:
        print(f"Error cargar_inventario: {e}")
        return pd.DataFrame()

def guardar_producto(data: dict):
    """Guarda o actualiza una montura en el inventario."""
    try:
        if not supabase: return
        if "id" in data:
            supabase.table("inventario").update(data).eq("id", data["id"]).execute()
        else:
            supabase.table("inventario").insert(data).execute()
        try:
            cargar_inventario.clear()
        except:
            pass
    except Exception as e:
        print(f"Error guardar_producto: {e}")

def eliminar_producto(id_producto: int):
    """Elimina un producto del inventario."""
    try:
        if not supabase: return
        supabase.table("inventario").delete().eq("id", id_producto).execute()
        try:
            cargar_inventario.clear()
        except:
            pass
    except Exception as e:
        print(f"Error eliminar_producto: {e}")

# ══════════════════════════════════════════════════════════════
# TRABAJOS (ÓRDENES) Y PAGOS
# ══════════════════════════════════════════════════════════════
def cargar_ordenes_trabajo(sucursal: str = None) -> pd.DataFrame:
    """Carga las órdenes de trabajo junto con sus pagos."""
    try:
        if not supabase: return pd.DataFrame()
        # Traemos la orden y el pago asociado (join simple de Supabase)
        query = supabase.table("ordenes_trabajo").select("*, pagos_y_saldos(*)")
        if sucursal:
            query = query.eq("sucursal", sucursal)
        res = query.order("id", desc=True).execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception as e:
        print(f"Error cargar_ordenes_trabajo: {e}")
        return pd.DataFrame()

def guardar_orden_trabajo(orden_data: dict):
    """Guarda una orden de trabajo técnica y su estado financiero."""
    try:
        if not supabase: return None
        # Insertar Orden con todos los campos técnicos (receta, etc)
        res = supabase.table("ordenes_trabajo").insert(orden_data).execute()
        if res.data:
            nueva_id = res.data[0]["id"]
            registrar_auditoria("Nueva Orden Óptica", "Laboratorio", f"Orden #{nueva_id} | Paciente: {orden_data.get('paciente_nombre')}", st.session_state.user_login, sucursal=orden_data.get("sucursal"))
            return nueva_id
        return None
    except Exception as e:
        print(f"Error guardar_orden_trabajo: {e}")
        return None

def actualizar_estado_orden(orden_id: int, nuevo_estado: str, usuario: str = "", sucursal: str = ""):
    """Actualiza el estado de una orden (Pendiente -> Laboratorio -> etc)."""
    try:
        if not supabase: return
        supabase.table("ordenes_trabajo").update({"estado": nuevo_estado}).eq("id", orden_id).execute()
        registrar_auditoria(
            accion="Cambio Estado Orden",
            entidad="Laboratorio",
            detalle=f"Orden ID {orden_id} pasó a estado: {nuevo_estado}",
            usuario=usuario,
            sucursal=sucursal
        )
    except Exception as e:
        print(f"Error actualizar_estado_orden: {e}")

# ══════════════════════════════════════════════════════════════
# CONTABILIDAD Y CAJA
# ══════════════════════════════════════════════════════════════
def obtener_estado_caja(sucursal: str, fecha: str) -> dict:
    """Busca si hay una caja abierta para hoy en esta sucursal."""
    try:
        if not supabase: return None
        res = supabase.table("caja_diaria").select("*").eq("sucursal", sucursal).eq("fecha", fecha).execute()
        return res.data[0] if res.data else None
    except: return None

def abrir_caja(data: dict):
    """Crea el registro de apertura de caja."""
    try:
        if not supabase: return
        supabase.table("caja_diaria").insert(data).execute()
        registrar_auditoria("Apertura de Caja", "Contabilidad", f"Monto inicial: ${data['monto_apertura']}", data['abierta_por'], sucursal=data['sucursal'])
    except Exception as e: print(f"Error abrir_caja: {e}")

def registrar_gasto(data: dict):
    """Registra un egreso de dinero."""
    try:
        if not supabase: return
        supabase.table("gastos").insert(data).execute()
        registrar_auditoria("Gasto Registrado", "Contabilidad", f"{data['categoria']}: ${data['monto']}", data['usuario'], sucursal=data['sucursal'])
    except Exception as e: print(f"Error registrar_gasto: {e}")

def obtener_resumen_dia(sucursal: str, fecha: str):
    """Calcula totales de ventas y gastos del día para el cierre, 
    sumando ingresos de ventas directas y abonos de órdenes.
    """
    try:
        if not supabase: return {"Efectivo":0, "Tarjeta":0, "Transferencia":0, "Gastos":0}
        
        totales = {"Efectivo":0, "Tarjeta":0, "Transferencia":0, "Gastos":0}
        
        # 1. Ingresos desde tabla 'ventas' (Nuevos registros internos)
        res_ventas = supabase.table("ventas").select("abono, metodo_pago").eq("sucursal", sucursal).filter("fecha", "gte", f"{fecha}T00:00:00").execute()
        for v in res_ventas.data:
            m = v.get("metodo_pago", "Efectivo")
            if m in totales:
                totales[m] += float(v.get("abono", 0))
        
        # 2. Ingresos desde 'ordenes_trabajo' (Abonos de órdenes creadas directamente o saldos)
        # Nota: Filtramos por 'creado_el' para nuevos abonos o podríamos tener una tabla de pagos específica.
        # Por ahora, sumamos abonos de órdenes cuya fecha coincida.
        res_ordenes = supabase.table("ordenes_trabajo").select("abono, metodo_pago").eq("sucursal", sucursal).filter("creado_el", "gte", f"{fecha}T00:00:00").execute()
        # Evitar duplicar si la venta ya registró el abono en la tabla ventas.
        # Pero como la app está separando módulos, esto dependerá del flujo.
        # Para ser conservadores y no duplicar, si ya sumamos de 'ventas', 
        # solo sumamos de 'ordenes' si no provienen de una venta directa.
        
        # 3. Gastos
        res_g = supabase.table("gastos").select("monto").eq("sucursal", sucursal).eq("fecha", fecha).execute()
        totales["Gastos"] = sum(float(g["monto"]) for g in res_g.data)
        
        return totales
    except Exception as e:
        print(f"Error obtener_resumen_dia: {e}")
        return {"Efectivo":0, "Tarjeta":0, "Transferencia":0, "Gastos":0}

def cerrar_caja(caja_id: int, data: dict):
    """Cierra la caja del día."""
    try:
        if not supabase: return
        supabase.table("caja_diaria").update(data).eq("id", caja_id).execute()
        registrar_auditoria("Cierre de Caja", "Contabilidad", f"Cierre final: ${data['monto_cierre']}", data['cerrada_por'], sucursal=data['sucursal'])
    except Exception as e: print(f"Error cerrar_caja: {e}")

def actualizar_historia(historia_id, data: dict):
    """Actualiza campos de una historia clínica en Supabase."""
    try:
        if not supabase: return
        supabase.table("historias_clinicas").update(data).eq("id", historia_id).execute()
        try:
            cargar_historias.clear()
        except:
            pass
        try:
            import streamlit as st
            registrar_auditoria("Actualizar Historia", "Clínica", f"ID Historia: {historia_id}", st.session_state.get("user_login", "desconocido"), sucursal=st.session_state.get("sucursal_activa", ""))
        except: pass
    except Exception as e: print(f"Error actualizar_historia: {e}")

def registrar_venta_directa(data: dict):
    """Registra una venta detallada (incluyendo costos para admin) y descuenta stock."""
    try:
        if not supabase: return None
        # 1. Registrar la venta en la tabla 'ventas' (ahora incluye costo_total para rentabilidad)
        res = supabase.table("ventas").insert(data).execute()
        
        # 2. Descontar stock de monturas si aplica
        for item in data.get("detalles", []):
            p_id = item.get("id_armazon") # ID del armazón del inventario
            if p_id:
                curr = supabase.table("inventario").select("cantidad_disponible").eq("id", p_id).execute()
                if curr.data:
                    stock_actual = float(curr.data[0].get("cantidad_disponible", 0))
                    nuevo_stock = max(0, stock_actual - 1)
                    supabase.table("inventario").update({"cantidad_disponible": nuevo_stock}).eq("id", p_id).execute()
        
        try:
            cargar_inventario.clear()
        except:
            pass

        # 3. Auditoría detallada
        costo = data.get('costo_total', 0)
        ganancia = float(data['total']) - float(costo)
        registrar_auditoria("Venta Óptica", "Ventas", f"Total: ${data['total']} | Ganancia: ${ganancia:.2f} | Cliente: {data.get('cliente')}", st.session_state.user_login, sucursal=data['sucursal'])
        return res.data[0] if res.data else True
    except Exception as e:
        print(f"Error registrar_venta_directa: {e}")
        return None

def cargar_ventas_historial(sucursal: str = None) -> pd.DataFrame:
    """Carga el historial completo de ventas para análisis de rentabilidad."""
    try:
        if not supabase: return pd.DataFrame()
        query = supabase.table("ventas").select("*")
        if sucursal and sucursal != "Todas":
            query = query.eq("sucursal", sucursal)
        res = query.order("fecha", desc=True).execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception as e:
        print(f"Error cargar_ventas_historial: {e}")
        return pd.DataFrame()

def registrar_pago_saldo(orden_id: int, monto: float, metodo: str, usuario: str, sucursal: str):
    """Registra el pago de un saldo pendiente de una orden de trabajo."""
    try:
        if not supabase: return
        # 1. Obtener orden
        res = supabase.table("ordenes_trabajo").select("saldo, abono").eq("id", orden_id).execute()
        if res.data:
            orden = res.data[0]
            nuevo_abono = float(orden["abono"]) + monto
            nuevo_saldo = max(0, float(orden["saldo"]) - monto)
            
            # 2. Actualizar orden
            upd = {"abono": nuevo_abono, "saldo": nuevo_saldo}
            if nuevo_saldo == 0: upd["estado"] = "Entregado" # Autocierre
            
            supabase.table("ordenes_trabajo").update(upd).eq("id", orden_id).execute()
            
            # 3. Auditoría
            registrar_auditoria("Cobro de Saldo", "Ventas", f"Orden #{orden_id} | Cobrado: ${monto}", usuario, sucursal=sucursal)
            return True
    except Exception as e:
        print(f"Error registrar_pago_saldo: {e}")
        return False

# ══════════════════════════════════════════════════════════════
# PACIENTES
# ══════════════════════════════════════════════════════════════
@cache_data(ttl=2, show_spinner=False)
def cargar_pacientes() -> pd.DataFrame:
    """Carga todos los pacientes desde Supabase."""
    try:
        if not supabase: return _empty_pacientes_df()
        response = supabase.table("pacientes").select("*").execute()
        data = response.data
        if data:
            # Reemplazar None por string vacío para mantener compatibilidad con la app
            df = pd.DataFrame(data).fillna("")
            return df
        return _empty_pacientes_df()
    except Exception as e:
        print(f"Error cargar_pacientes: {e}")
        return _empty_pacientes_df()

def _empty_pacientes_df() -> pd.DataFrame:
    return pd.DataFrame(columns=[
        "id", "identificacion", "nombre", "nombres", "apellidos",
        "genero", "direccion", "edad", "fecha_nacimiento",
        "telefono", "correo", "ocupacion"
    ])

def guardar_paciente(row: dict):
    """Inserta o actualiza un paciente en Supabase."""
    try:
        if not supabase: return
        # Asegurar que todos los valores sean string
        row_str = {k: str(v) if v is not None else "" for k, v in row.items()}
        supabase.table("pacientes").upsert(row_str).execute()
        try:
            cargar_pacientes.clear()
        except:
            pass
    except Exception as e:
        print(f"Error guardar_paciente: {e}")

def guardar_todos_pacientes(df: pd.DataFrame):
    """Sincroniza el DataFrame completo de pacientes a Supabase."""
    try:
        if not supabase: return
        # Convertir todo a string
        df_str = df.astype(str)
        # Reemplazar "nan" por ""
        df_str = df_str.replace("nan", "")
        records = df_str.to_dict(orient="records")
        if records:
            supabase.table("pacientes").upsert(records).execute()
        try:
            cargar_pacientes.clear()
        except:
            pass
    except Exception as e:
        print(f"Error guardar_todos_pacientes: {e}")
        try:
            import streamlit as st
            st.session_state["db_error"] = f"Error guardando pacientes en la base de datos: {e}"
        except: pass

def eliminar_paciente(p_id):
    """Elimina permanentemente un paciente de Supabase."""
    try:
        if not supabase: return
        supabase.table("pacientes").delete().eq("id", str(p_id)).execute()
        try:
            cargar_pacientes.clear()
        except:
            pass
    except Exception as e:
        print(f"Error eliminar_paciente: {e}")

PACIENTES_COLS = [
    "id", "identificacion", "nombre", "nombres", "apellidos", "genero", 
    "direccion", "edad", "fecha_nacimiento", "telefono", "correo", "ocupacion", "sucursal"
]

HISTORIAS_COLS = [
    "id", "paciente_id", "paciente_nombre", "fecha",
    "ant_personales", "ant_familiares", "motivo", "diabetes", "hipertension", 
    "patologia_otra", "observaciones", "lenso_od", "lenso_av_lej_od", "lenso_av_cer_od",
    "lenso_oi", "lenso_av_lej_oi", "lenso_av_cer_oi",
    "rx_od", "rx_av_lej_od", "rx_av_cer_od",
    "rx_oi", "rx_av_lej_oi", "rx_av_cer_oi",
    "estado_muscular", "seg_externo", "test_colores", "estado_refractivo",
    "diagnostico", "disposicion", "recomendaciones",
    "meses_proximo_control", "necesita_lentes", "test_color", "sucursal",
    "optometrista", "optometrista_login"
]

def migrar_estructuras():
    """Asegura que los DataFrames locales y remotos tengan todas las columnas necesarias."""
    try:
        import streamlit as st
        # 1. Migrar Pacientes
        if "df_pacientes" in st.session_state:
            df_p = st.session_state.df_pacientes
            for col in PACIENTES_COLS:
                if col not in df_p.columns:
                    # Asignar 'Matriz' a pacientes antiguos si no tienen sucursal
                    df_p[col] = "Matriz" if col == "sucursal" else ""
            
            # Limpiar sucursales vacías que pudieran haber quedado
            df_p.loc[df_p['sucursal'] == '', 'sucursal'] = 'Matriz'
            df_p.loc[df_p['sucursal'].isna(), 'sucursal'] = 'Matriz'
            st.session_state.df_pacientes = df_p[PACIENTES_COLS]
        
        # 2. Migrar Historias
        if "df_historias" in st.session_state:
            df_h = st.session_state.df_historias
            for col in HISTORIAS_COLS:
                if col not in df_h.columns:
                    # Asignar 'Matriz' a historias antiguas
                    df_h[col] = "Matriz" if col == "sucursal" else ""
            
            # Limpiar sucursales vacías que pudieran haber quedado
            df_h.loc[df_h['sucursal'] == '', 'sucursal'] = 'Matriz'
            df_h.loc[df_h['sucursal'].isna(), 'sucursal'] = 'Matriz'
            # Solo mantener columnas que existen (no eliminar columnas extra del DataFrame)
            cols_presentes = [c for c in HISTORIAS_COLS if c in df_h.columns]
            st.session_state.df_historias = df_h[cols_presentes]
            
        # 3. Migrar Usuarios (Nuevos Permisos) — solo la primera vez por sesión
        try:
            import streamlit as _st_mig
            if not _st_mig.session_state.get("_usuarios_migrados"):
                res_u = supabase.table("usuarios").select("*").execute()
                if res_u.data:
                    for usr in res_u.data:
                        if not usr.get("accesos") or "Generar Orden" not in usr.get("accesos", []):
                            # Asignar accesos base a usuarios antiguos incluyendo la nueva pestaña
                            default_acc = ["Pacientes", "Generar Orden", "Trabajos", "Ventas", "Inicio"]
                            if "Administrador" in str(usr.get("role", "")):
                                default_acc = ["Pacientes", "Generar Orden", "Trabajos", "Ventas", "Inventario", "Contabilidad", "Usuarios", "Configuracion", "Inicio"]
                            supabase.table("usuarios").update({"accesos": default_acc}).eq("username", usr["username"]).execute()
                _st_mig.session_state["_usuarios_migrados"] = True
        except Exception as ue:
            print(f"Error migrando permisos de usuarios: {ue}")

        print("Migración de estructuras completada exitosamente.")
    except Exception as e:
        print(f"Error en migración: {e}")

# ══════════════════════════════════════════════════════════════
# HISTORIAS CLÍNICAS
# ══════════════════════════════════════════════════════════════

@cache_data(ttl=300, show_spinner=False)
def cargar_historias() -> pd.DataFrame:
    """Carga todas las historias clínicas desde Supabase."""
    try:
        if not supabase: return pd.DataFrame(columns=HISTORIAS_COLS)
        response = supabase.table("historias_clinicas").select("*").execute()
        df = pd.DataFrame(response.data)
        # Asegurar columnas tras la carga
        for col in HISTORIAS_COLS:
            if col not in df.columns:
                df[col] = ""
        return df[HISTORIAS_COLS] if not df.empty else pd.DataFrame(columns=HISTORIAS_COLS)
    except Exception as e:
        print(f"Error cargar_historias: {e}")
        return pd.DataFrame(columns=HISTORIAS_COLS)

def _empty_historias_df() -> pd.DataFrame:
    return pd.DataFrame(columns=HISTORIAS_COLS)

def guardar_historia(row: dict):
    """Inserta o actualiza una historia clínica en Supabase."""
    try:
        if not supabase: return
        # Asegurar string y limpiar nulos
        row_str = {k: str(v) if v is not None else "" for k, v in row.items()}
        supabase.table("historias_clinicas").upsert(row_str).execute()
        try:
            cargar_historias.clear()
        except:
            pass
    except Exception as e:
        print(f"Error guardar_historia: {e}")

def guardar_todas_historias(df: pd.DataFrame):
    """Sincroniza el DataFrame completo de historias a Supabase."""
    try:
        if not supabase: return
        # Asegurar limpieza total de NaNs y conversión a strings
        df_limpio = df.copy().fillna("")
        records = []
        for _, row in df_limpio.iterrows():
            rec = {str(k): (str(v) if not pd.isna(v) and str(v).lower() != "nan" else "") for k, v in row.to_dict().items()}
            records.append(rec)
            
        if records:
            supabase.table("historias_clinicas").upsert(records).execute()
        try:
            cargar_historias.clear()
        except:
            pass
    except Exception as e:
        import traceback
        err_detail = traceback.format_exc()
        try:
            import streamlit as st
            st.session_state["db_error"] = f"🔥 ERROR CRÍTICO SUPABASE: {str(e)}\n\nDetalle técnico:\n{err_detail}"
        except: pass

def eliminar_historia(h_id):
    """Elimina permanentemente una historia de Supabase."""
    try:
        if not supabase: return
        supabase.table("historias_clinicas").delete().eq("id", str(h_id)).execute()
        try:
            cargar_historias.clear()
        except:
            pass
    except Exception as e:
        print(f"Error eliminar_historia: {e}")

# ══════════════════════════════════════════════════════════════
# SUCURSALES
# ══════════════════════════════════════════════════════════════

@cache_data(ttl=600, show_spinner=False)
def cargar_sucursales() -> pd.DataFrame:
    """Carga todas las sucursales desde Supabase."""
    try:
        if not supabase: return pd.DataFrame(columns=["nombre", "direccion", "telefono", "ciudad"])
        response = supabase.table("sucursales").select("*").order("nombre").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame(columns=["nombre", "direccion", "telefono", "ciudad"])
    except Exception as e:
        print(f"Error cargar_sucursales: {e}")
        return pd.DataFrame(columns=["nombre", "direccion", "telefono", "ciudad"])

def guardar_sucursal(row: dict):
    """Guarda o actualiza una sucursal. Si cambia el nombre, hace cascade UPDATE en todas las tablas."""
    try:
        if not supabase: return False, "Sin conexión a Supabase"

        # Detectar si el nombre cambió (solo aplica en edición, no creación)
        s_id = row.get("id")
        nombre_nuevo = row.get("nombre", "")
        if s_id and nombre_nuevo:
            try:
                res_prev = supabase.table("sucursales").select("nombre").eq("id", s_id).execute()
                nombre_anterior = res_prev.data[0]["nombre"] if res_prev.data else None
            except:
                nombre_anterior = None

            if nombre_anterior and nombre_anterior != nombre_nuevo:
                # Cascade UPDATE: actualizar nombre en todas las tablas relacionadas
                tablas_cascade = [
                    "pacientes", "historias_clinicas", "historias_lc",
                    "inventario", "citas", "ordenes_trabajo",
                    "ventas_directas", "caja_registros", "caja_estados"
                ]
                for tabla in tablas_cascade:
                    try:
                        supabase.table(tabla).update({"sucursal": nombre_nuevo}).eq("sucursal", nombre_anterior).execute()
                    except Exception as ce:
                        print(f"Cascade ignorado para '{tabla}': {ce}")

        supabase.table("sucursales").upsert(row).execute()
        try:
            cargar_sucursales.clear()
        except:
            pass
        return True, "Guardado exitosamente"
    except Exception as e:
        print(f"Error guardar_sucursal: {e}")
        return False, str(e)

def eliminar_sucursal(s_id):
    """Elimina una sucursal."""
    try:
        if not supabase: return
        supabase.table("sucursales").delete().eq("id", s_id).execute()
        try:
            cargar_sucursales.clear()
        except:
            pass
    except Exception as e:
        print(f"Error eliminar_sucursal: {e}")

def cargar_ordenes_trabajo(sucursal: str = None) -> pd.DataFrame:
    """Carga todas las órdenes de trabajo desde Supabase."""
    try:
        if not supabase: return pd.DataFrame()
        query = supabase.table("ordenes_trabajo").select("*")
        if sucursal and sucursal != "Todas":
            query = query.eq("sucursal", sucursal)
        res = query.order("creado_el", desc=True).execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception as e:
        print(f"Error cargar_ordenes_trabajo: {e}")
        return pd.DataFrame()

def actualizar_estado_orden(orden_id: int, nuevo_estado: str, usuario: str, sucursal: str):
    """Actualiza el estado de una orden de trabajo (ej: Pendiente -> Listo)."""
    try:
        if not supabase: return
        supabase.table("ordenes_trabajo").update({"estado": nuevo_estado}).eq("id", orden_id).execute()
        registrar_auditoria("Cambio de Estado", "Orden de Trabajo", f"Orden #{orden_id} pasó a {nuevo_estado}", usuario, sucursal=sucursal)
    except Exception as e:
        print(f"Error actualizar_estado_orden: {e}")

def cargar_orden_trabajo_detallada(orden_id: int):
    """Carga una orden específica con todos sus detalles."""
    try:
        if not supabase: return None
        res = supabase.table("ordenes_trabajo").select("*").eq("id", orden_id).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        print(f"Error cargar_orden_trabajo_detallada: {e}")
        return None

# ══════════════════════════════════════════════════════════════
# CITAS
# ══════════════════════════════════════════════════════════════
@cache_data(ttl=300, show_spinner=False)
def cargar_citas_hoy(sucursal: str = None) -> pd.DataFrame:
    """Carga las citas agendadas para el día actual."""
    try:
        if not supabase: return pd.DataFrame()
        hoy = pd.Timestamp.now().strftime("%Y-%m-%d")
        query = supabase.table("citas").select("*").eq("fecha", hoy)
        if sucursal and sucursal != "Todas":
            query = query.eq("sucursal", sucursal)
        res = query.order("hora").execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception as e:
        print(f"Error cargar_citas_hoy: {e}")
        return pd.DataFrame()

@cache_data(ttl=300, show_spinner=False)
def cargar_todas_citas(sucursal: str = None) -> pd.DataFrame:
    """Carga todas las citas."""
    try:
        if not supabase: return pd.DataFrame()
        query = supabase.table("citas").select("*")
        if sucursal and sucursal != "Todas":
            query = query.eq("sucursal", sucursal)
        res = query.order("fecha").order("hora").execute()
        return pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception as e:
        print(f"Error cargar_todas_citas: {e}")
        return pd.DataFrame()

# Alias para compatibilidad con rama cloud
cargar_citas = cargar_todas_citas

def guardar_cita(data: dict):
    """Guarda o actualiza una cita en la base de datos."""
    try:
        if not supabase: return None
        if "id" in data and data["id"]:
            res = supabase.table("citas").update(data).eq("id", data["id"]).execute()
        else:
            res = supabase.table("citas").insert(data).execute()
        try:
            import streamlit as st
            st.cache_data.clear()
        except:
            pass
        registrar_auditoria("Agendar Cita", "Citas", f"Cita {data.get('motivo', '')} para {data.get('paciente_nombre', '')}", st.session_state.get("user_login", "desconocido"), sucursal=data.get("sucursal", ""))
        if res.data:
            return res.data[0].get("id")
        return True
    except Exception as e:
        print(f"Error guardar_cita: {e}")
        return None

def eliminar_cita(cita_id: int, sucursal: str = "Matriz"):
    """Elimina una cita."""
    try:
        if not supabase: return False
        supabase.table("citas").delete().eq("id", cita_id).execute()
        try:
            import streamlit as st
            st.cache_data.clear()
        except:
            pass
        registrar_auditoria("Eliminar Cita", "Citas", f"Cita eliminada", st.session_state.get("user_login", "desconocido"), sucursal=sucursal)
        return True
    except Exception as e:
        print(f"Error eliminar_cita: {e}")
        return False


# ══════════════════════════════════════════════════════════════
# HISTORIAS CLÍNICAS — LENTES DE CONTACTO
# ══════════════════════════════════════════════════════════════

HISTORIAS_LC_COLS = [
    "id", "paciente_id", "paciente_nombre", "fecha", "sucursal",
    "optometrista", "optometrista_login",
    # Bloque 1 — Anamnesis
    "lc_usuario_previo", "lc_tipo_lente_ant", "lc_marca_ant",
    "lc_horas_uso", "lc_solucion_habitual", "lc_motivo_consulta",
    # Bloque 2 — Examen preliminar
    "lc_avsc_od", "lc_avsc_oi",
    "lc_rx_od", "lc_rx_oi",
    "lc_distancia_vertice",
    "lc_kera_od", "lc_kera_oi",
    "lc_astig_corneal_od", "lc_astig_corneal_oi",
    # Bloque 3 — Biomicroscopía
    "lc_parpados", "lc_conjuntiva", "lc_eversion", "lc_cornea",
    "lc_but_od", "lc_but_oi", "lc_menisco",
    # Bloque 4 — Lente de prueba
    "lc_prueba_tipo", "lc_prueba_od", "lc_prueba_oi",
    "lc_centrado", "lc_movimiento", "lc_pushup", "lc_rotacion",
    "lc_sobre_od", "lc_sobre_oi",
    # Bloque 5 — Lente definitivo
    "lc_final_od", "lc_final_oi",
    "lc_marca_final", "lc_modalidad", "lc_regimen", "lc_solucion_final",
    # Bloque 6 — Entrega y educación
    "lc_insercion", "lc_fecha_entrega", "lc_proximo_control", "lc_observaciones",
    "recomendaciones"
]


@cache_data(ttl=300, show_spinner=False)
def cargar_historias_lc() -> pd.DataFrame:
    """Carga todas las historias de Lentes de Contacto desde Supabase."""
    try:
        if not supabase:
            return pd.DataFrame(columns=HISTORIAS_LC_COLS)
        response = supabase.table("historias_lc").select("*").order("fecha", desc=True).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            for col in HISTORIAS_LC_COLS:
                if col not in df.columns:
                    df[col] = ""
            return df
        return pd.DataFrame(columns=HISTORIAS_LC_COLS)
    except Exception as e:
        print(f"Error cargar_historias_lc: {e}")
        return pd.DataFrame(columns=HISTORIAS_LC_COLS)


def guardar_historia_lc(row: dict) -> bool:
    """Inserta una nueva historia de LC en Supabase."""
    try:
        if not supabase: return False
        payload = {k: v for k, v in row.items() if k != "id"}
        supabase.table("historias_lc").insert(payload).execute()
        try:
            cargar_historias_lc.clear()
        except:
            pass
        return True
    except Exception as e:
        print(f"Error guardar_historia_lc: {e}")
        return False


def actualizar_historia_lc(historia_id, data: dict) -> bool:
    """Actualiza una historia de LC existente."""
    try:
        if not supabase: return False
        payload = {k: v for k, v in data.items() if k not in ("id", "created_at")}
        supabase.table("historias_lc").update(payload).eq("id", historia_id).execute()
        try:
            cargar_historias_lc.clear()
        except:
            pass
        return True
    except Exception as e:
        print(f"Error actualizar_historia_lc: {e}")
        return False


def eliminar_historia_lc(h_id) -> bool:
    """Elimina una historia de LC."""
    try:
        if not supabase: return False
        supabase.table("historias_lc").delete().eq("id", h_id).execute()
        try:
            cargar_historias_lc.clear()
        except:
            pass
        return True
    except Exception as e:
        print(f"Error eliminar_historia_lc: {e}")
        return False

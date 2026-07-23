import json
import os
import urllib.error
import urllib.request

import pandas as pd
import streamlit as st

from database import (
    cargar_inventario,
    cargar_ordenes_trabajo,
    cargar_todas_citas,
    cargar_ventas_historial,
)


SUGGESTED_QUESTIONS = [
    "Genera un resumen gerencial del mes",
    "Que productos tienen inventario critico?",
    "Cual fue mi utilidad este mes?",
    "Que pacientes necesitan seguimiento?",
    "Quienes tienen saldo pendiente?",
    "Como estuvo el negocio hoy?",
]


SYSTEM_PROMPT = """
Eres HappyVision AI, un asistente administrativo, financiero, comercial y clinico para una optica.

Tu objetivo es ayudar al usuario a tomar decisiones usando los datos reales disponibles del sistema.

Reglas:
1. No inventes datos. Si una metrica no esta disponible, dilo claramente.
2. Responde en espanol claro, ejecutivo y profesional.
3. Cuando haya analisis financiero, muestra metricas, lectura del resultado y recomendaciones.
4. Cuando haya temas clinicos, organiza informacion y sugiere seguimiento, pero no diagnostiques.
5. Prioriza acciones concretas: cobrar saldos, reponer inventario, contactar pacientes o revisar gastos.
6. Manten confidencialidad y evita exponer datos sensibles si el contexto no los incluye.
"""


def render_ai_assistant():
    """Renders the HappyVision AI assistant as a floating button on the bottom right."""
    _init_ai_state()
    _inject_styles()

    st.markdown("<span id='ai-popover-anchor'></span>", unsafe_allow_html=True)
    
    with st.popover("🤖", help="Habla con la IA"):
        st.markdown(
            """
            <div class="hv-ai-panel-title">
                <span>HappyVision AI</span>
                <small>Gerente virtual</small>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption("Preguntas sugeridas")
        for question in SUGGESTED_QUESTIONS:
            if st.button(question, key=f"hv_ai_suggestion_{question}", use_container_width=True):
                _ask_ai(question)
                st.rerun()

        if st.session_state.hv_ai_messages:
            st.markdown("<div class='hv-ai-history'>", unsafe_allow_html=True)
            for message in st.session_state.hv_ai_messages[-6:]:
                role_class = "user" if message["role"] == "user" else "assistant"
                role_label = "Tú" if role_class == "user" else "HappyVision AI"
                st.markdown(
                    f"""
                    <div class="hv-ai-message {role_class}">
                        <strong>{role_label}</strong>
                        <div>{_markdown_to_safe_html(message["content"])}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

        with st.form("hv_ai_form", clear_on_submit=True, border=False):
            question = st.text_area(
                "Pregunta",
                placeholder="Ej: ¿Cómo estuvo el negocio este mes?",
                label_visibility="collapsed",
                height=88,
            )
            col_send, col_clear = st.columns([2, 1])
            submitted = col_send.form_submit_button("Preguntar", type="primary", use_container_width=True)
            cleared = col_clear.form_submit_button("Limpiar", use_container_width=True)

        if cleared:
            st.session_state.hv_ai_messages = []
            st.rerun()

        if submitted and question.strip():
            _ask_ai(question.strip())
            st.rerun()


def _init_ai_state():
    if "hv_ai_messages" not in st.session_state:
        st.session_state.hv_ai_messages = []


def _inject_styles():
    st.markdown(
        """
        <style>
        /* Contenedor del popover para posicionarlo */
        div[data-testid="stElementContainer"]:has(#ai-popover-anchor) + div[data-testid="stElementContainer"] {
            position: fixed !important;
            bottom: 30px !important;
            right: 30px !important;
            z-index: 9999 !important;
        }
        
        /* Estilos del botón redondo de la IA */
        div[data-testid="stElementContainer"]:has(#ai-popover-anchor) + div[data-testid="stElementContainer"] button[data-testid="baseButton-popover"] {
            border-radius: 50% !important;
            width: 65px !important;
            height: 65px !important;
            background: linear-gradient(135deg, #3b82f6 0%, #1e3a8a 100%) !important;
            color: white !important;
            box-shadow: 0 8px 25px rgba(37, 99, 235, 0.4) !important;
            border: none !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            transition: all 0.3s ease !important;
        }
        
        div[data-testid="stElementContainer"]:has(#ai-popover-anchor) + div[data-testid="stElementContainer"] button[data-testid="baseButton-popover"]:hover {
            transform: scale(1.1) translateY(-5px) !important;
            box-shadow: 0 12px 30px rgba(37, 99, 235, 0.6) !important;
        }

        div[data-testid="stElementContainer"]:has(#ai-popover-anchor) + div[data-testid="stElementContainer"] button[data-testid="baseButton-popover"] p {
            font-size: 32px !important;
            margin: 0 !important;
            padding: 0 !important;
            line-height: 1 !important;
        }

        /* Estilos del interior del panel */
        div[data-testid="stPopoverBody"] {
            width: 380px !important;
            max-height: 80vh !important;
            border-radius: 16px !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2) !important;
            border: 1px solid #e2e8f0 !important;
            padding: 1rem !important;
        }

        .hv-ai-panel-title {
            background: linear-gradient(135deg, #0f172a, #1e3a8a);
            border: 1px solid rgba(59, 130, 246, 0.35);
            border-radius: 12px;
            padding: 12px 14px;
            color: white;
            margin-bottom: 10px;
            box-shadow: 0 8px 18px rgba(15, 23, 42, 0.18);
        }
        .hv-ai-panel-title span {
            display: block;
            font-weight: 800;
            font-size: 15px;
        }
        .hv-ai-panel-title small {
            color: #bfdbfe;
            font-size: 11px;
        }
        .hv-ai-history {
            max-height: 360px;
            overflow-y: auto;
            padding-right: 4px;
        }
        .hv-ai-message {
            border-radius: 10px;
            padding: 10px 11px;
            margin: 8px 0;
            font-size: 12px;
            line-height: 1.45;
            border: 1px solid #e2e8f0;
        }
        .hv-ai-message strong {
            display: block;
            margin-bottom: 4px;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .hv-ai-message.user {
            background: #eff6ff;
            color: #172554;
            border-color: #bfdbfe;
        }
        .hv-ai-message.assistant {
            background: #ffffff;
            color: #1e293b;
        }
        .hv-ai-message ul {
            margin: 6px 0 6px 18px;
            padding: 0;
        }
        .hv-ai-message p {
            margin: 5px 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _ask_ai(question: str):
    st.session_state.hv_ai_messages.append({"role": "user", "content": question})
    with st.spinner("HappyVision AI esta analizando los datos..."):
        answer = answer_question(question)
    st.session_state.hv_ai_messages.append({"role": "assistant", "content": answer})


def answer_question(question: str) -> str:
    sucursal = st.session_state.get("sucursal_activa", "Matriz")
    data = _load_business_data(sucursal)
    metrics = _build_metrics(data, sucursal)
    local_answer = _local_answer(question, metrics)

    api_key = _get_secret("OPENAI_API_KEY")
    if not api_key:
        return (
            f"{local_answer}\n\n"
            "_Modo local activo: configura `OPENAI_API_KEY` en variables de entorno o Streamlit Secrets "
            "para activar respuestas redactadas por IA._"
        )

    try:
        return _openai_answer(question, metrics, local_answer, api_key)
    except Exception as exc:
        return (
            f"{local_answer}\n\n"
            f"_No pude conectar con OpenAI ahora mismo. La respuesta anterior fue calculada localmente. Detalle: {exc}_"
        )


def _load_business_data(sucursal: str) -> dict:
    pacientes = st.session_state.get("df_pacientes", pd.DataFrame()).copy()
    historias = st.session_state.get("df_historias", pd.DataFrame()).copy()

    data = {
        "pacientes": _filter_sucursal(pacientes, sucursal),
        "historias": _filter_sucursal(historias, sucursal),
        "inventario": cargar_inventario(sucursal),
        "ventas": cargar_ventas_historial(sucursal),
        "ordenes": cargar_ordenes_trabajo(sucursal),
        "citas": cargar_todas_citas(sucursal),
    }
    return data


def _filter_sucursal(df: pd.DataFrame, sucursal: str) -> pd.DataFrame:
    if df is None or df.empty or "sucursal" not in df.columns:
        return df if df is not None else pd.DataFrame()
    return df[df["sucursal"].astype(str) == str(sucursal)].copy()


def _build_metrics(data: dict, sucursal: str) -> dict:
    today = pd.Timestamp.today().normalize()
    month_start = today.replace(day=1)
    prev_month_end = month_start - pd.Timedelta(days=1)
    prev_month_start = prev_month_end.replace(day=1)

    pacientes = data["pacientes"]
    historias = _with_datetime(data["historias"], "fecha", "fecha_dt")
    inventario = data["inventario"].copy()
    ventas = _with_datetime(data["ventas"], "fecha", "fecha_dt")
    ordenes = _with_datetime(data["ordenes"], "creado_el", "creado_dt")
    citas = _with_datetime(data["citas"], "fecha", "fecha_dt")

    ventas = _prepare_numeric(ventas, ["total", "costo_total", "abono", "saldo"])
    inventario = _prepare_numeric(inventario, ["cantidad_disponible", "stock", "stock_minimo", "precio_venta", "costo_compra"])
    ordenes = _prepare_numeric(ordenes, ["saldo", "abono", "total_venta"])

    ventas_mes = ventas[ventas["fecha_dt"] >= month_start] if "fecha_dt" in ventas.columns else ventas.iloc[0:0]
    ventas_mes_ant = ventas[
        (ventas["fecha_dt"] >= prev_month_start) & (ventas["fecha_dt"] < month_start)
    ] if "fecha_dt" in ventas.columns else ventas.iloc[0:0]
    ventas_hoy = ventas[ventas["fecha_dt"].dt.date == today.date()] if "fecha_dt" in ventas.columns else ventas.iloc[0:0]

    consultas_mes = historias[historias["fecha_dt"] >= month_start] if "fecha_dt" in historias.columns else historias.iloc[0:0]
    citas_hoy = citas[citas["fecha_dt"].dt.date == today.date()] if "fecha_dt" in citas.columns else citas.iloc[0:0]
    citas_futuras = citas[citas["fecha_dt"] >= today] if "fecha_dt" in citas.columns else citas.iloc[0:0]

    stock_col = "cantidad_disponible" if "cantidad_disponible" in inventario.columns else "stock"
    if stock_col not in inventario.columns:
        inventario[stock_col] = 0
    min_col = "stock_minimo" if "stock_minimo" in inventario.columns else None
    low_mask = inventario[stock_col] <= (inventario[min_col] if min_col else 3)
    low_stock = inventario[low_mask].copy() if not inventario.empty else pd.DataFrame()
    inventario["valor_venta_stock"] = inventario.get("precio_venta", 0) * inventario.get(stock_col, 0)
    inventario["valor_costo_stock"] = inventario.get("costo_compra", 0) * inventario.get(stock_col, 0)

    pendientes = ordenes[ordenes.get("estado", "").astype(str).str.lower().isin(["pendiente", "en laboratorio", "listo para entrega"])] if not ordenes.empty and "estado" in ordenes.columns else pd.DataFrame()
    saldos_ventas = ventas[ventas.get("saldo", 0) > 0] if not ventas.empty and "saldo" in ventas.columns else pd.DataFrame()
    saldos_ordenes = ordenes[ordenes.get("saldo", 0) > 0] if not ordenes.empty and "saldo" in ordenes.columns else pd.DataFrame()

    total_mes = float(ventas_mes.get("total", pd.Series(dtype=float)).sum())
    costo_mes = float(ventas_mes.get("costo_total", pd.Series(dtype=float)).sum())
    utilidad_mes = total_mes - costo_mes
    total_mes_ant = float(ventas_mes_ant.get("total", pd.Series(dtype=float)).sum())
    variacion_mes = ((total_mes - total_mes_ant) / total_mes_ant * 100) if total_mes_ant else None

    metrics = {
        "sucursal": sucursal,
        "fecha": today.strftime("%Y-%m-%d"),
        "ventas_hoy": float(ventas_hoy.get("total", pd.Series(dtype=float)).sum()),
        "ventas_mes": total_mes,
        "costos_mes": costo_mes,
        "utilidad_mes": utilidad_mes,
        "margen_mes": (utilidad_mes / total_mes * 100) if total_mes else 0,
        "ventas_mes_anterior": total_mes_ant,
        "variacion_ventas_mes_pct": variacion_mes,
        "ticket_promedio_mes": (total_mes / len(ventas_mes)) if len(ventas_mes) else 0,
        "transacciones_mes": int(len(ventas_mes)),
        "pacientes_total": int(len(pacientes)),
        "historias_total": int(len(historias)),
        "pacientes_atendidos_mes": _count_people(consultas_mes),
        "citas_hoy": int(len(citas_hoy)),
        "citas_pendientes_hoy": int(len(citas_hoy[citas_hoy.get("estado", "").astype(str) == "Pendiente"])) if not citas_hoy.empty and "estado" in citas_hoy.columns else 0,
        "citas_proximas": int(len(citas_futuras)),
        "inventario_total_productos": int(len(inventario)),
        "inventario_unidades": float(inventario.get(stock_col, pd.Series(dtype=float)).sum()),
        "inventario_valor_venta": float(inventario.get("valor_venta_stock", pd.Series(dtype=float)).sum()),
        "inventario_valor_costo": float(inventario.get("valor_costo_stock", pd.Series(dtype=float)).sum()),
        "inventario_bajo_stock_count": int(len(low_stock)),
        "productos_bajo_stock": _rows_to_records(low_stock, ["codigo_referencia", "nombre", "marca", stock_col, "precio_venta"], limit=8),
        "ordenes_pendientes_count": int(len(pendientes)),
        "ordenes_por_estado": _value_counts(ordenes, "estado"),
        "saldo_pendiente_total": float(saldos_ventas.get("saldo", pd.Series(dtype=float)).sum() + saldos_ordenes.get("saldo", pd.Series(dtype=float)).sum()),
        "clientes_con_saldo": _saldo_records(saldos_ventas, saldos_ordenes),
        "pacientes_seguimiento": _follow_up_records(historias),
        "productos_mas_vendidos": _top_sold_products(ventas_mes),
    }
    return metrics


def _with_datetime(df: pd.DataFrame, source_col: str, target_col: str) -> pd.DataFrame:
    df = df.copy()
    if source_col in df.columns:
        df[target_col] = pd.to_datetime(df[source_col], errors="coerce")
    return df


def _prepare_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    df = df.copy()
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


def _count_people(df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    for col in ["paciente_id", "paciente_nombre", "nombre"]:
        if col in df.columns:
            return int(df[col].astype(str).replace("", pd.NA).dropna().nunique())
    return int(len(df))


def _value_counts(df: pd.DataFrame, col: str) -> dict:
    if df.empty or col not in df.columns:
        return {}
    return {str(k): int(v) for k, v in df[col].fillna("Sin estado").value_counts().items()}


def _rows_to_records(df: pd.DataFrame, columns: list[str], limit: int = 5) -> list[dict]:
    if df.empty:
        return []
    available = [col for col in columns if col in df.columns]
    if not available:
        return []
    return df[available].head(limit).fillna("").to_dict(orient="records")


def _saldo_records(ventas: pd.DataFrame, ordenes: pd.DataFrame) -> list[dict]:
    records = []
    if not ventas.empty:
        for _, row in ventas.sort_values("saldo", ascending=False).head(5).iterrows():
            records.append({
                "cliente": row.get("cliente", "Cliente"),
                "origen": "Venta",
                "saldo": float(row.get("saldo", 0)),
                "fecha": str(row.get("fecha", ""))[:10],
            })
    if not ordenes.empty:
        for _, row in ordenes.sort_values("saldo", ascending=False).head(5).iterrows():
            records.append({
                "cliente": row.get("paciente_nombre", "Paciente"),
                "origen": "Orden",
                "saldo": float(row.get("saldo", 0)),
                "fecha": str(row.get("creado_el", ""))[:10],
            })
    return sorted(records, key=lambda x: x["saldo"], reverse=True)[:8]


def _follow_up_records(historias: pd.DataFrame) -> list[dict]:
    if historias.empty or "fecha_dt" not in historias.columns:
        return []

    today = pd.Timestamp.today().normalize()
    name_col = "paciente_nombre" if "paciente_nombre" in historias.columns else "nombre"
    id_col = "paciente_id" if "paciente_id" in historias.columns else name_col
    if name_col not in historias.columns or id_col not in historias.columns:
        return []

    df = historias.dropna(subset=["fecha_dt"]).copy()
    if df.empty:
        return []
    df["meses_proximo_control"] = pd.to_numeric(df.get("meses_proximo_control", 12), errors="coerce").fillna(12)
    df = df.sort_values("fecha_dt", ascending=False).drop_duplicates(subset=[id_col])

    def due_date(row):
        months = int(row.get("meses_proximo_control", 12) or 12)
        return row["fecha_dt"] + pd.DateOffset(months=max(months, 1))

    df["proximo_control"] = df.apply(due_date, axis=1)
    due = df[df["proximo_control"] <= today + pd.Timedelta(days=30)].copy()
    due["dias_para_control"] = (due["proximo_control"] - today).dt.days
    due = due.sort_values("dias_para_control").head(8)

    records = []
    for _, row in due.iterrows():
        records.append({
            "paciente": row.get(name_col, "Paciente"),
            "ultima_consulta": row.get("fecha_dt").strftime("%Y-%m-%d") if pd.notna(row.get("fecha_dt")) else "",
            "proximo_control": row.get("proximo_control").strftime("%Y-%m-%d") if pd.notna(row.get("proximo_control")) else "",
            "dias": int(row.get("dias_para_control", 0)),
        })
    return records


def _top_sold_products(ventas: pd.DataFrame) -> list[dict]:
    if ventas.empty or "detalles" not in ventas.columns:
        return []

    counts = {}
    for details in ventas["detalles"].dropna():
        items = details
        if isinstance(details, str):
            try:
                items = json.loads(details)
            except Exception:
                items = [{"descripcion": details}]
        if isinstance(items, dict):
            items = [items]
        if not isinstance(items, list):
            continue
        for item in items:
            desc = str(item.get("descripcion", "Producto")).strip() if isinstance(item, dict) else str(item)
            if not desc:
                continue
            counts[desc] = counts.get(desc, 0) + 1

    return [{"producto": k, "ventas": v} for k, v in sorted(counts.items(), key=lambda item: item[1], reverse=True)[:5]]


def _local_answer(question: str, metrics: dict) -> str:
    q = question.lower()
    if any(word in q for word in ["inventario", "stock", "agot", "comprar", "reponer"]):
        return _inventory_answer(metrics)
    if any(word in q for word in ["utilidad", "ganancia", "rentabilidad", "margen"]):
        return _profit_answer(metrics)
    if any(word in q for word in ["seguimiento", "control", "regres", "pacientes"]):
        return _patients_answer(metrics)
    if any(word in q for word in ["saldo", "pendiente", "deben", "cobrar"]):
        return _balances_answer(metrics)
    if any(word in q for word in ["cita", "agenda"]):
        return _appointments_answer(metrics)
    return _executive_summary(metrics)


def _executive_summary(metrics: dict) -> str:
    variation = metrics["variacion_ventas_mes_pct"]
    variation_text = "sin comparativo disponible"
    if variation is not None:
        variation_text = f"{variation:+.1f}% vs. mes anterior"

    alerts = []
    if metrics["inventario_bajo_stock_count"]:
        alerts.append(f"{metrics['inventario_bajo_stock_count']} productos con inventario critico")
    if metrics["saldo_pendiente_total"] > 0:
        alerts.append(f"{_money(metrics['saldo_pendiente_total'])} en saldos pendientes")
    if metrics["pacientes_seguimiento"]:
        alerts.append(f"{len(metrics['pacientes_seguimiento'])} pacientes para seguimiento cercano")
    if not alerts:
        alerts.append("sin alertas criticas en los datos disponibles")

    return (
        f"**Resumen gerencial de {metrics['sucursal']}**\n\n"
        f"- Ventas del mes: **{_money(metrics['ventas_mes'])}** ({variation_text}).\n"
        f"- Utilidad estimada del mes: **{_money(metrics['utilidad_mes'])}** con margen de **{metrics['margen_mes']:.1f}%**.\n"
        f"- Ticket promedio: **{_money(metrics['ticket_promedio_mes'])}** en {metrics['transacciones_mes']} transacciones.\n"
        f"- Pacientes atendidos este mes: **{metrics['pacientes_atendidos_mes']}**.\n"
        f"- Inventario valorizado para venta: **{_money(metrics['inventario_valor_venta'])}**.\n\n"
        "**Alertas:**\n"
        + "\n".join(f"- {alert}." for alert in alerts)
        + "\n\n**Accion sugerida:** revisar saldos, contactar pacientes vencidos y reponer primero los productos de alta salida con stock bajo."
    )


def _inventory_answer(metrics: dict) -> str:
    products = metrics["productos_bajo_stock"]
    if not products:
        return (
            "**Inventario critico**\n\n"
            "No aparecen productos por debajo del minimo en los datos disponibles. "
            f"Inventario total: {metrics['inventario_unidades']:.0f} unidades valorizadas en {_money(metrics['inventario_valor_venta'])}."
        )

    lines = []
    for product in products:
        name = product.get("nombre", "Producto")
        code = product.get("codigo_referencia", "Sin codigo")
        stock = product.get("cantidad_disponible", product.get("stock", 0))
        lines.append(f"- {code} | {name}: **{stock}** unidades")

    return (
        f"**Inventario critico ({metrics['inventario_bajo_stock_count']} productos)**\n\n"
        + "\n".join(lines)
        + "\n\n**Recomendacion:** prioriza reposicion de estos codigos y revisa si alguno tiene ventas recientes antes de comprar volumen alto."
    )


def _profit_answer(metrics: dict) -> str:
    return (
        "**Rentabilidad del mes**\n\n"
        f"- Ingresos: **{_money(metrics['ventas_mes'])}**.\n"
        f"- Costos registrados: **{_money(metrics['costos_mes'])}**.\n"
        f"- Utilidad estimada: **{_money(metrics['utilidad_mes'])}**.\n"
        f"- Margen: **{metrics['margen_mes']:.1f}%**.\n"
        f"- Ticket promedio: **{_money(metrics['ticket_promedio_mes'])}**.\n\n"
        "**Lectura:** si los costos no se registran en todas las ventas, la utilidad puede estar sobreestimada. "
        "Para una lectura fina, registra costo de lunas, laboratorio y armazon en cada venta."
    )


def _patients_answer(metrics: dict) -> str:
    followups = metrics["pacientes_seguimiento"]
    if not followups:
        return (
            "**Pacientes y seguimiento**\n\n"
            f"- Pacientes registrados: **{metrics['pacientes_total']}**.\n"
            f"- Historias clinicas: **{metrics['historias_total']}**.\n"
            f"- Pacientes atendidos este mes: **{metrics['pacientes_atendidos_mes']}**.\n\n"
            "No encuentro pacientes con control vencido o cercano en los datos disponibles."
        )

    lines = []
    for row in followups:
        estado = "vencido" if row["dias"] < 0 else f"en {row['dias']} dias"
        lines.append(f"- {row['paciente']}: ultimo control {row['ultima_consulta']}, proximo {row['proximo_control']} ({estado})")

    return (
        "**Pacientes para seguimiento**\n\n"
        + "\n".join(lines)
        + "\n\n**Accion sugerida:** enviar recordatorio por WhatsApp y priorizar los controles vencidos."
    )


def _balances_answer(metrics: dict) -> str:
    balances = metrics["clientes_con_saldo"]
    if not balances:
        return "**Saldos pendientes**\n\nNo encuentro saldos pendientes en ventas u ordenes con los datos disponibles."

    lines = [f"- {row['cliente']} ({row['origen']} {row['fecha']}): **{_money(row['saldo'])}**" for row in balances]
    return (
        f"**Saldos pendientes: {_money(metrics['saldo_pendiente_total'])}**\n\n"
        + "\n".join(lines)
        + "\n\n**Accion sugerida:** contactar primero los saldos mas altos y registrar abonos en caja para mantener flujo."
    )


def _appointments_answer(metrics: dict) -> str:
    return (
        "**Agenda**\n\n"
        f"- Citas de hoy: **{metrics['citas_hoy']}**.\n"
        f"- Pendientes hoy: **{metrics['citas_pendientes_hoy']}**.\n"
        f"- Citas proximas registradas: **{metrics['citas_proximas']}**.\n\n"
        "Revisa la agenda si hay pendientes hoy para confirmar asistencia o reagendar temprano."
    )


def _openai_answer(question: str, metrics: dict, local_answer: str, api_key: str) -> str:
    share_patient_data = str(_get_secret("HAPPYVISION_AI_SHARE_PATIENT_DATA", "false")).lower() in {"1", "true", "yes", "si"}
    model = _get_secret("HAPPYVISION_AI_MODEL", "gpt-5.4-mini")
    safe_metrics = _metrics_for_model(metrics, include_private=share_patient_data)

    payload = {
        "model": model,
        "instructions": (
            SYSTEM_PROMPT
            + "\nDatos del sistema en JSON:\n"
            + json.dumps(safe_metrics, ensure_ascii=False, default=str)
            + "\n\nRespuesta local ya calculada:\n"
            + local_answer
        ),
        "input": question,
        "max_output_tokens": 900,
        "store": False,
    }

    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(_friendly_openai_error(exc.code, detail)) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError("sin conexion o timeout hacia la API") from exc

    text = _extract_response_text(body)
    if not text:
        raise RuntimeError("la API no devolvio texto util")
    return text


def _metrics_for_model(metrics: dict, include_private: bool) -> dict:
    allowed = dict(metrics)
    if not include_private:
        allowed["clientes_con_saldo"] = [{"total_registros": len(metrics.get("clientes_con_saldo", []))}]
        allowed["pacientes_seguimiento"] = [{"total_registros": len(metrics.get("pacientes_seguimiento", []))}]
    return allowed


def _extract_response_text(body: dict) -> str:
    if body.get("output_text"):
        return str(body["output_text"]).strip()

    parts = []
    for item in body.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                parts.append(content.get("text", ""))
    return "\n".join(part for part in parts if part).strip()


def _friendly_openai_error(status_code: int, detail: str) -> str:
    if status_code == 401:
        return "OPENAI_API_KEY invalida o ausente"
    if status_code == 429:
        return "limite o credito insuficiente en OpenAI"
    if status_code >= 500:
        return "error temporal de OpenAI"
    try:
        parsed = json.loads(detail)
        return parsed.get("error", {}).get("message", f"error HTTP {status_code}")
    except Exception:
        return f"error HTTP {status_code}"


def _get_secret(name: str, default: str | None = None) -> str | None:
    try:
        value = st.secrets.get(name)
        if value:
            return str(value)
    except Exception:
        pass
    return os.getenv(name, default)


def _money(value: float) -> str:
    try:
        return f"${float(value):,.2f}"
    except Exception:
        return "$0.00"


def _markdown_to_safe_html(text: str) -> str:
    import html
    import re

    escaped = html.escape(text)
    escaped = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = escaped.replace("\n", "<br>")
    return escaped

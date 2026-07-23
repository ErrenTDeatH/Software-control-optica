import streamlit as st
import pandas as pd
from datetime import datetime, date
from database import (
    obtener_estado_caja, abrir_caja, registrar_gasto,
    obtener_resumen_dia, cerrar_caja, cargar_sucursales,
    cargar_ventas_historial, cargar_ordenes_trabajo, registrar_pago_saldo
)
from database_facturas import cargar_cuentas_por_cobrar

import plotly.graph_objects as go
import plotly.express as px


def render_contabilidad():
    st.markdown("""
        <style>
        .kpi-card {
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px 15px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        .kpi-label { font-size: 12px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
        .kpi-value { font-size: 26px; font-weight: 800; }
        .kpi-green  { color: #16a34a; }
        .kpi-blue   { color: #2563eb; }
        .kpi-red    { color: #dc2626; }
        .kpi-amber  { color: #d97706; }
        .cobrar-row {
            background: white;
            border: 1px solid #fde68a;
            border-left: 4px solid #f59e0b;
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 8px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="page-header">
            <h1 style='margin:0; color:#1e293b;'>💰 Gestión Financiera y Rentabilidad</h1>
            <p style='margin:5px 0 0 0; color:#64748b;'>Control de caja diaria, análisis de ganancias y cuentas por cobrar</p>
        </div>
    """, unsafe_allow_html=True)

    sucursal = st.session_state.get("sucursal_activa", "Matriz")
    es_admin = st.session_state.get("user_role") == "Administrador"
    hoy = date.today().strftime("%Y-%m-%d")

    tabs = st.tabs(["💵 Caja Diaria", "📊 Rentabilidad", "🔴 Cuentas por Cobrar"])

    # ══════════════════════════════════════════════════════════════
    # TAB 1: CAJA DIARIA
    # ══════════════════════════════════════════════════════════════
    with tabs[0]:
        caja = obtener_estado_caja(sucursal, hoy)

        if not caja:
            st.markdown(f"""
                <div style='background:#fff7ed; border:1px solid #fed7aa; border-radius:12px; padding:30px; text-align:center; margin:20px 0;'>
                    <h3 style='color:#92400e; margin:0;'>🔒 Caja Cerrada</h3>
                    <p style='color:#78350f; margin:10px 0 0 0;'>Debes abrir la caja de <b>{sucursal}</b> para empezar a registrar movimientos del día.</p>
                </div>
            """, unsafe_allow_html=True)
            col_btn = st.columns([1, 2, 1])
            with col_btn[1]:
                monto_aper = st.number_input("💵 Monto inicial en caja ($):", min_value=0.0, step=1.0, key="monto_aper")
                if st.button("🔓 Abrir Caja Ahora", type="primary", use_container_width=True):
                    abrir_caja({
                        "fecha": hoy,
                        "sucursal": sucursal,
                        "monto_apertura": monto_aper,
                        "estado": "Abierta",
                        "abierta_por": st.session_state.get("user_login", "admin")
                    })
                    st.success("✅ Caja abierta correctamente.")
                    st.rerun()
        else:
            # RESUMEN DEL DÍA
            res = obtener_resumen_dia(sucursal, hoy)
            total_ingresos = res["Efectivo"] + res["Tarjeta"] + res["Transferencia"]
            utilidad_bruta = total_ingresos - res["Gastos"]

            k1, k2, k3, k4 = st.columns(4)
            with k1:
                st.markdown(f'<div class="kpi-card"><div class="kpi-label">Ingresos Hoy</div><div class="kpi-value kpi-blue">${total_ingresos:,.2f}</div></div>', unsafe_allow_html=True)
            with k2:
                st.markdown(f'<div class="kpi-card"><div class="kpi-label">Efectivo</div><div class="kpi-value kpi-green">${res["Efectivo"]:,.2f}</div></div>', unsafe_allow_html=True)
            with k3:
                st.markdown(f'<div class="kpi-card"><div class="kpi-label">Gastos Hoy</div><div class="kpi-value kpi-red">${res["Gastos"]:,.2f}</div></div>', unsafe_allow_html=True)
            with k4:
                color = "kpi-green" if utilidad_bruta >= 0 else "kpi-red"
                st.markdown(f'<div class="kpi-card"><div class="kpi-label">Utilidad Bruta</div><div class="kpi-value {color}">${utilidad_bruta:,.2f}</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            col_gastos, col_desglose = st.columns([1, 1])

            with col_gastos:
                st.subheader("📝 Registrar Gasto")
                with st.form("form_gasto_diario"):
                    cat = st.selectbox("Categoría", ["Lunas/Lab", "Armazones", "Sueldos", "Servicios Básicos", "Arriendo", "Publicidad", "Mantenimiento", "Otros"])
                    concepto = st.text_input("Concepto / Descripción")
                    monto_g = st.number_input("Monto ($)", min_value=0.0, step=0.50)
                    if st.form_submit_button("💾 Registrar Gasto", type="primary", use_container_width=True):
                        if monto_g > 0:
                            registrar_gasto({
                                "fecha": hoy,
                                "sucursal": sucursal,
                                "categoria": cat,
                                "concepto": concepto or cat,
                                "monto": monto_g,
                                "usuario": st.session_state.get("user_login", "admin")
                            })
                            st.success(f"✅ Gasto ${monto_g:.2f} registrado.")
                            st.rerun()
                        else:
                            st.warning("Ingresa un monto mayor a $0.")

            with col_desglose:
                st.subheader("💳 Desglose por Método de Pago")
                metodos = {
                    "Efectivo": res["Efectivo"],
                    "Tarjeta": res["Tarjeta"],
                    "Transferencia": res["Transferencia"]
                }
                df_met = pd.DataFrame(list(metodos.items()), columns=["Método", "Monto"])
                if df_met["Monto"].sum() > 0:
                    fig = px.pie(df_met, names="Método", values="Monto",
                                 color_discrete_sequence=["#2563eb", "#16a34a", "#f59e0b"],
                                 hole=0.45)
                    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=250,
                                      showlegend=True, legend=dict(orientation="h", y=-0.1))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Sin ingresos registrados hoy.")

            # CIERRE DE CAJA
            if es_admin and caja.get("estado") == "Abierta":
                st.markdown("---")
                with st.expander("🔒 Cerrar Caja del Día"):
                    monto_cierre = st.number_input("Monto físico en caja al cierre ($):", min_value=0.0, step=1.0)
                    notas_cierre = st.text_area("Observaciones del cierre:")
                    if st.button("🔒 Confirmar Cierre de Caja", type="primary"):
                        diferencia = monto_cierre - (float(caja.get("monto_apertura", 0)) + total_ingresos - res["Gastos"])
                        cerrar_caja(caja["id"], {
                            "estado": "Cerrada",
                            "monto_cierre": monto_cierre,
                            "diferencia": diferencia,
                            "notas": notas_cierre,
                            "cerrada_por": st.session_state.get("user_login", "admin"),
                            "sucursal": sucursal
                        })
                        st.success("✅ Caja cerrada correctamente.")
                        st.rerun()

    # ══════════════════════════════════════════════════════════════
    # TAB 2: RENTABILIDAD
    # ══════════════════════════════════════════════════════════════
    with tabs[1]:
        if not es_admin:
            st.error("🔒 El reporte de rentabilidad solo es visible para el Administrador.")
        else:
            st.subheader("📊 Estado de Resultados")

            c_f1, c_f2, c_f3 = st.columns(3)
            df_suc = cargar_sucursales()
            suc_opts = ["Todas"] + (df_suc["nombre"].tolist() if not df_suc.empty else ["Matriz"])
            suc_sel = c_f1.selectbox("Sucursal:", suc_opts, key="cont_suc")
            mes_nombres = ["Todos", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                           "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
            mes_sel = c_f2.selectbox("Mes:", mes_nombres, index=datetime.now().month, key="cont_mes")
            anio_sel = c_f3.selectbox("Año:", [2024, 2025, 2026], index=[2024,2025,2026].index(datetime.now().year) if datetime.now().year in [2024,2025,2026] else 1, key="cont_anio")

            df_v = cargar_ventas_historial(suc_sel if suc_sel != "Todas" else None)

            if df_v.empty:
                st.info("📭 No hay datos de ventas para este período.")
            else:
                df_v["fecha_dt"] = pd.to_datetime(df_v["fecha"], errors="coerce")
                meses_map = {"Enero":1,"Febrero":2,"Marzo":3,"Abril":4,"Mayo":5,"Junio":6,
                             "Julio":7,"Agosto":8,"Septiembre":9,"Octubre":10,"Noviembre":11,"Diciembre":12}

                df_f = df_v[df_v["fecha_dt"].dt.year == anio_sel]
                if mes_sel != "Todos":
                    df_f = df_f[df_f["fecha_dt"].dt.month == meses_map[mes_sel]]

                ingresos = df_f["total"].astype(float).sum() if "total" in df_f.columns else 0
                costos = df_f["costo_total"].astype(float).sum() if "costo_total" in df_f.columns else 0
                ganancia = ingresos - costos
                margen = (ganancia / ingresos * 100) if ingresos > 0 else 0

                k1, k2, k3, k4 = st.columns(4)
                with k1:
                    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Ingresos Brutos</div><div class="kpi-value kpi-blue">${ingresos:,.2f}</div></div>', unsafe_allow_html=True)
                with k2:
                    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Costos (Lab/Mat)</div><div class="kpi-value kpi-red">${costos:,.2f}</div></div>', unsafe_allow_html=True)
                with k3:
                    color = "kpi-green" if ganancia >= 0 else "kpi-red"
                    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Ganancia Neta</div><div class="kpi-value {color}">${ganancia:,.2f}</div></div>', unsafe_allow_html=True)
                with k4:
                    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Margen de Ganancia</div><div class="kpi-value kpi-green">{margen:.1f}%</div></div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Gráfico de tendencia
                if not df_f.empty:
                    df_f["fecha_dia"] = df_f["fecha_dt"].dt.date
                    df_daily = df_f.groupby("fecha_dia").agg(
                        Ingresos=("total", "sum"),
                        Costos=("costo_total", "sum") if "costo_total" in df_f.columns else ("total", lambda x: 0)
                    ).reset_index()
                    df_daily["Ganancia"] = df_daily["Ingresos"] - df_daily["Costos"]

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df_daily["fecha_dia"], y=df_daily["Ingresos"],
                                             name="Ingresos", fill="tozeroy", line=dict(color="#2563eb", width=2)))
                    fig.add_trace(go.Scatter(x=df_daily["fecha_dia"], y=df_daily["Ganancia"],
                                             name="Ganancia", fill="tozeroy", line=dict(color="#16a34a", width=2)))
                    fig.update_layout(height=280, margin=dict(t=20, b=20, l=0, r=0),
                                      legend=dict(orientation="h", y=1.1),
                                      plot_bgcolor="white", paper_bgcolor="white",
                                      yaxis=dict(gridcolor="#f1f5f9"))
                    st.plotly_chart(fig, use_container_width=True)

                # Gráfico por método de pago del período
                if "metodo_pago" in df_f.columns:
                    df_met = df_f.groupby("metodo_pago")["total"].sum().reset_index()
                    col_chart, col_table = st.columns([1, 2])
                    with col_chart:
                        fig2 = px.bar(df_met, x="metodo_pago", y="total",
                                      title="Ingresos por Método de Pago",
                                      color="metodo_pago",
                                      color_discrete_sequence=px.colors.qualitative.Set2)
                        fig2.update_layout(height=280, margin=dict(t=40, b=0, l=0, r=0), showlegend=False)
                        st.plotly_chart(fig2, use_container_width=True)
                    with col_table:
                        with st.expander("📋 Detalle de Transacciones", expanded=False):
                            cols_show = [c for c in ["fecha", "cliente", "total", "costo_total", "metodo_pago", "sucursal"] if c in df_f.columns]
                            st.dataframe(df_f[cols_show], use_container_width=True, hide_index=True)

                # Botones de exportar (CSV y Excel)
                csv = df_f[[c for c in ["fecha", "cliente", "total", "costo_total", "metodo_pago", "sucursal"] if c in df_f.columns]].to_csv(index=False).encode("utf-8")
                
                # --- GENERAR EXCEL CON OPENPYXL ---
                import io
                excel_buffer = io.BytesIO()
                try:
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        # Hoja 1: Detalle de Ventas
                        df_excel = df_f[[c for c in ["fecha", "cliente", "total", "costo_total", "metodo_pago", "sucursal"] if c in df_f.columns]].copy()
                        if "total" in df_excel.columns and "costo_total" in df_excel.columns:
                            df_excel["ganancia"] = df_excel["total"].astype(float) - df_excel["costo_total"].astype(float)
                        df_excel.to_excel(writer, sheet_name="Detalle de Ventas", index=False)
                        
                        # Hoja 2: Resumen Ejecutivo
                        resumen_data = {
                            "Métrica": ["Ingresos Brutos", "Costos (Lab/Mat)", "Ganancia Neta", "Margen de Ganancia Promedio"],
                            "Valor": [f"${ingresos:,.2f}", f"${costos:,.2f}", f"${ganancia:,.2f}", f"{margen:.1f}%"]
                        }
                        pd.DataFrame(resumen_data).to_excel(writer, sheet_name="Resumen Ejecutivo", index=False)
                    excel_data = excel_buffer.getvalue()
                except Exception as e:
                    excel_data = None
                    print(f"Error generando Excel: {e}")
                
                c_exp1, c_exp2 = st.columns(2)
                c_exp1.download_button("📥 Exportar Reporte CSV", data=csv,
                                   file_name=f"Reporte_{sucursal}_{mes_sel}_{anio_sel}.csv",
                                   mime="text/csv", use_container_width=True)
                if excel_data:
                    c_exp2.download_button("📊 Descargar Reporte Excel (.xlsx)", data=excel_data,
                                       file_name=f"Reporte_Financiero_{sucursal}_{mes_sel}_{anio_sel}.xlsx",
                                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                       use_container_width=True)

    # ══════════════════════════════════════════════════════════════
    # TAB 3: CUENTAS POR COBRAR
    # ══════════════════════════════════════════════════════════════
    with tabs[2]:
        st.subheader("🔴 Saldos Pendientes de Cobro")
        st.caption("Órdenes de trabajo entregadas con saldo sin saldar.")

        df_cobrar = cargar_cuentas_por_cobrar(sucursal if sucursal != "Todas" else None)

        if df_cobrar.empty:
            st.success("✅ ¡Sin cuentas pendientes! Todo al día.")
        else:
            total_pendiente = df_cobrar["saldo"].astype(float).sum() if "saldo" in df_cobrar.columns else 0
            st.markdown(f"""
                <div style='background:#fff7ed; border:1px solid #fed7aa; border-radius:10px; padding:15px; margin-bottom:20px;'>
                    <b style='color:#92400e;'>⚠️ Total por cobrar: <span style='font-size:20px;'>${total_pendiente:,.2f}</span></b>
                    &nbsp;·&nbsp; {len(df_cobrar)} registro(s) pendiente(s)
                </div>
            """, unsafe_allow_html=True)

            for _, row in df_cobrar.iterrows():
                with st.container():
                    r1, r2, r3, r4 = st.columns([3, 1.5, 1.5, 1.5])
                    r1.markdown(f"**{row.get('paciente_nombre', row.get('cliente', '---'))}**  \n"
                                f"<span style='font-size:12px;color:#64748b;'>Orden #{row['id']}</span>", unsafe_allow_html=True)
                    r2.metric("Total", f"${float(row.get('total_venta', 0)):,.2f}")
                    r3.metric("Abono", f"${float(row.get('abono', 0)):,.2f}")
                    r4.metric("Saldo", f"${float(row.get('saldo', 0)):,.2f}", delta="Pendiente", delta_color="inverse")

                    with st.expander(f"💳 Registrar cobro — Orden #{row['id']}"):
                        with st.form(f"cobro_{row['id']}"):
                            c1, c2 = st.columns(2)
                            monto_cobro = c1.number_input("Monto a cobrar ($):", min_value=0.01,
                                                          max_value=float(row.get("saldo", 9999)), step=0.50,
                                                          key=f"mc_{row['id']}")
                            metodo_cobro = c2.selectbox("Método:", ["Efectivo", "Tarjeta", "Transferencia", "Cheque"],
                                                        key=f"met_{row['id']}")
                            ref = st.text_input("Referencia (N° comprobante, etc):", key=f"ref_{row['id']}")
                            if st.form_submit_button("✅ Registrar Cobro", type="primary"):
                                registrar_pago_saldo(
                                    orden_id=int(row["id"]),
                                    monto=monto_cobro,
                                    metodo=metodo_cobro,
                                    usuario=st.session_state.get("user_login", "admin"),
                                    sucursal=sucursal
                                )
                                st.success(f"✅ Cobro de ${monto_cobro:.2f} registrado.")
                                st.rerun()
                    st.markdown("<hr style='margin:8px 0; opacity:0.15;'>", unsafe_allow_html=True)

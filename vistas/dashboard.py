# -*- coding: utf-8 -*-
"""
Scale: 1:1
HAPPY VISION · vistas/dashboard.py
Módulo de Dashboard Operativo & Inteligencia de Negocios
"""

import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from database import (
    cargar_ordenes_trabajo,
    cargar_inventario,
    obtener_resumen_dia,
    cargar_ventas_historial,
    cargar_citas_hoy,
    cargar_sucursales,
    cargar_historias
)

def render_dashboard():
    st.markdown("""
        <style>
        .bi-kpi-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        .bi-kpi-card {
            background: linear-gradient(135deg, #1e293b, #0f172a);
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .bi-kpi-value {
            font-size: 2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-top: 5px;
        }
        .bi-kpi-value-green {
            font-size: 2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #22c55e, #4ade80);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-top: 5px;
        }
        .bi-kpi-value-yellow {
            font-size: 2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #eab308, #facc15);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-top: 5px;
        }
        .bi-kpi-label {
            font-size: 0.8rem;
            color: #94a3b8;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="page-header">
            <h1 style='margin:0; color:#1e293b;'>🏠 Panel de Control Gerencial</h1>
            <p style='margin:5px 0 0 0; color:#64748b;'>Resumen operativo y analítica avanzada de Happy Vision</p>
        </div>
    """, unsafe_allow_html=True)

    sucursal = st.session_state.get("sucursal_activa", "Matriz")
    
    # Habilitamos las pestañas gerenciales para todos los roles (facilita la consulta al propietario/directivos)
    tabs = st.tabs(["🏠 Panel Operativo Diario", "📊 Inteligencia de Negocios (BI)"])
    with tabs[0]:
        render_panel_operativo(sucursal)
    with tabs[1]:
        render_bi_dashboard(sucursal)


def render_panel_operativo(sucursal):
    # ── ALERTAS DE CITAS DE HOY (MÓDULO 1) ──
    citas_hoy = cargar_citas_hoy(sucursal)
    if not citas_hoy.empty:
        st.markdown(f"""
            <div class="alert-ok" style="background: linear-gradient(135deg, #1e3a8a, #3b82f6); border-color: #3b82f6; margin-bottom: 20px;">
                <div class="alert-text">📅 <b>¡Alertas de Agenda!</b> Tienes <b>{len(citas_hoy)}</b> cita(s) programada(s) para hoy en esta sucursal.</div>
                <div class="alert-sub">Revisa la pestaña "Agenda y Citas" para ver el detalle y comenzar la atención del día.</div>
            </div>
        """, unsafe_allow_html=True)

    # 1. MÉTRICAS OPERATIVAS
    resumen = obtener_resumen_dia(sucursal, pd.Timestamp.now().strftime("%Y-%m-%d"))
    df_ordenes = cargar_ordenes_trabajo(sucursal)
    df_inv = cargar_inventario(sucursal)
    
    m1, m2, m3, m4 = st.columns(4)
    
    # Ventas de hoy
    ventas_hoy = resumen["Efectivo"] + resumen["Tarjeta"] + resumen["Transferencia"]
    m1.metric("Ventas de Hoy", f"${ventas_hoy:.2f}", delta=f"-${resumen['Gastos']:.2f} gastos")
    
    # Órdenes en Laboratorio
    en_lab = 0
    listos = 0
    if not df_ordenes.empty and "estado" in df_ordenes.columns:
        en_lab = len(df_ordenes[df_ordenes["estado"] == "En Laboratorio"])
        listos = len(df_ordenes[df_ordenes["estado"] == "Listo para Entrega"])
    
    m2.metric("En Laboratorio", en_lab, help="Trabajos actualmente en proceso técnico")
    m3.metric("Listos p/ Entrega", listos, delta=f"{listos} clientes esperando" if listos > 0 else None)
    
    # Alertas de Inventario
    bajo_stock = 0
    if not df_inv.empty:
        col_s = "cantidad_disponible" if "cantidad_disponible" in df_inv.columns else "stock"
        col_m = "stock_minimo" if "stock_minimo" in df_inv.columns else None
        
        if col_m:
            bajo_stock = len(df_inv[df_inv[col_s] <= df_inv[col_m]])
        else:
            # Fallback a stock <= 3
            bajo_stock = len(df_inv[df_inv[col_s] <= 3])
            
    m4.metric("Bajo Stock", bajo_stock, delta="Revisar" if bajo_stock > 0 else "OK", delta_color="inverse" if bajo_stock > 0 else "normal")

    st.divider()

    col_l, col_r = st.columns([2, 1])
    
    with col_l:
        st.markdown("### 📈 Flujo de Órdenes Recientes")
        if not df_ordenes.empty:
            # Gráfico de órdenes por estado
            df_counts = df_ordenes["estado"].value_counts().reset_index()
            df_counts.columns = ["Estado", "Cantidad"]
            fig = px.bar(df_counts, x="Estado", y="Cantidad", color="Estado", 
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(showlegend=False, height=300, margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin datos de órdenes aún.")

    with col_r:
        # Mostrar productos con bajo stock
        if bajo_stock > 0:
            col_s = "cantidad_disponible" if "cantidad_disponible" in df_inv.columns else "stock"
            col_m = "stock_minimo" if "stock_minimo" in df_inv.columns else None
            
            st.markdown("**🚨 Alertas de Reposición**")
            if col_m:
                df_alertas = df_inv[df_inv[col_s] <= df_inv[col_m]].head(5)
            else:
                df_alertas = df_inv[df_inv[col_s] <= 3].head(5)
                
            for _, row in df_alertas.iterrows():
                st.error(f"**{row.get('nombre', 'Producto')}**\n\nQuedan solo **{int(row.get(col_s, 0))}** unidades.")
        else:
            st.success("✅ Inventario saludable.")
            
        st.markdown("---")
        # Mostrar órdenes más antiguas sin entregar
        st.markdown("**⏳ Trabajos Pendientes**")
        if not df_ordenes.empty and "estado" in df_ordenes.columns:
            df_viejas = df_ordenes[df_ordenes["estado"] == "Pendiente"].head(3)
            for _, row in df_viejas.iterrows():
                st.warning(f"ID #{row['id']} - {row['paciente_nombre']}")
        else:
            st.caption("No hay trabajos pendientes.")

    # Acceso Rápido
    st.markdown("### ⚡ Acciones Rápidas")
    cq1, cq2, cq3 = st.columns(3)
    if cq1.button("📅 Gestionar Agenda / Citas", use_container_width=True):
        st.session_state.page = "Citas"
        st.rerun()
    if cq2.button("👥 Ver Clientes y Fichas", use_container_width=True):
        st.session_state.page = "Pacientes"
        st.rerun()
    if cq3.button("💰 Abrir/Cerrar Caja Hoy", use_container_width=True):
        st.session_state.page = "Contabilidad"
        st.rerun()


def render_bi_dashboard(sucursal_activa):
    st.subheader("📊 Business Intelligence (BI) y Reportes Estratégicos")
    
    # Filtros BI de sucursal
    df_sucursales = cargar_sucursales()
    lista_sucs = ["Todas"] + (df_sucursales["nombre"].tolist() if not df_sucursales.empty else ["Matriz"])
    
    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        suc_sel = st.selectbox("Analizar Sucursal:", lista_sucs, index=lista_sucs.index(sucursal_activa) if sucursal_activa in lista_sucs else 0)
    with col_f2:
        st.write("") # Alineador estético

    # 1. Cargar Historial Completo de Ventas
    df_ventas = cargar_ventas_historial(suc_sel)
    df_inv = cargar_inventario(None if suc_sel == "Todas" else suc_sel)
    df_historias = cargar_historias()
    
    if df_ventas.empty:
        st.warning("⚠️ No se registran datos de ventas para generar el reporte gerencial.")
        return

    # Normalizar tipos
    df_ventas["total"] = pd.to_numeric(df_ventas["total"], errors='coerce').fillna(0.0)
    df_ventas["costo_total"] = pd.to_numeric(df_ventas["costo_total"], errors='coerce').fillna(0.0)
    df_ventas["abono"] = pd.to_numeric(df_ventas["abono"], errors='coerce').fillna(0.0)
    df_ventas["saldo"] = pd.to_numeric(df_ventas["saldo"], errors='coerce').fillna(0.0)
    df_ventas["fecha_dt"] = pd.to_datetime(df_ventas["fecha"])

    # ══════════════════════════════════════════════════════════════
    # R1: REPORTE FINANCIERO Y DE RENTABILIDAD
    # ══════════════════════════════════════════════════════════════
    total_ingresos = df_ventas["total"].sum()
    total_costos = df_ventas["costo_total"].sum()
    utilidad_bruta = total_ingresos - total_costos
    margen_promedio = (utilidad_bruta / total_ingresos * 100) if total_ingresos > 0 else 0.0

    st.markdown("#### 1. KPI Financieros y Margen de Utilidad")
    
    st.markdown(f"""
        <div class="bi-kpi-container">
            <div class="bi-kpi-card">
                <div class="bi-kpi-label">Ingresos Globales</div>
                <div class="bi-kpi-value">${total_ingresos:,.2f}</div>
            </div>
            <div class="bi-kpi-card">
                <div class="bi-kpi-label">Costo de Adquisición (Lab/Stock)</div>
                <div class="bi-kpi-value-yellow">${total_costos:,.2f}</div>
            </div>
            <div class="bi-kpi-card">
                <div class="bi-kpi-label">Utilidad Bruta Neta</div>
                <div class="bi-kpi-value-green">${utilidad_bruta:,.2f}</div>
            </div>
            <div class="bi-kpi-card">
                <div class="bi-kpi-label">Margen de Ganancia Promedio</div>
                <div class="bi-kpi-value-green">{margen_promedio:.1f}%</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Gráfico de Tendencia Mensual de Ingresos vs Utilidad
    df_ventas["mes_nombre"] = df_ventas["fecha_dt"].dt.strftime("%Y-%m")
    df_finan_mensual = df_ventas.groupby("mes_nombre").agg({
        "total": "sum",
        "costo_total": "sum"
    }).reset_index()
    df_finan_mensual["Utilidad"] = df_finan_mensual["total"] - df_finan_mensual["costo_total"]

    fig_trend = go.Figure()
    fig_trend.add_trace(go.Bar(
        x=df_finan_mensual["mes_nombre"], y=df_finan_mensual["total"],
        name="Ingresos Brutos", marker_color="#3b82f6"
    ))
    fig_trend.add_trace(go.Scatter(
        x=df_finan_mensual["mes_nombre"], y=df_finan_mensual["Utilidad"],
        name="Utilidad Bruta Neta", line=dict(color="#10b981", width=3), mode='lines+markers'
    ))
    fig_trend.update_layout(
        title="Ganancia Real vs Ingresos por Mes",
        xaxis_title="Mes", yaxis_title="Monto ($)",
        barmode='group', height=350, margin=dict(t=40, b=20, l=20, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown("---")

    # ══════════════════════════════════════════════════════════════
    # R2: ANÁLISIS DE ROTACIÓN DE INVENTARIO (ABC)
    # ══════════════════════════════════════════════════════════════
    st.markdown("#### 2. Clasificación ABC de Rotación de Inventario")
    
    sold_products = {}
    if "detalles" in df_ventas.columns:
        for _, sale in df_ventas.iterrows():
            details = sale["detalles"]
            if isinstance(details, str):
                try: details = json.loads(details)
                except: details = []
            if isinstance(details, list):
                for d in details:
                    p_id = d.get("id_armazon")
                    desc = d.get("descripcion", "Lunas/Laboratorio")
                    p_qty = d.get("cantidad", 1)
                    p_val = d.get("precio", 0.0)
                    p_cost = d.get("costo", 0.0)
                    
                    key = str(p_id) if p_id else desc
                    if key not in sold_products:
                         sold_products[key] = {"Producto": desc, "Unidades Vendidas": 0, "Ingresos Totales": 0.0, "Costo Total": 0.0}
                    sold_products[key]["Unidades Vendidas"] += p_qty
                    sold_products[key]["Ingresos Totales"] += p_val * p_qty
                    sold_products[key]["Costo Total"] += p_cost * p_qty

    if sold_products:
        df_sold = pd.DataFrame(sold_products.values())
        # Clasificar usando valor monetario acumulado de ventas
        df_sold = df_sold.sort_values(by="Ingresos Totales", ascending=False)
        df_sold["cum_ingresos"] = df_sold["Ingresos Totales"].cumsum()
        total_rev = df_sold["Ingresos Totales"].sum()
        
        if total_rev > 0:
            df_sold["cum_pct"] = (df_sold["cum_ingresos"] / total_rev) * 100
            
            def abc_classify(pct):
                if pct <= 70: return "A (Alta Rotación / 70% Valor)"
                elif pct <= 90: return "B (Rotación Media / 20% Valor)"
                else: return "C (Baja Rotación / 10% Valor)"
            
            df_sold["Clasificación ABC"] = df_sold["cum_pct"].apply(abc_classify)
            
            c_abc1, c_abc2 = st.columns([1, 1])
            with c_abc1:
                # Plotly Pie para Distribución ABC
                df_abc_summary = df_sold.groupby("Clasificación ABC").agg({
                    "Producto": "count",
                    "Ingresos Totales": "sum"
                }).reset_index().rename(columns={"Producto": "Cantidad de Productos"})
                
                fig_abc = px.pie(
                    df_abc_summary, values="Ingresos Totales", names="Clasificación ABC",
                    color_discrete_map={
                        "A (Alta Rotación / 70% Valor)": "#10b981",
                        "B (Rotación Media / 20% Valor)": "#f59e0b",
                        "C (Baja Rotación / 10% Valor)": "#ef4444"
                    },
                    title="Contribución de Ingresos por Clasificación ABC"
                )
                fig_abc.update_layout(height=300, margin=dict(t=30, b=10, l=10, r=10))
                st.plotly_chart(fig_abc, use_container_width=True)
            with c_abc2:
                st.caption("🔍 **Leyenda Estratégica ABC:**")
                st.markdown("""
                - **Clase A:** Generan el **70%** de los ingresos. Son tus productos estrella, mantén stock siempre disponible.
                - **Clase B:** Generan el **20%** de ingresos. Productos de demanda media.
                - **Clase C:** Generan solo el **10%** de ingresos. Estancados o de bajísima rotación. Evita sobrecompras.
                """)
                st.dataframe(df_sold[["Producto", "Unidades Vendidas", "Ingresos Totales", "Clasificación ABC"]].head(8), use_container_width=True, hide_index=True)
    else:
        st.info("Sin datos para análisis de rotación ABC.")

    # ── AGREGAR EL ANÁLISIS ABC DE STOCK DE INVENTARIO (BODEGA) ORIGINAL ──
    st.markdown("#### 2.1. Análisis de Valor Estancado en Stock (Inventario en Bodega)")
    if not df_inv.empty:
        df_inv_copy = df_inv.copy()
        df_inv_copy['precio_venta'] = pd.to_numeric(df_inv_copy.get('precio_venta', 0), errors='coerce').fillna(0)
        df_inv_copy['cantidad'] = pd.to_numeric(df_inv_copy.get('cantidad_disponible', df_inv_copy.get('stock', 0)), errors='coerce').fillna(0)
        df_inv_copy['valor_potencial'] = df_inv_copy['precio_venta'] * df_inv_copy['cantidad']
        
        col_inv_abc1, col_inv_abc2 = st.columns([1, 1])
        with col_inv_abc1:
            fig_abc_stock = px.pie(df_inv_copy.sort_values('valor_potencial', ascending=False).head(10), 
                             names='nombre', values='valor_potencial', 
                             title="Top 10 Productos por Valor Estancado en Stock")
            fig_abc_stock.update_layout(height=300, margin=dict(t=30, b=10, l=10, r=10))
            st.plotly_chart(fig_abc_stock, use_container_width=True)
        with col_inv_abc2:
            st.caption("📦 **Valorización de Stock en Bodega:**")
            st.write("Este gráfico detalla los productos que representan el mayor valor monetario inmovilizado en tus perchas y almacén.")
            st.dataframe(df_inv_copy[["nombre", "cantidad", "precio_venta", "valor_potencial"]].sort_values("valor_potencial", ascending=False).head(8), use_container_width=True, hide_index=True)
    else:
        st.info("No hay datos de inventario en bodega para valorizar.")

    st.markdown("---")

    # ══════════════════════════════════════════════════════════════
    # R3 & R4: RENDIMIENTO DE CONSULTAS Y TENDENCIAS POR CATEGORÍA
    # ══════════════════════════════════════════════════════════════
    st.markdown("#### 3. Rendimiento Clínico y Tendencias de Compra")
    
    cr1, cr2 = st.columns(2)
    
    with cr1:
        # Conversión Clínica-Venta & Ticket Promedio
        total_historias = len(df_historias)
        total_ventas_count = len(df_ventas)
        
        conversion_rate = (total_ventas_count / total_historias * 100) if total_historias > 0 else 0.0
        ticket_promedio = (total_ingresos / total_ventas_count) if total_ventas_count > 0 else 0.0
        
        st.write("**Conversión y Ticket Promedio**")
        
        sub_c1, sub_c2 = st.columns(2)
        sub_c1.metric("Fichas Clínicas (Consultas)", total_historias)
        sub_c2.metric("Conversión Clínica-Venta", f"{conversion_rate:.1f}%", help="Porcentaje de consultas que resultan en una venta directa")
        
        sub_c3, sub_c4 = st.columns(2)
        sub_c3.metric("Total Transacciones", total_ventas_count)
        sub_c4.metric("Ticket Promedio Venta", f"${ticket_promedio:.2f}", help="Monto promedio gastado por cliente por compra")
        
    with cr2:
        # Tendencias de Venta por Categoría (Lunas vs Armazones)
        cat_totals = {"Armazones": 0.0, "Lunas": 0.0, "Accesorios/Otros": 0.0}
        if sold_products:
            for item in sold_products.values():
                name = item["Producto"].lower()
                val = item["Ingresos Totales"]
                if "armazón" in name or "montura" in name:
                    cat_totals["Armazones"] += val
                elif "luna" in name or "progresivo" in name or "monofocal" in name or "bifocal" in name:
                    cat_totals["Lunas"] += val
                else:
                    cat_totals["Accesorios/Otros"] += val
                    
            df_cat = pd.DataFrame(list(cat_totals.items()), columns=["Categoría", "Ingresos"])
            fig_cat = px.pie(df_cat, values="Ingresos", names="Categoría", hole=.4,
                             color_discrete_sequence=px.colors.qualitative.Safe,
                             title="Distribución de Ventas por Tipo de Producto")
            fig_cat.update_layout(height=280, margin=dict(t=40, b=10, l=10, r=10))
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.caption("Sin datos de categorías.")

    st.markdown("---")

    # ══════════════════════════════════════════════════════════════
    # R5 & R6: RENTABILIDAD POR SUCURSAL & TOP PRODUCTOS
    # ══════════════════════════════════════════════════════════════
    st.markdown("#### 4. Análisis Geográfico (Sucursales) y Productos Estrella")
    
    cr3, cr4 = st.columns(2)
    
    with cr3:
        # R5: Rentabilidad por Sucursal
        df_ventas_all = cargar_ventas_historial("Todas")
        df_ventas_all["total"] = pd.to_numeric(df_ventas_all["total"], errors='coerce').fillna(0.0)
        df_ventas_all["costo_total"] = pd.to_numeric(df_ventas_all["costo_total"], errors='coerce').fillna(0.0)
        
        if not df_ventas_all.empty:
            df_sucs = df_ventas_all.groupby("sucursal").agg({
                "total": "sum",
                "costo_total": "sum"
            }).reset_index()
            df_sucs["Utilidad Neta"] = df_sucs["total"] - df_sucs["costo_total"]
            
            fig_sucs = px.bar(df_sucs, x="sucursal", y=["total", "Utilidad Neta"],
                              title="Ingreso Bruto vs Utilidad Neta por Sucursal",
                              barmode="group",
                              color_discrete_map={"total": "#3b82f6", "Utilidad Neta": "#10b981"})
            fig_sucs.update_layout(height=300, margin=dict(t=40, b=10, l=10, r=10))
            st.plotly_chart(fig_sucs, use_container_width=True)
        else:
            st.caption("Sin datos de sucursales.")
            
    with cr4:
        # R6: Top Productos Más Vendidos
        if sold_products:
            df_sold_sorted = pd.DataFrame(sold_products.values()).sort_values(by="Unidades Vendidas", ascending=False).head(5)
            fig_top = px.bar(df_sold_sorted, x="Unidades Vendidas", y="Producto", orientation="h",
                             title="Top 5 Productos Más Vendidos (Volumen)",
                             color="Unidades Vendidas",
                             color_continuous_scale=px.colors.sequential.Teal)
            fig_top.update_layout(height=300, showlegend=False, margin=dict(t=40, b=10, l=10, r=10))
            st.plotly_chart(fig_top, use_container_width=True)
        else:
            st.caption("Sin datos de volumen.")

    st.markdown("---")

    # ══════════════════════════════════════════════════════════════
    # R7: REPORTE DE DEUDORES / SALDOS PENDIENTES
    # ══════════════════════════════════════════════════════════════
    st.markdown("#### 5. Reporte de Cuentas por Cobrar (Deudores / Saldos Pendientes)")
    
    df_deudores = df_ventas[df_ventas["saldo"] > 0].copy()
    cartera_pendiente = df_deudores["saldo"].sum()
    
    c_debt1, c_debt2 = st.columns([1, 3])
    with c_debt1:
        st.markdown(f"""
            <div style="background-color: #fef2f2; border: 1px solid #fee2e2; border-left: 5px solid #ef4444; border-radius: 10px; padding: 20px; text-align: center; margin-top: 10px;">
                <p style="color: #991b1b; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; margin: 0;">Cartera Pendiente</p>
                <h3 style="color: #ef4444; font-size: 2.2rem; margin: 5px 0 0 0; font-weight: 800;">${cartera_pendiente:,.2f}</h3>
                <p style="color: #7f1d1d; font-size: 0.8rem; margin: 5px 0 0 0;"><b>{len(df_deudores)}</b> facturas con saldo activo.</p>
            </div>
        """, unsafe_allow_html=True)
    with c_debt2:
        if df_deudores.empty:
            st.success("🎉 ¡Excelente! No tienes saldos pendientes en esta sucursal.")
        else:
            # Reorganizar columnas para el analista
            df_deudores_view = df_deudores[["fecha", "cliente", "identificacion", "total", "abono", "saldo", "metodo_pago"]].copy()
            df_deudores_view["fecha"] = pd.to_datetime(df_deudores_view["fecha"]).dt.strftime("%d/%m/%Y %H:%M")
            df_deudores_view.columns = ["Fecha Venta", "Paciente/Cliente", "Identificación", "Total ($)", "Abonado ($)", "Saldo Pendiente ($)", "Forma de Pago"]
            
            st.dataframe(df_deudores_view, use_container_width=True, hide_index=True)

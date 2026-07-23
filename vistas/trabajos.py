import streamlit as st
import pandas as pd
from datetime import datetime
from database import cargar_orden_trabajo_detallada, actualizar_estado_orden, cargar_ordenes_trabajo

def render_trabajos():
    st.markdown("""
        <style>
        .order-card {
            background-color: white;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 5px solid #00458e;
        }
        .prescription-box {
            background-color: #f8fafc;
            border: 1px solid #cbd5e1;
            padding: 10px;
            font-family: monospace;
            font-size: 14px;
            border-radius: 4px;
        }
        .status-badge {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="page-header">
            <h1 style='margin:0; color:#1e293b;'>📋 Órdenes de Trabajo (Laboratorio)</h1>
            <p style='margin:5px 0 0 0; color:#64748b;'>Seguimiento técnico y control de lunas</p>
        </div>
    """, unsafe_allow_html=True)

    sucursal_activa = st.session_state.get("sucursal_activa", "Matriz")
    
    # Cargar órdenes desde la DB
    df_ord = cargar_ordenes_trabajo(sucursal_activa)
    
    if df_ord.empty:
        st.info("No hay órdenes de trabajo registradas actualmente.")
        return

    # Filtros rápidos
    c1, c2 = st.columns([2, 1])
    busqueda = c1.text_input("🔍 Buscar por paciente o ID:", placeholder="Nombre del paciente...")
    filtro_estado = c2.selectbox("Filtrar por estado:", ["Todos", "Pendiente", "Laboratorio", "Listo", "Entregado"])

    # Aplicar filtros
    if busqueda:
        df_ord = df_ord[df_ord["paciente_nombre"].str.contains(busqueda, case=False, na=False)]
    if filtro_estado != "Todos":
        df_ord = df_ord[df_ord["estado"] == filtro_estado]

    st.write(f"Mostrando {len(df_ord)} órdenes")

    for _, row in df_ord.iterrows():
        with st.container():
            st.markdown(f"""
                <div class="order-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="margin:0; color:#00458e;">Orden #{row['id']} - {row['paciente_nombre']}</h3>
                        <span class="status-badge" style="background:#dcfce7; color:#166534;">{row['estado']}</span>
                    </div>
                    <p style="margin:5px 0; color:#64748b;">📍 Sucursal: {row.get('sucursal', 'N/A')} | 📅 Fecha: {row.get('creado_el', 'N/A')[:10]}</p>
                    <hr style="margin:10px 0; border:0; border-top:1px solid #e2e8f0;">
                    <p><b>🔬 Lentes:</b> {row.get('detalle_lentes', 'No especificado')}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Detalle expandible con la RECETA
            with st.expander("Ver Ficha Técnica (Receta)"):
                presc = row.get("prescripcion", {})
                
                # Cuadro de medidas profesional
                st.markdown("#### 📋 Cuadro de Medidas")
                col_od, col_oi = st.columns(2)
                
                with col_od:
                    st.markdown("**Ojo Derecho (OD)**")
                    rx_od = presc.get("OD", {}) if isinstance(presc, dict) else {}
                    st.json(rx_od)
                
                with col_oi:
                    st.markdown("**Ojo Izquierdo (OI)**")
                    rx_oi = presc.get("OI", {}) if isinstance(presc, dict) else {}
                    st.json(rx_oi)

                # Acciones
                st.markdown("---")
                a1, a2, a3 = st.columns([1, 1, 1])
                nuevo_st = a1.selectbox("Cambiar Estado:", ["Pendiente", "Laboratorio", "Listo", "Entregado"], key=f"st_{row['id']}")
                if a2.button("💾 Actualizar", key=f"btn_st_{row['id']}"):
                    actualizar_estado_orden(row['id'], nuevo_st, st.session_state.user_login, sucursal_activa)
                    st.success("Estado actualizado")
                    st.rerun()
                
                # --- MEJORA PREMIUM: WHATSAPP INTELIGENTE ---
                msg = ""
                from utils.whatsapp import generar_msg_orden_lista, wa_link
                if nuevo_st == "Listo":
                    msg = generar_msg_orden_lista(row['paciente_nombre'])
                elif nuevo_st == "Laboratorio":
                    msg = f"Hola *{row['paciente_nombre']}*,\n\nTe informamos que tus lentes han ingresado a nuestro laboratorio técnico de *Happy Vision*. Te avisaremos apenas estén listos. 👓✨"
                
                if msg:
                    # Intentar buscar el teléfono del paciente en la DB
                    from database import cargar_pacientes
                    df_p = cargar_pacientes()
                    p_info = df_p[df_p['nombre'] == row['paciente_nombre']]
                    tel = str(p_info.iloc[0]['telefono']) if not p_info.empty and 'telefono' in p_info.columns else ""
                    
                    if tel:
                        link = wa_link(tel, msg)
                        st.markdown(f'<a href="{link}" target="_blank"><button style="background:#25D366; color:white; border:none; padding:8px 12px; border-radius:6px; width:100%; cursor:pointer; font-weight:bold; margin-top:8px;">📲 Notificar por WhatsApp</button></a>', unsafe_allow_html=True)
                    else:
                        st.caption("⚠️ No hay teléfono registrado para este paciente.")
                
                if a3.button("🖨️ Imprimir Orden", key=f"print_{row['id']}"):
                    st.info("Vista de impresión técnica generada.")

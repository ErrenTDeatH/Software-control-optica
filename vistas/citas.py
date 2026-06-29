import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database import cargar_todas_citas, guardar_cita, eliminar_cita
from utils import wa_link

def render_lista_citas(df_mostrar, key_prefix):
    """Renderiza una lista de citas formateada como tarjetas de diseño premium."""
    if df_mostrar.empty:
        st.info("No hay citas registradas en esta sección.")
        return
        
    filtro_estado = st.selectbox("Filtrar por estado", ["Todas", "Pendiente", "Atendido", "Cancelado"], key=f"filter_{key_prefix}")
    if filtro_estado != "Todas":
        df_final = df_mostrar[df_mostrar["estado"] == filtro_estado]
    else:
        df_final = df_mostrar
        
    if df_final.empty:
        st.info(f"No hay citas con el estado: {filtro_estado}")
        return
        
    # Renderizar tarjetas
    for idx, cita in df_final.iterrows():
        estado = cita["estado"]
        badge_class = "badge-yellow" if estado == "Pendiente" else "badge-green" if estado == "Atendido" else "badge-red"
        
        hora_str = cita['hora']
        try:
            # Intentar formatear a formato de 12 horas para mayor claridad visual
            hora_str = datetime.strptime(cita['hora'], "%H:%M:%S").strftime("%I:%M %p")
        except:
            try:
                hora_str = datetime.strptime(cita['hora'], "%H:%M").strftime("%I:%M %p")
            except:
                pass
                
        card_html = f"""
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 14px; padding: 18px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 1.15rem; font-weight: 700; color: #0f172a;">⏰ {hora_str} &nbsp;&nbsp;|&nbsp;&nbsp; 👤 {cita['paciente_nombre']}</span>
                <span class="badge {badge_class}">{estado}</span>
            </div>
            <div style="font-size: 0.9rem; color: #475569; margin-bottom: 10px;">
                📅 <b>Fecha:</b> {cita['fecha']} &nbsp;&nbsp;•&nbsp;&nbsp; 👨‍⚕️ <b>Optometrista:</b> {cita.get('optometrista', 'N/A')}
            </div>
            <div style="font-size: 0.9rem; color: #64748b;">
                📝 <b>Motivo:</b> {cita.get('motivo', 'N/A')} &nbsp;&nbsp;•&nbsp;&nbsp; 📞 <b>Teléfono:</b> {cita.get('telefono', 'N/A')}
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
        
        # Acciones para cada cita
        c1, c2, c3, _ = st.columns([1.2, 1.2, 2.2, 3.4])
        
        if estado == "Pendiente":
            if c1.button("✅ Atendido", key=f"atender_{key_prefix}_{cita['id']}", use_container_width=True):
                cita_update = cita.to_dict()
                cita_update["estado"] = "Atendido"
                cita_update.pop("fecha_parsed", None)
                guardar_cita(cita_update)
                st.success(f"Cita marcada como Atendida.")
                st.rerun()
            if c2.button("❌ Cancelar", key=f"cancelar_{key_prefix}_{cita['id']}", use_container_width=True):
                cita_update = cita.to_dict()
                cita_update["estado"] = "Cancelado"
                cita_update.pop("fecha_parsed", None)
                guardar_cita(cita_update)
                st.warning(f"Cita marcada como Cancelada.")
                st.rerun()
        else:
            if c1.button("🗑️ Eliminar", key=f"eliminar_{key_prefix}_{cita['id']}", use_container_width=True):
                eliminar_cita(cita["id"])
                st.success("Cita eliminada correctamente.")
                st.rerun()
                
        if cita.get("telefono"):
            # Generar recordatorio formal en español para enviar por WhatsApp
            msg = (
                f"Estimado/a {cita['paciente_nombre']},\n\n"
                f"Esperamos que se encuentre muy bien. Le saluda el equipo de *Happy Vision*.\n\n"
                f"Le recordamos su próxima cita de optometría agendada:\n"
                f"📅 *Fecha:* {cita['fecha']}\n"
                f"⏰ *Hora:* {hora_str}\n"
                f"🏢 *Sucursal:* {cita.get('sucursal', 'Matriz')}\n"
                f"👨‍⚕️ *Optometrista:* {cita.get('optometrista', '')}\n\n"
                f"Por favor, confirme su asistencia respondiendo directamente a este mensaje por WhatsApp o comunicándose a nuestro número de atención: +593 96 324 1158.\n\n"
                f"Atentamente,\n"
                f"Happy Vision"
            )
            link = wa_link(cita["telefono"], msg)
            c3.link_button("💬 Recordatorio WA", link, use_container_width=True)
            
        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)


def render_citas():
    st.markdown("""
        <div class="page-header">
            <h1 style='margin:0; color:#1e293b;'>📅 Agendamiento de Citas</h1>
            <p style='margin:5px 0 0 0; color:#64748b;'>Gestión interna de citas para optometría</p>
        </div>
    """, unsafe_allow_html=True)

    sucursal = st.session_state.get("sucursal_activa", "Matriz")
    df_pacientes = st.session_state.get("df_pacientes")
    
    # Preselección desde el CRM
    pre_sel_name = st.session_state.get("pre_sel_name", None)
    expander_expanded = pre_sel_name is not None
    
    # ── FORMULARIO PARA NUEVA CITA ────────────────────────────
    with st.expander("➕ Agendar Nueva Cita", expanded=expander_expanded):
        if pre_sel_name:
            st.info(f"📍 Agendando cita sugerida para: **{pre_sel_name}**")
            if st.button("🧹 Limpiar pre-selección", key="clear_pre_sel"):
                st.session_state.pop("pre_sel_name", None)
                st.rerun()
                
        c1, c2 = st.columns(2)
        fecha = c1.date_input("Fecha de la Cita")
        hora = c2.time_input("Hora de la Cita")
        
        opcion_paciente = st.radio("Tipo de Registro de Paciente", ["Paciente Registrado", "Nuevo Paciente (Sin registrar)"], horizontal=True)
        
        paciente_nombre = ""
        telefono = ""
        
        if opcion_paciente == "Paciente Registrado" and df_pacientes is not None and not df_pacientes.empty:
            # Filtrar pacientes que tengan un nombre válido
            df_p_valid = df_pacientes[df_pacientes["nombre"].str.strip() != ""]
            if not df_p_valid.empty:
                df_p_sorted = df_p_valid.sort_values(by="nombre")
                
                # Crear etiquetas del selector "Nombre (C.I. / Teléfono)"
                pacientes_list = []
                paciente_map = {}
                for _, prow in df_p_sorted.iterrows():
                    label = f"{prow['nombre']}"
                    if prow.get('identificacion'):
                        label += f" - {prow['identificacion']}"
                    elif prow.get('telefono'):
                        label += f" - {prow['telefono']}"
                    pacientes_list.append(label)
                    paciente_map[label] = prow
                    
                # Buscar índice del paciente preseleccionado si existe
                default_idx = 0
                if pre_sel_name:
                    for idx, label in enumerate(pacientes_list):
                        if label.startswith(pre_sel_name):
                            default_idx = idx
                            break
                            
                paciente_sel = st.selectbox("Seleccione el Paciente", pacientes_list, index=default_idx)
                if paciente_sel:
                    selected_p = paciente_map[paciente_sel]
                    paciente_nombre = selected_p["nombre"]
                    telefono = selected_p.get("telefono", "")
            else:
                st.info("No hay pacientes registrados con nombres válidos.")
                opcion_paciente = "Nuevo Paciente (Sin registrar)"
        
        if opcion_paciente == "Nuevo Paciente (Sin registrar)" or df_pacientes is None or df_pacientes.empty:
            c3, c4 = st.columns(2)
            paciente_nombre = c3.text_input("Nombre del Paciente", value=paciente_nombre)
            telefono = c4.text_input("Teléfono (Opcional)", value=telefono)
        else:
            c3, c4 = st.columns(2)
            st.text_input("Nombre del Paciente", value=paciente_nombre, disabled=True)
            st.text_input("Teléfono (Opcional)", value=telefono, disabled=True)
            
        c5, c6 = st.columns(2)
        motivo = c5.text_input("Motivo de la Cita", value="Control de Rutina" if pre_sel_name else "")
        optometrista = c6.text_input("Optometrista Asignado", value=st.session_state.get("user_name", ""))
        
        if st.button("Agendar Cita", type="primary", use_container_width=True):
            if not paciente_nombre:
                st.error("El nombre del paciente es obligatorio.")
            else:
                nueva_cita = {
                    "fecha": fecha.strftime("%Y-%m-%d"),
                    "hora": hora.strftime("%H:%M:%S"),
                    "paciente_nombre": paciente_nombre,
                    "telefono": telefono,
                    "motivo": motivo,
                    "optometrista": optometrista,
                    "sucursal": sucursal,
                    "estado": "Pendiente"
                }
                st.session_state.pop("pre_sel_name", None)
                guardar_cita(nueva_cita)
                st.success("Cita agendada correctamente.")
                st.rerun()
                
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ── CONTROL Y METRICAS DE HOY ─────────────────────────────
    df_citas = cargar_todas_citas(sucursal)
    
    # CÁLCULO DE CONTROLES PENDIENTES (CRM)
    df_h = st.session_state.get("df_historias")
    df_p = st.session_state.get("df_pacientes")
    df_alerta = pd.DataFrame()
    
    if df_h is not None and not df_h.empty and df_p is not None and not df_p.empty:
        def proximo_control(row):
            try:
                fecha_consulta = pd.to_datetime(row["fecha"]).date()
                val = str(row.get("meses_proximo_control", "")).strip()
                if not val:
                    return fecha_consulta + timedelta(days=12 * 30)
                if "-" in val:
                    try:
                        return pd.to_datetime(val[:10]).date()
                    except:
                        pass
                val_clean = "".join(c for c in val if c.isdigit() or c == ".")
                if val_clean:
                    meses = int(float(val_clean))
                else:
                    meses = 12
                return fecha_consulta + timedelta(days=meses * 30)
            except Exception:
                return None

        df_h_copy = df_h.copy()
        df_h_copy["proximo_control"] = df_h_copy.apply(proximo_control, axis=1)
        
        df_h_sorted = df_h_copy.sort_values("fecha", ascending=False)
        df_ultima = df_h_sorted.drop_duplicates(subset=["paciente_id"], keep="first").copy()
        df_ultima = df_ultima.merge(df_p[["id", "nombre", "telefono"]], left_on="paciente_id", right_on="id", how="left", suffixes=("", "_pac"))
        
        hoy_date = datetime.now().date()
        df_ultima["dias_para_control"] = df_ultima["proximo_control"].apply(
            lambda d: (d - hoy_date).days if d is not None else None
        )
        
        # Vencidos o próximos a vencer en los siguientes 365 días (1 año)
        mask_alerta = df_ultima["dias_para_control"].apply(
            lambda d: d is not None and d <= 365
        )
        df_alerta = df_ultima[mask_alerta].sort_values("dias_para_control")
    
    if not df_citas.empty or not df_alerta.empty:
        hoy_str = datetime.now().strftime("%Y-%m-%d")
        citas_hoy = df_citas[df_citas["fecha"] == hoy_str] if not df_citas.empty else pd.DataFrame()
        
        pendientes_hoy = len(citas_hoy[citas_hoy["estado"] == "Pendiente"]) if not citas_hoy.empty else 0
        atendidas_hoy = len(citas_hoy[citas_hoy["estado"] == "Atendido"]) if not citas_hoy.empty else 0
        canceladas_hoy = len(citas_hoy[citas_hoy["estado"] == "Cancelado"]) if not citas_hoy.empty else 0
        
        st.markdown(f"""
        <div class="kpi-grid">
            <div style="background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%); border: 1px solid #fed7aa; border-radius: 16px; padding: 20px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03); transition: transform 0.2s;">
                <div style="font-size: 1.8rem; margin-bottom: 6px;">🕒</div>
                <div style="font-size: 2.2rem; font-weight: 800; color: #c2410c; line-height: 1;">{pendientes_hoy}</div>
                <div style="font-size: 0.85rem; font-weight: 700; color: #ea580c; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 8px;">Pendientes Hoy</div>
            </div>
            <div style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); border: 1px solid #bbf7d0; border-radius: 16px; padding: 20px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03); transition: transform 0.2s;">
                <div style="font-size: 1.8rem; margin-bottom: 6px;">✅</div>
                <div style="font-size: 2.2rem; font-weight: 800; color: #15803d; line-height: 1;">{atendidas_hoy}</div>
                <div style="font-size: 0.85rem; font-weight: 700; color: #16a34a; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 8px;">Atendidas Hoy</div>
            </div>
            <div style="background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%); border: 1px solid #fecaca; border-radius: 16px; padding: 20px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03); transition: transform 0.2s;">
                <div style="font-size: 1.8rem; margin-bottom: 6px;">❌</div>
                <div style="font-size: 2.2rem; font-weight: 800; color: #b91c1c; line-height: 1;">{canceladas_hoy}</div>
                <div style="font-size: 0.85rem; font-weight: 700; color: #dc2626; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 8px;">Canceladas Hoy</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ── SEPARACIÓN POR PESTAÑAS TEMPORALES ────────────────────
        df_hoy = pd.DataFrame()
        df_proximas = pd.DataFrame()
        df_historial = pd.DataFrame()
        
        if not df_citas.empty:
            df_citas["fecha_parsed"] = pd.to_datetime(df_citas["fecha"]).dt.date
            hoy_date = datetime.now().date()
            
            df_hoy = df_citas[df_citas["fecha_parsed"] == hoy_date]
            df_proximas = df_citas[df_citas["fecha_parsed"] > hoy_date]
            df_historial = df_citas[df_citas["fecha_parsed"] < hoy_date]
        
        tab_hoy, tab_proximas, tab_historial, tab_crm = st.tabs([
            f"📅 Hoy ({len(df_hoy)})", 
            f"🚀 Próximas ({len(df_proximas)})", 
            f"⏳ Historial ({len(df_historial)})",
            f"🔔 Controles CRM ({len(df_alerta)})"
        ])
        
        with tab_hoy:
            st.markdown("<h4 style='color:#1e293b; margin-top:10px;'>Citas Programadas para Hoy</h4>", unsafe_allow_html=True)
            render_lista_citas(df_hoy, "hoy")
            
        with tab_proximas:
            st.markdown("<h4 style='color:#1e293b; margin-top:10px;'>Citas Planificadas (Futuras)</h4>", unsafe_allow_html=True)
            render_lista_citas(df_proximas, "proximas")
            
        with tab_historial:
            st.markdown("<h4 style='color:#1e293b; margin-top:10px;'>Registro Histórico de Citas</h4>", unsafe_allow_html=True)
            render_lista_citas(df_historial, "historial")
            
        with tab_crm:
            st.markdown("<h4 style='color:#1e293b; margin-top:10px;'>Alertas de Próximos Controles y Pacientes Vencidos</h4>", unsafe_allow_html=True)
            st.caption("Filtra los pacientes que se atendieron y requieren un nuevo control visual según la fecha programada.")
            
            # Selector de rango
            opciones_rango = {
                "Vencidos o que vencen en los siguientes 30 días": 30,
                "Vencidos o que vencen en los siguientes 90 días": 90,
                "Vencidos o que vencen en los siguientes 12 meses": 365,
                "Mostrar todos los controles programados": 99999
            }
            rango_sel = st.selectbox("Rango de visualización de controles:", list(opciones_rango.keys()), index=2) # Default a 12 meses
            max_dias = opciones_rango[rango_sel]
            
            df_filtrada = df_alerta[df_alerta["dias_para_control"] <= max_dias] if not df_alerta.empty else pd.DataFrame()
            
            if df_filtrada.empty:
                st.success("✅ Ningún paciente coincide con el filtro de tiempo seleccionado.")
            else:
                for _, row in df_filtrada.iterrows():
                    dias = row.get("dias_para_control")
                    nombre = row.get("nombre", row.get("paciente_nombre", ""))
                    tel = str(row.get("telefono", "")).strip()
                    fecha_ultima = row.get("fecha", "")
                    fecha_control = row.get("proximo_control")
                    meses = row.get("meses_proximo_control", 12)
                    
                    if dias is not None and dias < 0:
                        estado_label = f"🔴 Vencido hace {abs(dias)} días"
                        color = "#ef4444"
                        bg = "#fee2e2"
                        text_color = "#991b1b"
                    else:
                        estado_label = f"🟡 Vence en {dias} días ({fecha_control})"
                        color = "#f59e0b"
                        bg = "#fef9c3"
                        text_color = "#854d0e"
                        
                    card_crm_html = f"""
                    <div style="background: {bg}; border-left: 5px solid {color}; border-radius: 12px; padding: 15px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                            <span style="font-size: 1.1rem; font-weight: 700; color: {text_color};">👤 {nombre}</span>
                            <span style="font-weight: 600; font-size: 0.85rem; color: {text_color};">{estado_label}</span>
                        </div>
                        <div style="font-size: 0.88rem; color: #475569;">
                            📅 <b>Última consulta:</b> {fecha_ultima} &nbsp;&nbsp;•&nbsp;&nbsp; ⏳ <b>Control cada:</b> {meses} meses &nbsp;&nbsp;•&nbsp;&nbsp; 📞 <b>Teléfono:</b> {tel or 'Sin teléfono'}
                        </div>
                    </div>
                    """
                    st.markdown(card_crm_html, unsafe_allow_html=True)
                    
                    c_b1, c_b2, _ = st.columns([1.5, 2.5, 6])
                    
                    if c_b1.button("📅 Agendar Cita", key=f"crm_book_{row['paciente_id']}", use_container_width=True):
                        st.session_state.pre_sel_name = nombre
                        st.rerun()
                        
                    if tel:
                        msg = (
                            f"Estimado/a {nombre},\n\n"
                            f"Esperamos que se encuentre muy bien. Le saluda el equipo de *Happy Vision*.\n\n"
                            f"Le escribimos para recordarle que es momento de agendar su control preventivo de salud visual periódico recomendado (cada {meses} meses) posterior a su última atención del día {fecha_ultima}.\n\n"
                            f"Si desea programar su cita, puede hacerlo respondiendo directamente a este mensaje por WhatsApp o comunicándose a nuestro número de atención: +593 96 324 1158.\n\n"
                            f"Estaremos gustosos de coordinar su cita en la fecha y hora que le resulte más conveniente.\n\n"
                            f"Atentamente,\n"
                            f"Happy Vision"
                        )
                        link = wa_link(tel, msg)
                        c_b2.link_button("📲 Invitar por WhatsApp", link, use_container_width=True)
                        
                    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    else:
        st.info("No hay citas registradas en esta sucursal.")

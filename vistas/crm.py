# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
from utils import wa_link
from database import cargar_ventas_historial


def render_crm():
    st.markdown("""
    <div class="page-header">
        <h1>📡 Seguimiento CRM & Segmentación</h1>
        <p>Retención de pacientes · Alertas de próximos controles · Segmentación Inteligente (VIP, Frecuentes, Inactivos)</p>
    </div>
    """, unsafe_allow_html=True)

    df_h = st.session_state.df_historias.copy()
    df_p = st.session_state.df_pacientes.copy()

    if len(df_h) == 0 or len(df_p) == 0:
        st.info("📭 No hay historias clínicas o pacientes registrados aún. El CRM se activará cuando haya datos.")
        return

    # Tabs
    tab_controles, tab_segmentacion = st.tabs(["🚨 Recordatorios de Control", "🎯 Segmentación de Pacientes"])

    # ── TAB 1: RECORDATORIOS DE CONTROL ─────────────────────────────
    with tab_controles:
        # Calcular fecha de próximo control
        today = datetime.today().date()

        def proximo_control(row):
            try:
                fecha_consulta = datetime.strptime(str(row["fecha"]), "%Y-%m-%d").date()
                meses = int(float(row.get("meses_proximo_control", 12) or 12))
                return fecha_consulta + timedelta(days=meses * 30)
            except Exception:
                return None

        df_h["proximo_control"] = df_h.apply(proximo_control, axis=1)

        # Tomar la consulta más reciente por paciente
        df_h_sorted = df_h.sort_values("fecha", ascending=False)
        df_ultima = df_h_sorted.drop_duplicates(subset=["paciente_id"], keep="first").copy()
        df_ultima = df_ultima.merge(df_p[["id", "nombre", "telefono"]], left_on="paciente_id", right_on="id", how="left", suffixes=("", "_pac"))

        # Calcular días restantes
        df_ultima["dias_para_control"] = df_ultima["proximo_control"].apply(
            lambda d: (d - today).days if d is not None else None
        )

        # Alertas: vencidos o próximos 30 días
        mask_alerta = df_ultima["dias_para_control"].apply(
            lambda d: d is not None and d <= 30
        )
        df_alerta = df_ultima[mask_alerta].sort_values("dias_para_control")

        # KPIs
        total_pac = len(df_ultima)
        vencidos = len(df_ultima[df_ultima["dias_para_control"].apply(lambda d: d is not None and d < 0)])
        proximos_30 = len(df_alerta[df_alerta["dias_para_control"].apply(lambda d: d is not None and 0 <= d <= 30)])
        al_dia = total_pac - len(df_alerta)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("👥 Pacientes Activos", total_pac)
        k2.metric("🔴 Controles Vencidos", vencidos)
        k3.metric("🟡 Control en 30 Días", proximos_30)
        k4.metric("🟢 Al Día", al_dia)

        st.markdown("---")

        if len(df_alerta) == 0:
            st.success("✅ ¡Excelente! Ningún paciente tiene control vencido o próximo. Todos están al día.")
        else:
            st.markdown("<div class='section-title'>🚨 Pacientes que requieren contacto</div>", unsafe_allow_html=True)
            st.caption("Controles vencidos o que vencen en los próximos 30 días.")

            for _, row in df_alerta.iterrows():
                dias = row.get("dias_para_control")
                nombre = row.get("nombre", row.get("paciente_nombre", ""))
                tel = str(row.get("telefono", "")).strip()
                fecha_ultima = row.get("fecha", "")
                fecha_control = row.get("proximo_control")
                meses = row.get("meses_proximo_control", 12)

                if dias is not None and dias < 0:
                    estado_label = f"🔴 Vencido hace {abs(dias)} días"
                    color = "#ef4444"
                    bg = "#fff1f2"
                    text_col = "#991b1b"
                else:
                    estado_label = f"🟡 Vence en {dias} días ({fecha_control})"
                    color = "#f59e0b"
                    bg = "#fefbeb"
                    text_col = "#9a3412"

                col_info, col_wa = st.columns([5, 1])
                with col_info:
                    st.markdown(
                        f"<div style='background:{bg}; border-left:4px solid {color}; border-radius:8px; padding:10px 16px;'>"
                        f"<b style='color:{text_col};'>{nombre}</b> &nbsp;"
                        f"<span style='color:{color}; font-size:13px; font-weight:bold;'>{estado_label}</span><br>"
                        f"<span style='color:#64748b; font-size:12px;'>Última consulta: {fecha_ultima} · "
                        f"Control programado cada: {meses} meses · 📞 {tel or 'Sin número'}</span>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                with col_wa:
                    if tel and tel != "nan" and tel.strip():
                        msg = (
                            f"¡Hola, {nombre}! ✨ Esperamos que estés teniendo un excelente día.\n\n"
                            f"En Happy Vision nos importa tu bienestar visual. Ya han pasado {meses} meses desde tu última visita el {fecha_ultima}, por lo que es el momento ideal para tu chequeo periódico de rutina. 👁️\n\n"
                            f"¿Te gustaría agendar tu cita para esta semana?\n"
                            f"Responde a este mensaje y coordinamos la hora que te quede más cómoda. ¡Te esperamos!"
                        )
                        link = wa_link(tel, msg)
                        st.markdown(
                            f'<a href="{link}" target="_blank">'
                            f'<button style="background:#25D366;color:white;border:none;border-radius:6px;'
                            f'padding:8px 10px;cursor:pointer;font-size:13px;width:100%;margin-top:4px;font-weight:bold;">'
                            f'📲 Invitar</button></a>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.caption("Sin número")

        st.markdown("---")

        with st.expander("📋 Ver todos los pacientes y sus próximos controles"):
            df_show = df_ultima[["nombre", "fecha", "proximo_control", "dias_para_control", "telefono", "meses_proximo_control"]].copy()
            df_show.columns = ["Paciente", "Última Consulta", "Próximo Control", "Días restantes", "Teléfono", "Meses intervalo"]
            df_show = df_show.sort_values("Días restantes")
            st.dataframe(df_show, use_container_width=True, hide_index=True)

    # ── TAB 2: SEGMENTACIÓN DE PACIENTES ────────────────────────────
    with tab_segmentacion:
        st.subheader("🎯 Clasificación de Clientes")
        st.caption("Filtra y agrupa a tus pacientes según su valor para la óptica para realizar campañas de marketing directas.")

        # Cargar historial de ventas para segmento VIP
        try:
            df_ventas = cargar_ventas_historial(None)
        except Exception:
            df_ventas = pd.DataFrame()

        # 1. SEGMENTO VIP
        # Clientes con compras acumuladas > $150
        vips = []
        if not df_ventas.empty:
            df_ventas["total"] = pd.to_numeric(df_ventas["total"], errors="coerce").fillna(0.0)
            df_compras_usr = df_ventas.groupby("cliente")["total"].sum().reset_index()
            df_vips = df_compras_usr[df_compras_usr["total"] >= 150.0]
            vips = df_vips["cliente"].tolist()

        # 2. SEGMENTO FRECUENTE
        # Clientes con 2 o más consultas / historias clínicas
        df_h_count = df_h.groupby("paciente_id").size().reset_index(name="consultas")
        df_frecuentes_ids = df_h_count[df_h_count["consultas"] >= 2]["paciente_id"].tolist()

        # 3. SEGMENTO INACTIVO
        # Sin consultas en los últimos 6 meses (180 días) o sin ninguna consulta
        inactivos = []
        hoy_dt = date.today()
        limite_inactividad = hoy_dt - timedelta(days=180)
        
        # Pacientes que sí tienen consultas pero la última fue hace más de 180 días
        df_h_sorted = df_h.sort_values("fecha", ascending=False)
        df_ult_consultas = df_h_sorted.drop_duplicates(subset=["paciente_id"], keep="first").copy()
        
        # Pacientes inactivos por tiempo
        for _, prow in df_p.iterrows():
            p_id = prow["id"]
            # Buscar su última consulta
            match_c = df_ult_consultas[df_ult_consultas["paciente_id"] == p_id]
            if not match_c.empty:
                try:
                    f_c = datetime.strptime(str(match_c.iloc[0]["fecha"])[:10], "%Y-%m-%d").date()
                    if f_c < limite_inactividad:
                        inactivos.append(prow["id"])
                except Exception:
                    pass
            else:
                # Nunca ha tenido una consulta clínica registrada
                inactivos.append(prow["id"])

        # Armar dataframes finales para visualización
        df_p_vips = df_p[df_p["nombre"].isin(vips)].copy()
        df_p_frecuentes = df_p[df_p["id"].isin(df_frecuentes_ids)].copy()
        df_p_inactivos = df_p[df_p["id"].isin(inactivos)].copy()

        # Renderizar en la interfaz
        col_vip, col_frec, col_inac = st.columns(3)
        
        # Tarjetas estéticas
        col_vip.markdown(f"""
            <div style="background:#fef2f2; border:1px solid #fee2e2; border-left:4px solid #ef4444; border-radius:10px; padding:15px; text-align:center;">
                <div style="font-size:28px;">💎</div>
                <h4 style="margin:6px 0; color:#991b1b;">Pacientes VIP</h4>
                <div style="font-size:20px; font-weight:800; color:#b91c1c;">{len(df_p_vips)}</div>
                <div style="font-size:11px; color:#ef4444; font-weight:600; text-transform:uppercase;">Compras &ge; $150</div>
            </div>
        """, unsafe_allow_html=True)
        
        col_frec.markdown(f"""
            <div style="background:#eff6ff; border:1px solid #dbeafe; border-left:4px solid #3b82f6; border-radius:10px; padding:15px; text-align:center;">
                <div style="font-size:28px;">🔥</div>
                <h4 style="margin:6px 0; color:#1e40af;">Frecuentes</h4>
                <div style="font-size:20px; font-weight:800; color:#1d4ed8;">{len(df_p_frecuentes)}</div>
                <div style="font-size:11px; color:#2563eb; font-weight:600; text-transform:uppercase;">&ge; 2 Consultas</div>
            </div>
        """, unsafe_allow_html=True)
        
        col_inac.markdown(f"""
            <div style="background:#f9fafb; border:1px solid #f3f4f6; border-left:4px solid #94a3b8; border-radius:10px; padding:15px; text-align:center;">
                <div style="font-size:28px;">💤</div>
                <h4 style="margin:6px 0; color:#374151;">Inactivos</h4>
                <div style="font-size:20px; font-weight:800; color:#4b5563;">{len(df_p_inactivos)}</div>
                <div style="font-size:11px; color:#64748b; font-weight:600; text-transform:uppercase;">&gt; 6 meses sin consulta</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Selección de segmento para interactuar
        segmento_sel = st.selectbox("Selecciona un segmento para ver la lista de pacientes:",
                                      ["💎 Segmento VIP", "🔥 Segmento Frecuentes", "💤 Segmento Inactivos"])
        
        df_sel = pd.DataFrame()
        campania_msg = ""
        
        if segmento_sel == "💎 Segmento VIP":
            df_sel = df_p_vips
            campania_msg = "¡Hola! Como cliente exclusivo VIP de Happy Vision, queremos agradecerte tu preferencia obsequiándote un 20% de descuento en lunas fotocromáticas esta semana. ¡Responde a este mensaje para agendar!"
        elif segmento_sel == "🔥 Segmento Frecuentes":
            df_sel = df_p_frecuentes
            campania_msg = "¡Hola! Esperamos que te encuentres muy bien. Queremos obsequiarte una limpieza ultrasónica gratuita para tus lentes por ser un cliente frecuente de Happy Vision. ¡Te esperamos en cualquier momento!"
        else:
            df_sel = df_p_inactivos
            campania_msg = "¡Hola! Te extrañamos en Happy Vision. Ha pasado algún tiempo desde tu último chequeo visual. Te invitamos a agendar un examen visual preventivo esta semana para asegurar que tu medida esté actualizada."

        if df_sel.empty:
            st.info("No hay pacientes en este segmento por el momento.")
        else:
            st.markdown(f"**Lista de Pacientes ({len(df_sel)}):**")
            
            for _, r_p in df_sel.iterrows():
                nombre = r_p.get("nombre", "")
                tel = str(r_p.get("telefono", "")).strip()
                ident = r_p.get("identificacion", "")
                
                c_info, c_action = st.columns([4, 1.5])
                c_info.markdown(f"""
                    <div style="background:white; border:1px solid #e2e8f0; border-radius:6px; padding:8px 12px; margin-bottom:4px;">
                        <b>{nombre}</b> <span style="font-size:11px; color:#64748b;">(C.I. {ident})</span>
                        <br><span style="font-size:11px; color:#94a3b8;">Teléfono: {tel or 'Sin teléfono'}</span>
                    </div>
                """, unsafe_allow_html=True)
                
                if tel and tel != "nan" and tel.strip():
                    link_c = wa_link(tel, campania_msg)
                    c_action.markdown(f'''
                        <a href="{link_c}" target="_blank">
                            <button style="background:#25D366; color:white; border:none; padding:8px 10px; border-radius:6px; cursor:pointer; width:100%; margin-top:2px; font-weight:bold; font-size:12px;">
                                📲 Enviar Promo
                            </button>
                        </a>
                    ''', unsafe_allow_html=True)
                else:
                    c_action.caption("Sin número")

# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils import wa_link


def render_crm():
    st.markdown("""
    <div class="page-header">
        <h1>📡 Seguimiento CRM</h1>
        <p>Retención de pacientes · Alertas de próximos controles · Recordatorios automáticos</p>
    </div>
    """, unsafe_allow_html=True)

    df_h = st.session_state.df_historias.copy()
    df_p = st.session_state.df_pacientes.copy()

    if len(df_h) == 0 or len(df_p) == 0:
        st.info("📭 No hay historias clínicas o pacientes registrados aún. El CRM se activará cuando haya datos.")
        return

    # ── Calcular fecha de próximo control ─────────────────────────
    today = datetime.today().date()

    def proximo_control(row):
        try:
            fecha_consulta = datetime.strptime(str(row["fecha"]), "%Y-%m-%d").date()
            meses = int(float(row.get("meses_proximo_control", 12) or 12))
            # Sumar meses aproximadamente
            return fecha_consulta + timedelta(days=meses * 30)
        except Exception:
            return None

    df_h["proximo_control"] = df_h.apply(proximo_control, axis=1)

    # Tomar la consulta más reciente por paciente
    df_h_sorted     = df_h.sort_values("fecha", ascending=False)
    df_ultima       = df_h_sorted.drop_duplicates(subset=["paciente_id"], keep="first").copy()
    df_ultima       = df_ultima.merge(df_p[["id","nombre","telefono"]], left_on="paciente_id", right_on="id", how="left", suffixes=("","_pac"))

    # Calcular días restantes
    df_ultima["dias_para_control"] = df_ultima["proximo_control"].apply(
        lambda d: (d - today).days if d is not None else None
    )

    # ── ALERTAS: vencidos o próximos 30 días ──────────────────────
    mask_alerta = df_ultima["dias_para_control"].apply(
        lambda d: d is not None and d <= 30
    )
    df_alerta = df_ultima[mask_alerta].sort_values("dias_para_control")

    # ── KPIs ──────────────────────────────────────────────────────
    total_pac    = len(df_ultima)
    vencidos     = len(df_ultima[df_ultima["dias_para_control"].apply(lambda d: d is not None and d < 0)])
    proximos_30  = len(df_alerta[df_alerta["dias_para_control"].apply(lambda d: d is not None and 0 <= d <= 30)])
    al_dia       = total_pac - len(df_alerta)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("👥 Total pacientes",     total_pac)
    k2.metric("🔴 Controles vencidos",  vencidos)
    k3.metric("🟡 Control en 30 días",  proximos_30)
    k4.metric("🟢 Al día",              al_dia)

    st.markdown("---")

    # ── TABLA DE ALERTAS ──────────────────────────────────────────
    if len(df_alerta) == 0:
        st.success("✅ ¡Excelente! Ningún paciente tiene control vencido o próximo. Todos están al día.")
    else:
        st.markdown("<div class='section-title'>🚨 Pacientes que requieren contacto</div>", unsafe_allow_html=True)
        st.caption("Controles vencidos o que vencen en los próximos 30 días.")

        for _, row in df_alerta.iterrows():
            dias   = row.get("dias_para_control")
            nombre = row.get("nombre", row.get("paciente_nombre", ""))
            tel    = str(row.get("telefono", "")).strip()
            fecha_ultima = row.get("fecha", "")
            fecha_control = row.get("proximo_control")
            meses  = row.get("meses_proximo_control", 12)

            if dias is not None and dias < 0:
                estado_label = f"🔴 Vencido hace {abs(dias)} días"
                color        = "#ef4444"
                bg           = "#450a0a"
            else:
                estado_label = f"🟡 Vence en {dias} días ({fecha_control})"
                color        = "#f59e0b"
                bg           = "#431407"

            col_info, col_wa = st.columns([5, 1])
            with col_info:
                st.markdown(
                    f"<div style='background:{bg}; border-left:4px solid {color}; border-radius:8px; padding:10px 16px;'>"
                    f"<b style='color:#e2e8f0;'>{nombre}</b> &nbsp;"
                    f"<span style='color:{color}; font-size:13px;'>{estado_label}</span><br>"
                    f"<span style='color:#94a3b8; font-size:12px;'>Última consulta: {fecha_ultima} · "
                    f"Control programado cada: {meses} meses · 📞 {tel or 'Sin número'}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            with col_wa:
                if tel:
                    msg = (
                        f"¡Hola, {nombre}! ✨ Esperamos que estés teniendo un excelente día.\n\n"
                        f"En Happy Vision nos importa tu bienestar visual. Ya han pasado {meses} meses desde tu última visita el {fecha_ultima}, por lo que es el momento ideal para tu chequeo periódico de rutina. 👁️\n\n"
                        f"¿Te gustaría agendar tu cita para esta semana?\n"
                        f"📱 Responde directamente a este mensaje y coordinamos el día y la hora que te queden más cómodos. ¡Te esperamos!"
                    )
                    link = wa_link(tel, msg)
                    st.markdown(
                        f'<a href="{link}" target="_blank">'
                        f'<button style="background:#25D366;color:white;border:none;border-radius:6px;'
                        f'padding:8px 10px;cursor:pointer;font-size:13px;width:100%;margin-top:4px;">'
                        f'📲 Invitar</button></a>',
                        unsafe_allow_html=True
                    )
                else:
                    st.caption("Sin número")

    st.markdown("---")

    # ── TABLA COMPLETA ─────────────────────────────────────────────
    with st.expander("📋 Ver todos los pacientes y sus próximos controles"):
        df_show = df_ultima[["nombre","fecha","proximo_control","dias_para_control","telefono","meses_proximo_control"]].copy()
        df_show.columns = ["Paciente","Última Consulta","Próximo Control","Días restantes","Teléfono","Meses intervalo"]
        df_show = df_show.sort_values("Días restantes")
        st.dataframe(df_show, use_container_width=True, hide_index=True)

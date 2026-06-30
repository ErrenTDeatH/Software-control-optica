import streamlit as st
import pandas as pd
from datetime import date
from utils import wa_link, generar_pdf_historia, generar_msg_indicaciones
from database import eliminar_historia, actualizar_historia


def _render_lectura_historia(hrow):
    """Muestra la historia clínica en modo lectura con un diseño premium tipo ficha médica."""
    def _p(s, i):
        pts = str(s).split("|") if s else []
        return pts[i].strip() if i < len(pts) else "—"

    def _val(v):
        return str(v) if v and str(v).strip() and str(v) != "nan" else "—"

    rx_od = hrow.get('rx_od')
    rx_oi = hrow.get('rx_oi')
    lenso_od = hrow.get('lenso_od')
    lenso_oi = hrow.get('lenso_oi')

    st.markdown("""
    <style>
    .hc-card { background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:16px 20px; margin-bottom:12px; }
    .hc-card-blue { background:linear-gradient(135deg,#eff6ff,#dbeafe); border:1px solid #bfdbfe; border-radius:12px; padding:16px 20px; margin-bottom:12px; }
    .hc-card-green { background:linear-gradient(135deg,#f0fdf4,#dcfce7); border:1px solid #86efac; border-radius:12px; padding:16px 20px; margin-bottom:12px; }
    .hc-card-amber { background:linear-gradient(135deg,#fffbeb,#fef3c7); border:1px solid #fcd34d; border-radius:12px; padding:16px 20px; margin-bottom:12px; }
    .hc-section-title { font-size:13px; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:.06em; margin-bottom:10px; }
    .hc-label { font-size:11px; color:#94a3b8; font-weight:600; text-transform:uppercase; letter-spacing:.05em; margin-bottom:2px; }
    .hc-value { font-size:15px; color:#1e293b; font-weight:600; margin-bottom:0; }
    .hc-value-mono { font-family:monospace; font-size:14px; color:#1e40af; font-weight:700; }
    .hc2-header {
        background: linear-gradient(135deg,#0f172a,#1e3a8a);
        border-radius:16px; padding:20px 28px; margin-bottom:14px; color:white;
        display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;
    }
    .hc2-section {
        border-radius:12px; padding:14px 18px; margin-bottom:12px;
    }
    .hc2-section-title {
        font-size:12px; font-weight:800; text-transform:uppercase;
        letter-spacing:.07em; margin-bottom:10px; display:flex; align-items:center; gap:6px;
    }
    .rx-table { width:100%; border-collapse:collapse; font-size:13px; }
    .rx-table th {
        background:#1e3a8a; color:white; font-weight:700; font-size:11px;
        text-transform:uppercase; letter-spacing:.05em;
        padding:7px 10px; text-align:center;
    }
    .rx-table th.rx-th-eye { background:#0f172a; text-align:left; width:110px; }
    .rx-table td {
        padding:8px 10px; text-align:center; font-family:monospace;
        font-size:14px; font-weight:700; border-bottom:1px solid #e2e8f0;
        color:#1e293b;
    }
    .rx-table td.rx-eye-label {
        font-family:sans-serif; font-size:11px; font-weight:800;
        color:white; text-align:left; white-space:nowrap;
    }
    .rx-table tr.rx-od td.rx-eye-label { background:#3b82f6; }
    .rx-table tr.rx-oi td.rx-eye-label { background:#8b5cf6; }
    .rx-table tr:last-child td { border-bottom:none; }
    .rx-table td.rx-dash { color:#cbd5e1; font-weight:400; }
    .hc2-pill {
        display:inline-flex; align-items:center; gap:5px;
        padding:4px 12px; border-radius:20px; font-size:12px; font-weight:700;
    }
    .hc2-pill-blue   { background:#dbeafe; color:#1d4ed8; }
    .hc2-pill-green  { background:#dcfce7; color:#15803d; }
    .hc2-pill-red    { background:#fee2e2; color:#dc2626; }
    .hc2-pill-amber  { background:#fef3c7; color:#92400e; }
    .hc2-pill-purple { background:#ede9fe; color:#6d28d9; }
    </style>
    """, unsafe_allow_html=True)



    # ─── ENCABEZADO ───────────────────────────────────────────
    fecha  = _val(hrow.get('fecha'))
    motivo = _val(hrow.get('motivo'))
    diag   = _val(hrow.get('diagnostico'))
    opto   = _val(hrow.get('optometrista'))
    diag_short = diag[:60] + "…" if len(diag) > 60 else diag

    st.markdown(f"""
    <div class="hc2-header">
        <div>
            <div style="font-size:10px;color:#93c5fd;letter-spacing:.1em;text-transform:uppercase;font-weight:700">
                Historia Clínica Optométrica
            </div>
            <div style="font-size:19px;font-weight:800;margin-top:3px">📋 {motivo}</div>
            <div style="font-size:12px;color:#bfdbfe;margin-top:6px">👨‍⚕️ <b>{opto}</b></div>
        </div>
        <div style="text-align:right">
            <div style="font-size:11px;color:#93c5fd">Fecha de consulta</div>
            <div style="font-size:20px;font-weight:800;letter-spacing:-.5px">📅 {fecha}</div>
            <div style="margin-top:8px"><span class="hc2-pill hc2-pill-green">✅ {diag_short}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─── ANTECEDENTES ─────────────────────────────────────────
    ant_p = _val(hrow.get('ant_personales'))
    ant_f = _val(hrow.get('ant_familiares'))

    st.markdown(f"""
    <div class="hc2-section" style="background:#f8fafc;border:1px solid #e2e8f0">
        <div class="hc2-section-title" style="color:#475569">👤 Antecedentes</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
            <div>
                <div style="font-size:10px;color:#94a3b8;font-weight:700;text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px">Personales</div>
                <div style="font-size:14px;color:#1e293b;font-weight:600">{ant_p}</div>
            </div>
            <div>
                <div style="font-size:10px;color:#94a3b8;font-weight:700;text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px">Familiares</div>
                <div style="font-size:14px;color:#1e293b;font-weight:600">{ant_f}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─── HELPER: celda tabla ──────────────────────────────────
    def _c(v):
        val = v if v and str(v).strip() and str(v) not in ("—", "nan", "None", "") else "—"
        cls = "rx-dash" if val == "—" else ""
        return f'<td class="{cls}">{val}</td>'

    # ─── LENSOMETRÍA ──────────────────────────────────────────
    lo_esf = _p(lenso_od,0); lo_cyl = _p(lenso_od,1)
    lo_eje = _p(lenso_od,2); lo_add = _p(lenso_od,3)
    li_esf = _p(lenso_oi,0); li_cyl = _p(lenso_oi,1)
    li_eje = _p(lenso_oi,2); li_add = _p(lenso_oi,3)
    lo_avl = _val(hrow.get('lenso_av_lej_od')); lo_avc = _val(hrow.get('lenso_av_cer_od'))
    li_avl = _val(hrow.get('lenso_av_lej_oi')); li_avc = _val(hrow.get('lenso_av_cer_oi'))

    avl_od_cls = 'rx-dash' if lo_avl == '—' else ''
    avl_oi_cls = 'rx-dash' if li_avl == '—' else ''

    st.markdown(f"""
    <div class="hc2-section" style="background:linear-gradient(135deg,#eff6ff,#dbeafe);border:1px solid #bfdbfe">
        <div class="hc2-section-title" style="color:#1d4ed8">🔍 Lensometría &nbsp;·&nbsp; Rx en Uso &nbsp;·&nbsp; Agudeza Visual S/C</div>
        <table class="rx-table">
            <thead>
                <tr>
                    <th class="rx-th-eye">Ojo</th>
                    <th>ESF</th><th>CYL</th><th>EJE</th><th>ADD</th>
                    <th style="border-left:2px solid #3b82f6">AV Lejos</th>
                    <th>AV Cerca</th>
                </tr>
            </thead>
            <tbody>
                <tr class="rx-od">
                    <td class="rx-eye-label">🔵 OD &nbsp;Derecho</td>
                    {_c(lo_esf)}{_c(lo_cyl)}{_c(lo_eje)}{_c(lo_add)}
                    <td style="border-left:2px solid #3b82f6" class="{avl_od_cls}">{lo_avl}</td>
                    {_c(lo_avc)}
                </tr>
                <tr class="rx-oi">
                    <td class="rx-eye-label">🟣 OI &nbsp;Izquierdo</td>
                    {_c(li_esf)}{_c(li_cyl)}{_c(li_eje)}{_c(li_add)}
                    <td style="border-left:2px solid #3b82f6" class="{avl_oi_cls}">{li_avl}</td>
                    {_c(li_avc)}
                </tr>
            </tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)

    # ─── REFRACCIÓN FINAL ─────────────────────────────────────
    ro_esf = _p(rx_od,0); ro_cyl = _p(rx_od,1); ro_eje = _p(rx_od,2); ro_add = _p(rx_od,3)
    ro_dnp = _p(rx_od,4); ro_alt = _p(rx_od,5); ro_dp  = _p(rx_od,6); ro_av  = _p(rx_od,7)
    ri_esf = _p(rx_oi,0); ri_cyl = _p(rx_oi,1); ri_eje = _p(rx_oi,2); ri_add = _p(rx_oi,3)
    ri_dnp = _p(rx_oi,4); ri_alt = _p(rx_oi,5); ri_dp  = _p(rx_oi,6); ri_av  = _p(rx_oi,7)
    ro_avl = _val(hrow.get('rx_av_lej_od')); ro_avc = _val(hrow.get('rx_av_cer_od'))
    ri_avl = _val(hrow.get('rx_av_lej_oi')); ri_avc = _val(hrow.get('rx_av_cer_oi'))

    ro_dnp_cls = 'rx-dash' if ro_dnp == '—' else ''
    ri_dnp_cls = 'rx-dash' if ri_dnp == '—' else ''
    ro_avl_cls = 'rx-dash' if ro_avl == '—' else ''
    ri_avl_cls = 'rx-dash' if ri_avl == '—' else ''

    st.markdown(f"""
    <div class="hc2-section" style="background:linear-gradient(135deg,#f0fdf4,#dcfce7);border:1px solid #86efac">
        <div class="hc2-section-title" style="color:#15803d">✨ Refracción Final &nbsp;·&nbsp; Rx Actual &nbsp;·&nbsp; Agudeza Visual C/C</div>
        <table class="rx-table">
            <thead>
                <tr>
                    <th class="rx-th-eye">Ojo</th>
                    <th>ESF</th><th>CYL</th><th>EJE</th><th>ADD</th>
                    <th style="border-left:2px solid #22c55e">DNP</th>
                    <th>ALT</th><th>DP</th><th>A/V</th>
                    <th style="border-left:2px solid #22c55e">AV Lejos</th>
                    <th>AV Cerca</th>
                </tr>
            </thead>
            <tbody>
                <tr class="rx-od">
                    <td class="rx-eye-label">🔵 OD &nbsp;Derecho</td>
                    {_c(ro_esf)}{_c(ro_cyl)}{_c(ro_eje)}{_c(ro_add)}
                    <td style="border-left:2px solid #22c55e" class="{ro_dnp_cls}">{ro_dnp}</td>
                    {_c(ro_alt)}{_c(ro_dp)}{_c(ro_av)}
                    <td style="border-left:2px solid #22c55e" class="{ro_avl_cls}">{ro_avl}</td>
                    {_c(ro_avc)}
                </tr>
                <tr class="rx-oi">
                    <td class="rx-eye-label">🟣 OI &nbsp;Izquierdo</td>
                    {_c(ri_esf)}{_c(ri_cyl)}{_c(ri_eje)}{_c(ri_add)}
                    <td style="border-left:2px solid #22c55e" class="{ri_dnp_cls}">{ri_dnp}</td>
                    {_c(ri_alt)}{_c(ri_dp)}{_c(ri_av)}
                    <td style="border-left:2px solid #22c55e" class="{ri_avl_cls}">{ri_avl}</td>
                    {_c(ri_avc)}
                </tr>
            </tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)

    # ─── RESUMEN CLÍNICO (PILLS) ──────────────────────────────
    necesita = _val(hrow.get('necesita_lentes'))
    color_t  = _val(hrow.get('test_color'))
    proximo  = _val(hrow.get('meses_proximo_control'))
    obs      = _val(hrow.get('observaciones'))
    rec      = _val(hrow.get('recomendaciones'))

    lentes_pill = '<span class="hc2-pill hc2-pill-blue">👓 Sí, necesita lentes</span>' \
        if necesita == "SI" else '<span class="hc2-pill hc2-pill-green">✅ No necesita lentes</span>'
    color_pill  = '<span class="hc2-pill hc2-pill-red">⚠️ Daltonismo detectado</span>' \
        if "dalton" in color_t.lower() else '<span class="hc2-pill hc2-pill-green">✅ Test de color normal</span>'
    ctrl_pill   = f'<span class="hc2-pill hc2-pill-purple">📅 Próx. control: {proximo}</span>'

    st.markdown(f"""
    <div class="hc2-section" style="background:#f8fafc;border:1px solid #e2e8f0">
        <div class="hc2-section-title" style="color:#475569">📊 Resumen Clínico</div>
        <div style="display:flex;flex-wrap:wrap;gap:8px">
            {lentes_pill} {color_pill} {ctrl_pill}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─── OBSERVACIONES Y RECOMENDACIONES ─────────────────────
    if obs != "—" or rec != "—":
        obs_label = '<div style="font-size:10px;color:#475569;font-weight:700;text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px">Observaciones</div>' if obs != "—" else ""
        obs_html  = f'<div style="font-size:14px;color:#1e293b;line-height:1.6;margin-bottom:12px">{obs}</div>' if obs != "—" else ""
        rec_label = '<div style="font-size:10px;color:#92400e;font-weight:700;text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px">💡 Indicaciones al Paciente</div>' if rec != "—" else ""
        rec_html  = f'<div style="font-size:14px;color:#78350f;line-height:1.6">{rec}</div>' if rec != "—" else ""
        st.markdown(f"""
        <div class="hc2-section" style="background:linear-gradient(135deg,#fffbeb,#fef3c7);border:1px solid #fcd34d">
            <div class="hc2-section-title" style="color:#92400e">📝 Observaciones y Recomendaciones</div>
            {obs_label}{obs_html}{rec_label}{rec_html}
        </div>
        """, unsafe_allow_html=True)


def render_clinica():
    st.markdown("""
    <div class="page-header">
        <h1>👥 Pacientes</h1>
        <p>Directorio de pacientes, historial clínico y gestión de consultas</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── BUSCADOR ────────────────────────────────────────────
    st.markdown("<div class='section-title'>🔍 Buscar Paciente</div>", unsafe_allow_html=True)
    busca_col, nuevo_col = st.columns([3, 1])
    with busca_col:
        if "clinica_buscar" in st.session_state and st.session_state["clinica_buscar"]:
            st.session_state["buscador_act"] = st.session_state["clinica_buscar"]
            st.session_state["clinica_buscar"] = ""
        q = st.text_input("Buscador", key="buscador_act", placeholder="Escribe el nombre o cédula del paciente...", label_visibility="collapsed")
    with nuevo_col:
        mostrar_form_nuevo = st.button("➕ Nuevo Paciente", use_container_width=True, type="secondary")

    sucursal_actual = st.session_state.get("sucursal_activa", "Matriz")
    
    if "sucursal" in st.session_state.df_pacientes.columns:
        df_p_all = st.session_state.df_pacientes[st.session_state.df_pacientes["sucursal"] == sucursal_actual].copy()
    else:
        df_p_all = st.session_state.df_pacientes.copy()

    # ── Formulario NUEVO PACIENTE ────────────────────────────
    if mostrar_form_nuevo:
        st.session_state["mostrar_nuevo_p"] = not st.session_state.get("mostrar_nuevo_p", False)

    if st.session_state.get("mostrar_nuevo_p", False):
        with st.form("nuevo_paciente", clear_on_submit=True):
            st.markdown("<div class='section-title'>Registrar Nuevo Paciente</div>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns([1, 1.5, 1.5, 1])
            p_id        = c1.text_input("Cédula/ID")
            p_nombres   = c2.text_input("Nombres *")
            p_apellidos = c3.text_input("Apellidos *")
            p_genero    = c4.selectbox("Género", ["Masculino", "Femenino", "Otro"])

            col_p4, col_p5, col_p6 = st.columns([1.5, 1, 1.5])
            p_fnac  = col_p4.date_input("Fecha de Nacimiento", value=date(1990,1,1), min_value=date(1900,1,1), max_value=date.today())
            p_edad_manual = col_p5.number_input("O Edad", min_value=0, max_value=120, value=0)
            p_tel   = col_p6.text_input("Teléfono")
            
            col_p7, col_p8, col_p9 = st.columns([1.5, 1.5, 1])
            p_email = col_p7.text_input("Correo")
            p_dir   = col_p8.text_input("Dirección")
            p_ocupa = col_p9.text_input("Ocupación")

            colbtn1, _ = st.columns([2, 1])
            if colbtn1.form_submit_button("✅ Guardar Paciente", type="primary", use_container_width=True):
                # 1. Validaciones básicas
                id_input = str(p_id).strip()
                nom_input = p_nombres.strip()
                ape_input = p_apellidos.strip()
                nombre_completo_input = f"{ape_input} {nom_input}"

                if not nom_input or not ape_input:
                    st.error("⚠️ Nombres y Apellidos son obligatorios.")
                else:
                    # 2. Verificar duplicados (Directo en DB para máxima seguridad)
                    from database import supabase
                    existe_en_db = False
                    nombre_existente = ""
                    sucursal_existente = ""
                    if id_input and supabase:
                        try:
                            check_db = supabase.table("pacientes").select("id, nombre, sucursal").eq("identificacion", id_input).execute()
                            if check_db.data:
                                existe_en_db = True
                                nombre_existente = check_db.data[0].get("nombre", "Desconocido")
                                sucursal_existente = check_db.data[0].get("sucursal", "otra sucursal")
                        except:
                            if id_input in st.session_state.df_pacientes["identificacion"].astype(str).tolist():
                                existe_en_db = True
                                sucursal_existente = "Caché local"
                    
                    if existe_en_db:
                        st.error(f"🚫 ERROR: El paciente con cédula **{id_input}** ya está registrado como **{nombre_existente}** en **{sucursal_existente}**.")
                    else:
                        # 3. Guardar si todo está bien
                        hoy = date.today()
                        if p_edad_manual > 0:
                            final_edad = p_edad_manual
                            final_fnac = ""
                        else:
                            final_edad = hoy.year - p_fnac.year - ((hoy.month, hoy.day) < (p_fnac.month, p_fnac.day))
                            final_fnac = p_fnac.strftime("%Y-%m-%d")

                        # Calcular ID de forma segura
                        df_p_current = st.session_state.df_pacientes
                        if not df_p_current.empty and "id" in df_p_current.columns:
                            max_id = pd.to_numeric(df_p_current["id"], errors="coerce").max()
                            nuevo_id = int(max_id + 1) if pd.notna(max_id) else 1
                        else:
                            nuevo_id = 1

                        nuevo_p = {
                            "id": nuevo_id,
                            "identificacion": id_input,
                            "nombre": nombre_completo_input,
                            "nombres": nom_input,
                            "apellidos": ape_input,
                            "genero": p_genero,
                            "edad": str(final_edad),
                            "fecha_nacimiento": final_fnac,
                            "telefono": p_tel.strip(),
                            "correo": p_email.strip(),
                            "direccion": p_dir.strip(),
                            "ocupacion": p_ocupa.strip(),
                            "sucursal": sucursal_actual
                        }
                        st.session_state.df_pacientes = pd.concat([st.session_state.df_pacientes, pd.DataFrame([nuevo_p])], ignore_index=True)
                        from database import guardar_paciente
                        guardar_paciente(nuevo_p)
                        # AUDITORÍA: Nuevo Paciente
                        from database import registrar_auditoria
                        registrar_auditoria(
                            accion="Registrar Nuevo Paciente",
                            entidad="Paciente",
                            detalle=f"Paciente: {nombre_completo_input} | ID: {nuevo_id} | Cédula: {id_input}",
                            usuario=st.session_state.get("user_login", ""),
                            nombre_usuario=st.session_state.get("user_name", ""),
                            sucursal=sucursal_actual
                        )
                        st.success(f"✅ Paciente **{nombre_completo_input}** registrado.")
                        st.session_state["mostrar_nuevo_p"] = False
                        st.rerun()

    # ── RESULTADOS DE BÚSQUEDA ────────────────────────
    if q:
        def limpiar_buscador():
            st.session_state["buscador_act"] = ""
            
        # Botón para volver al listado
        st.button("← Volver al listado", key="btn_volver_listado", on_click=limpiar_buscador)
        st.markdown("---")

        resultados = df_p_all[
            df_p_all["nombre"].str.contains(q, case=False, na=False) |
            df_p_all["identificacion"].astype(str).str.contains(q, case=False, na=False)
        ]
        if len(resultados) == 0:
            st.info(f"No se encontró '«{q}»'. Usa ➕ Nuevo Paciente.")
        else:
            for _, pac in resultados.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div style='background: #f0f9ff; border-radius: 12px; padding: 14px 20px; border: 1px solid #bae6fd; border-left: 6px solid #0284c7; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); margin-bottom: 12px;'>
                        <div style='color: #0c4a6e; font-size: 18px; font-weight: 800; margin-bottom: 4px;'>{pac.get('nombre','').upper()}</div>
                        <div style='color: #0369a1; font-size: 13px; font-weight: 500; display: flex; flex-wrap: wrap; gap: 12px;'>
                            <span>🆔 <b>{pac.get('identificacion','')}</b></span>
                            <span style='color: #94a3b8;'>|</span>
                            <span>📅 <b>{pac.get('edad','')} años</b></span>
                            <span style='color: #94a3b8;'>|</span>
                            <span>📞 <b>{pac.get('telefono','')}</b></span>
                            <span style='color: #94a3b8;'>|</span>
                            <span>⚧️ <b>{pac.get('genero','')}</b></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    hist_pac = st.session_state.df_historias[
                        st.session_state.df_historias["paciente_id"] == pac["id"]
                    ].sort_values("fecha", ascending=False)

                    ca, cb, cc = st.columns([3, 1, 1])
                    ca.caption(f"🗂️ {len(hist_pac)} consulta(s)")

                    with cb:
                        if st.button("📋 Nueva Consulta", key=f"new_h_{pac['id']}", use_container_width=True, type="primary"):
                            st.session_state["nueva_consulta_paciente"] = pac["nombre"]
                            st.rerun()

                    with cc:
                        if st.button("✏️ Editar Datos", key=f"edit_p_{pac['id']}", use_container_width=True):
                            st.session_state["editar_paciente_id"] = pac["id"]

                    # Editar datos del paciente
                    if st.session_state.get("editar_paciente_id") == pac["id"]:
                        with st.form(f"edit_pac_{pac['id']}", clear_on_submit=False):
                            ec1, ec2, ec3, ec4 = st.columns([1, 1.5, 1.5, 1])
                            e_id  = ec1.text_input("Cédula", value=str(pac.get("identificacion", "")))
                            e_nom = ec2.text_input("Nombres", value=str(pac.get("nombres", pac.get("nombre","").split()[-1] if pac.get("nombre") else "")))
                            e_ape = ec3.text_input("Apellidos", value=str(pac.get("apellidos", pac.get("nombre","").split()[0] if pac.get("nombre") else "")))
                            e_gen = ec4.selectbox("Género", ["Masculino","Femenino","Otro"],
                                index=["Masculino","Femenino","Otro"].index(pac.get("genero","Masculino"))
                                      if pac.get("genero","Masculino") in ["Masculino","Femenino","Otro"] else 0)
                            ec5, ec6, ec7 = st.columns([1.5, 1, 1.5])
                            fnac_val  = pac.get("fecha_nacimiento", "")
                            default_d = date(1990,1,1)
                            if fnac_val and str(fnac_val) not in ("", "nan", "None", "NaT"):
                                try: default_d = date.fromisoformat(str(fnac_val)[:10])
                                except: pass
                            e_fnac = ec5.date_input("Fecha de Nacimiento", value=default_d, min_value=date(1900,1,1), max_value=date.today())
                            e_edad_manual = ec6.number_input("O Edad", min_value=0, max_value=120, value=int(pac.get("edad", 0)) if not fnac_val else 0)
                            e_tel  = ec7.text_input("Teléfono", value=str(pac.get("telefono", "")))
                            
                            ec8, ec9, ec10 = st.columns([1.5, 1.5, 1])
                            e_mail = ec8.text_input("Correo",   value=str(pac.get("correo", "")))
                            e_dir  = ec9.text_input("Dirección", value=str(pac.get("direccion", "")))
                            e_ocu  = ec10.text_input("Ocupación", value=str(pac.get("ocupacion", "")))
                            
                            if st.form_submit_button("💾 Actualizar", type="primary"):
                                idx_p = st.session_state.df_pacientes[st.session_state.df_pacientes["id"] == pac["id"]].index[0]
                                hoy   = date.today()
                                
                                if e_edad_manual > 0 and (not fnac_val or e_edad_manual != (hoy.year - default_d.year)):
                                    final_edad = e_edad_manual
                                    final_fnac = ""
                                else:
                                    final_edad = hoy.year - e_fnac.year - ((hoy.month, hoy.day) < (e_fnac.month, e_fnac.day))
                                    final_fnac = e_fnac.strftime("%Y-%m-%d")

                                nombre_nuevo = f"{e_ape.strip()} {e_nom.strip()}"
                                st.session_state.df_pacientes.at[idx_p, "identificacion"]   = str(e_id)
                                st.session_state.df_pacientes.at[idx_p, "nombre"]           = nombre_nuevo
                                st.session_state.df_pacientes.at[idx_p, "nombres"]          = e_nom.strip()
                                st.session_state.df_pacientes.at[idx_p, "apellidos"]        = e_ape.strip()
                                st.session_state.df_pacientes.at[idx_p, "genero"]           = str(e_gen)
                                st.session_state.df_pacientes.at[idx_p, "fecha_nacimiento"] = final_fnac
                                st.session_state.df_pacientes.at[idx_p, "edad"]             = str(final_edad)
                                st.session_state.df_pacientes.at[idx_p, "telefono"]         = str(e_tel)
                                st.session_state.df_pacientes.at[idx_p, "correo"]           = str(e_mail)
                                st.session_state.df_pacientes.at[idx_p, "direccion"]        = str(e_dir)
                                st.session_state.df_pacientes.at[idx_p, "ocupacion"]        = e_ocu
                                
                                from database import guardar_paciente
                                # Obtenemos la fila actualizada para mandar a DB
                                row_upd = st.session_state.df_pacientes.iloc[idx_p].to_dict()
                                guardar_paciente(row_upd)
                                # AUDITORÍA: Edición de paciente
                                from database import registrar_auditoria
                                registrar_auditoria(
                                    accion="Editar Paciente",
                                    entidad="Paciente",
                                    detalle=f"Paciente: {nombre_nuevo} | Cédula: {str(e_id)}",
                                    usuario=st.session_state.get("user_login", ""),
                                    nombre_usuario=st.session_state.get("user_name", ""),
                                    sucursal=st.session_state.get("sucursal_activa", "")
                                )
                                st.success("✅ Datos actualizados.")
                                st.session_state["editar_paciente_id"] = None
                                st.rerun()

                    # Historias del paciente
                    if len(hist_pac) == 0:
                        st.caption("💭 No hay consultas registradas todavía.")
                    else:
                        for _, hrow in hist_pac.iterrows():
                            h_id = hrow.get('id','')
                            with st.expander(f"📅 Consulta: {hrow.get('fecha','')} — {hrow.get('motivo','Sin motivo')}"):
                                if not st.session_state.get(f"editando_historia_{h_id}", False):
                                    # MODO LECTURA (Toda la historia)
                                    _render_lectura_historia(hrow)
                                    
                                    hact1, hact2 = st.columns(2)
                                    with hact1:
                                        if st.button(f"✏️ Editar Historia", key=f"edit_h_{h_id}", use_container_width=True):
                                            st.session_state[f"editando_historia_{h_id}"] = True
                                            st.rerun()
                                    with hact2:
                                        if st.button(f"🗑️ Eliminar Historia", key=f"del_h_{h_id}", type="secondary", use_container_width=True):
                                            eliminar_historia(h_id)
                                            st.session_state.df_historias = st.session_state.df_historias[
                                                st.session_state.df_historias["id"].astype(str) != str(h_id)
                                            ].reset_index(drop=True)
                                            # AUDITORÍA: Eliminación de historia
                                            from database import registrar_auditoria
                                            registrar_auditoria(
                                                accion="Eliminar Historia Clínica",
                                                entidad="Historia Clínica",
                                                detalle=f"Historia ID: {h_id} | Paciente: {hrow.get('paciente_nombre','')} | Fecha consulta: {hrow.get('fecha','')}",
                                                usuario=st.session_state.get("user_login", ""),
                                                nombre_usuario=st.session_state.get("user_name", ""),
                                                sucursal=st.session_state.get("sucursal_activa", "")
                                            )
                                            st.success("Historia eliminada permanentemente.")
                                            st.rerun()
                                else:
                                    # MODO EDICIÓN (Formulario)
                                    if st.button("⬅️ Volver a vista de lectura", key=f"cancel_edit_{h_id}"):
                                        st.session_state[f"editando_historia_{h_id}"] = False
                                        st.rerun()

                                if st.session_state.get(f"editando_historia_{h_id}", False):
                                    _def = hrow.to_dict()
                                    with st.form(key=f"edit_h_form_{h_id}"):
                                        st.markdown("**Editar Consulta Completa**")
                                        eh_col1, eh_col2 = st.columns(2)
                                        eh_fecha  = eh_col1.date_input("Fecha", value=date.fromisoformat(str(_def.get('fecha', str(date.today())))[:10]))
                                        eh_motivo = eh_col2.text_input("Motivo de la consulta", value=str(_def.get('motivo','')))

                                        st.markdown("**(2) Antecedentes**")
                                        ea1, ea2 = st.columns(2)
                                        eh_ant_per = ea1.text_input("Antecedentes Personales", value=str(_def.get('ant_personales','')))
                                        eh_ant_fam = ea2.text_input("Antecedentes Familiares", value=str(_def.get('ant_familiares','')))

                                        st.markdown("**(3) Agudezas Visuales S/C y C/C)**")
                                        eav1,eav2,eav3,eav4,eav5,eav6 = st.columns([1,2,2,1,2,2])
                                        eav1.markdown("<p style='margin-top:28px;'><b>S/C</b></p>", unsafe_allow_html=True)
                                        eh_av_lej_sc_od = eav2.text_input("Lejos OD S/C", value=str(_def.get('lenso_av_lej_od','')))
                                        eh_av_cer_sc_od = eav3.text_input("Cerca OD S/C", value=str(_def.get('lenso_av_cer_od','')))
                                        eh_av_lej_sc_oi = eav2.text_input("Lejos OI S/C", value=str(_def.get('lenso_av_lej_oi','')))
                                        eh_av_cer_sc_oi = eav3.text_input("Cerca OI S/C", value=str(_def.get('lenso_av_cer_oi','')))
                                        eav4.markdown("<p style='margin-top:28px;'><b>C/C</b></p>", unsafe_allow_html=True)
                                        eh_rx_av_lej_od = eav5.text_input("Lejos OD C/C", value=str(_def.get('rx_av_lej_od','')))
                                        eh_rx_av_cer_od = eav6.text_input("Cerca OD C/C", value=str(_def.get('rx_av_cer_od','')))
                                        eh_rx_av_lej_oi = eav5.text_input("Lejos OI C/C", value=str(_def.get('rx_av_lej_oi','')))
                                        eh_rx_av_cer_oi = eav6.text_input("Cerca OI C/C", value=str(_def.get('rx_av_cer_oi','')))

                                        # Parse lenso existente
                                        def _p(s, i):
                                            pts = str(s).split("|") if s else []
                                            return pts[i].strip() if i < len(pts) else ""

                                        st.markdown("**(4) Lensometria (Rx en uso)**")
                                        el1,el2,el3,el4,el5 = st.columns([1,2,2,2,2])
                                        el1.write(" "); el2.write("**ESF**"); el3.write("**CYL**"); el4.write("**EJE**"); el5.write("**ADD**")
                                        el1.write("**OD**")
                                        elo2 = el2.text_input("LE o1e", label_visibility="collapsed", value=_p(_def.get('lenso_od'),0), placeholder="Esf")
                                        elo3 = el3.text_input("LC o1e", label_visibility="collapsed", value=_p(_def.get('lenso_od'),1), placeholder="Cyl")
                                        elo4 = el4.text_input("LJ o1e", label_visibility="collapsed", value=_p(_def.get('lenso_od'),2), placeholder="Eje")
                                        elo5 = el5.text_input("LA o1e", label_visibility="collapsed", value=_p(_def.get('lenso_od'),3), placeholder="Add")
                                        el1.write("**OI**")
                                        eli2 = el2.text_input("LE i1e", label_visibility="collapsed", value=_p(_def.get('lenso_oi'),0), placeholder="Esf")
                                        eli3 = el3.text_input("LC i1e", label_visibility="collapsed", value=_p(_def.get('lenso_oi'),1), placeholder="Cyl")
                                        eli4 = el4.text_input("LJ i1e", label_visibility="collapsed", value=_p(_def.get('lenso_oi'),2), placeholder="Eje")
                                        eli5 = el5.text_input("LA i1e", label_visibility="collapsed", value=_p(_def.get('lenso_oi'),3), placeholder="Add")

                                        st.markdown("**(5) Refraccion (Rx actual)**")
                                        er1,er2,er3,er4,er5,er6,er7,er8,er9 = st.columns([1,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5])
                                        er1.write(" "); er2.write("**ESF**"); er3.write("**CYL**"); er4.write("**EJE**"); er5.write("**ADD**")
                                        er6.write("**DNP**"); er7.write("**ALT**"); er8.write("**DP**"); er9.write("**A/V**")
                                        er1.write("**OD**")
                                        ero2 = er2.text_input("RE o1e", label_visibility="collapsed", value=_p(_def.get('rx_od'),0), placeholder="Esf")
                                        ero3 = er3.text_input("RC o1e", label_visibility="collapsed", value=_p(_def.get('rx_od'),1), placeholder="Cyl")
                                        ero4 = er4.text_input("RJ o1e", label_visibility="collapsed", value=_p(_def.get('rx_od'),2), placeholder="Eje")
                                        ero5 = er5.text_input("RA o1e", label_visibility="collapsed", value=_p(_def.get('rx_od'),3), placeholder="Add")
                                        ero6 = er6.text_input("RDP o1e", label_visibility="collapsed", value=_p(_def.get('rx_od'),4), placeholder="DNP")
                                        ero7 = er7.text_input("RAL o1e", label_visibility="collapsed", value=_p(_def.get('rx_od'),5), placeholder="Alt")
                                        ero8 = er8.text_input("RDp1e", label_visibility="collapsed", value=_p(_def.get('rx_od'),6), placeholder="DP")
                                        ero9 = er9.text_input("RAV o1e", label_visibility="collapsed", value=_p(_def.get('rx_od'),7), placeholder="A/V")
                                        er1.write("**OI**")
                                        eri2 = er2.text_input("RE i1e", label_visibility="collapsed", value=_p(_def.get('rx_oi'),0), placeholder="Esf")
                                        eri3 = er3.text_input("RC i1e", label_visibility="collapsed", value=_p(_def.get('rx_oi'),1), placeholder="Cyl")
                                        eri4 = er4.text_input("RJ i1e", label_visibility="collapsed", value=_p(_def.get('rx_oi'),2), placeholder="Eje")
                                        eri5 = er5.text_input("RA i1e", label_visibility="collapsed", value=_p(_def.get('rx_oi'),3), placeholder="Add")
                                        eri6 = er6.text_input("RDP i1e", label_visibility="collapsed", value=_p(_def.get('rx_oi'),4), placeholder="DNP")
                                        eri7 = er7.text_input("RAL i1e", label_visibility="collapsed", value=_p(_def.get('rx_oi'),5), placeholder="Alt")
                                        eri8 = er8.text_input("RDp2e", label_visibility="collapsed", value=_p(_def.get('rx_oi'),6), placeholder="DP")
                                        eri9 = er9.text_input("RAV i1e", label_visibility="collapsed", value=_p(_def.get('rx_oi'),7), placeholder="A/V")

                                        st.markdown("**(6) Diagnostico**")
                                        CIE10_OPCIONES_E = [
                                            "H52.1 Miopia", "H52.0 Hipermetropia", "H52.2 Astigmatismo",
                                            "H52.3 Anisometropia", "H52.4 Presbicia", "H52.6 Otros defectos refractivos",
                                            "H40.0 Hipertension ocular", "H40.1 Glaucoma primario angulo abierto",
                                            "H40.2 Glaucoma primario angulo cerrado",
                                            "H26.9 Catarata", "H26.0 Catarata infantil", "H26.1 Catarata traumatica",
                                            "H35.3 Degeneracion macular", "H35.0 Retinopatia de fondo",
                                            "H50.0 Estrabismo convergente", "H50.1 Estrabismo divergente",
                                            "H50.4 Heteroforia", "H55.0 Nistagmo",
                                            "H04.1 Ojo seco (Sindrome de ojo seco)", "H04.0 Dacrioadenitis",
                                            "H10.9 Conjuntivitis", "H10.1 Conjuntivitis atopica",
                                            "H16.9 Queratitis", "H16.0 Ulcera corneal", "H18.0 Pigmentacion corneal",
                                            "H57.1 Dolor ocular", "H57.0 Anomalias pupilares",
                                            "H02.4 Ptosis palpebral", "H02.0 Entropion",
                                            "H25.0 Catarata senil incipiente", "H25.9 Catarata senil",
                                            "H33.0 Desprendimiento de retina", "H34.0 Oclusion arteria retiniana",
                                            "H30.9 Coriorretinitis", "H20.0 Iridociclitis",
                                            "Z01.0 Examen visual de rutina", "Z96.1 Lentes intraoculares",
                                        ]
                                        curr_diag = str(_def.get('diagnostico',''))
                                        _presel = [c for c in CIE10_OPCIONES_E if c in curr_diag]
                                        _curr_libre = curr_diag
                                        for _c in _presel:
                                            _curr_libre = _curr_libre.replace(_c, "").replace("|", "").strip()
                                        
                                        eh_diag_cie_multi = st.multiselect(
                                            "Buscador CIE-10 (Busca y selecciona para agregar)",
                                            options=CIE10_OPCIONES_E,
                                            default=_presel,
                                            key=f"cie_e_in_{h_id}"
                                        )
                                        eh_diag_libre = st.text_input("Detalle adicional", value=_curr_libre, key=f"dl_e_{h_id}")

                                        ed1, ed2, ed3 = st.columns(3)
                                        lentes_opts = ["SI","NO"]
                                        lentes_curr = str(_def.get('necesita_lentes','NO'))
                                        lentes_idx  = 0 if lentes_curr == "SI" else 1
                                        eh_necesita_lentes = ed1.radio("Necesita lentes", lentes_opts, index=lentes_idx, horizontal=True, key=f"nl_e_{h_id}")
                                        color_opts = ["Normal", "Se detecta daltonismo"]
                                        color_curr = str(_def.get('test_color','Normal'))
                                        color_idx = 1 if "dalton" in color_curr.lower() else 0
                                        eh_test_color = ed2.radio("Test de Color", color_opts, index=color_idx, horizontal=True, key=f"tc_e_{h_id}")
                                        def _safe_meses(v, default=12):
                                            try:
                                                return max(1, min(36, int(float(str(v)))))
                                            except Exception:
                                                return default
                                        # Proximo control como fecha
                                        from datetime import timedelta as _td2
                                        _curr_ctrl = str(_def.get('meses_proximo_control', ''))
                                        try:
                                            _ctrl_date = date.fromisoformat(_curr_ctrl[:10])
                                        except Exception:
                                            _meses_n = _safe_meses(_curr_ctrl)
                                            _ctrl_date = date.today() + _td2(days=_meses_n * 30)
                                        eh_proximo_control = ed3.date_input("Proximo control", value=_ctrl_date, key=f"pc_e_{h_id}")

                                        eh_obs = st.text_area("Observaciones / Recomendaciones", value=str(_def.get('observaciones','')), key=f"obs_e_{h_id}")
                                        eh_recom = st.text_area("Recomendaciones (Indicaciones al paciente)", value=str(_def.get('recomendaciones','')), key=f"rec_e_{h_id}")

                                        if st.form_submit_button("Guardar Cambios", type="primary", use_container_width=True):
                                            eh_diag = " | ".join(eh_diag_cie_multi)
                                            if eh_diag_libre.strip():
                                                eh_diag = (eh_diag + " " + eh_diag_libre.strip()).strip()

                                            idx_h = st.session_state.df_historias[
                                                st.session_state.df_historias["id"].astype(str) == str(h_id)
                                            ].index
                                            if len(idx_h) > 0:
                                                i = idx_h[0]
                                                updates = {
                                                    "fecha": eh_fecha.strftime("%Y-%m-%d"),
                                                    "motivo": eh_motivo,
                                                    "ant_personales": eh_ant_per, "ant_familiares": eh_ant_fam,
                                                    "lenso_av_lej_od": eh_av_lej_sc_od, "lenso_av_cer_od": eh_av_cer_sc_od,
                                                    "lenso_av_lej_oi": eh_av_lej_sc_oi, "lenso_av_cer_oi": eh_av_cer_sc_oi,
                                                    "rx_av_lej_od": eh_rx_av_lej_od, "rx_av_cer_od": eh_rx_av_cer_od,
                                                    "rx_av_lej_oi": eh_rx_av_lej_oi, "rx_av_cer_oi": eh_rx_av_cer_oi,
                                                    "lenso_od": f"{elo2}|{elo3}|{elo4}|{elo5}",
                                                    "lenso_oi": f"{eli2}|{eli3}|{eli4}|{eli5}",
                                                    "rx_od": f"{ero2}|{ero3}|{ero4}|{ero5}|{ero6}|{ero7}|{ero8}|{ero9}",
                                                    "rx_oi": f"{eri2}|{eri3}|{eri4}|{eri5}|{eri6}|{eri7}|{eri8}|{eri9}",
                                                    "diagnostico": eh_diag,
                                                    "necesita_lentes": eh_necesita_lentes,
                                                    "test_color": eh_test_color,
                                                    "meses_proximo_control": eh_proximo_control.strftime("%Y-%m-%d"),
                                                    "observaciones": eh_obs,
                                                    "recomendaciones": eh_recom,
                                                }
                                                for campo, val in updates.items():
                                                    st.session_state.df_historias.at[i, campo] = val
                                                from database import actualizar_historia
                                                actualizar_historia(h_id, updates)
                                                st.session_state[f"editando_historia_{h_id}"] = False
                                                st.success("Historia actualizada.")
                                                st.rerun()


                                st.markdown("**💡 Recomendaciones / Lo que se llevó el paciente:**")
                                rec_val     = hrow.get("recomendaciones", "")
                                rec_editado = st.text_area("Recomendaciones", value=str(rec_val) if rec_val else "",
                                    key=f"rec_{hrow['id']}", label_visibility="collapsed", height=80)
                                if st.button("💾 Guardar recomendación", key=f"save_rec_{hrow['id']}"):
                                    idx_h = st.session_state.df_historias[
                                        st.session_state.df_historias["id"] == hrow["id"]
                                    ].index[0]
                                    st.session_state.df_historias.at[idx_h, "recomendaciones"] = rec_editado
                                    from database import actualizar_historia
                                    actualizar_historia(hrow["id"], {"recomendaciones": rec_editado})
                                    st.toast("✅ Recomendación guardada en la nube.")
                                    st.rerun()

                                st.markdown("---")
                                from database import guardar_orden_trabajo, cargar_inventario
                                bacc1, bacc2, bacc3 = st.columns(3)

                                # Generar PDF para botones — usar el optometrista que atendió originalmente
                                try:
                                    import base64 as _b64
                                    
                                    _opto_login_hist = hrow.get("optometrista_login", "") or st.session_state.get("user_login", "")
                                    
                                    _ud_supabase = {}
                                    try:
                                        from database import supabase as _supa
                                        if _supa and _opto_login_hist:
                                            _res = _supa.table("usuarios").select("*").eq("username", _opto_login_hist).execute()
                                            if _res.data:
                                                _ud_supabase = _res.data[0]
                                                if _opto_login_hist == st.session_state.get("user_login", "") and _ud_supabase.get("firma_base64"):
                                                    st.session_state["user_firma"] = _ud_supabase["firma_base64"]
                                    except Exception: pass

                                    _opto_nombre_hist = hrow.get("optometrista", "") or st.session_state.get("user_name", "")

                                    opto_info = {
                                        "username":     _opto_login_hist,
                                        "nombre":       _ud_supabase.get("nombre")   or _opto_nombre_hist,
                                        "cargo":        _ud_supabase.get("cargo")    or st.session_state.get("user_cargo", "Optometrista"),
                                        "registro":     _ud_supabase.get("registro") or st.session_state.get("user_registro", ""),
                                        "telefono":     _ud_supabase.get("telefono") or st.session_state.get("user_telefono", ""),
                                        "firma_base64": _ud_supabase.get("firma_base64") or st.session_state.get("user_firma", "")
                                    }
                                    
                                    pdf_bytes = generar_pdf_historia(hrow.to_dict(), pac.to_dict(), opto_info)
                                    
                                    # Definir tel_pac una sola vez para todos los botones
                                    import urllib.parse
                                    def _normalizar_tel(tel_raw):
                                        """Convierte el número al formato internacional para WhatsApp (Ecuador)."""
                                        t = str(tel_raw).strip().replace(" ", "").replace("-", "").replace("+", "")
                                        if t.startswith("0"):      # 0987654321 → 593987654321
                                            t = "593" + t[1:]
                                        elif not t.startswith("593"):  # Sin código de país, añadir Ecuador
                                            t = "593" + t
                                        return t
                                    
                                    tel_pac = _normalizar_tel(pac.get("telefono", ""))
                                    nombre_pac = pac.get('nombre', '')
                                    
                                    def _log_pdf_descarga():
                                        from database import registrar_auditoria
                                        registrar_auditoria(
                                            accion="Descargar PDF",
                                            entidad="Certificado Visual",
                                            detalle=f"Paciente: {nombre_pac} | Historia ID: {hrow['id']}",
                                            usuario=st.session_state.get("user_login", ""),
                                            nombre_usuario=st.session_state.get("user_name", ""),
                                            sucursal=st.session_state.get("sucursal_activa", "")
                                        )

                                    with bacc1:
                                        st.download_button(
                                            label="📥 Descargar Certificado (PDF)",
                                            data=pdf_bytes,
                                            file_name=f"Certificado_{nombre_pac.replace(' ','_')}.pdf",
                                            mime="application/pdf",
                                            use_container_width=True,
                                            key=f"pdf_dl_main_{hrow['id']}",
                                            on_click=_log_pdf_descarga
                                        )

                                    with bacc2:
                                        with st.expander("👁️ Vista Previa"):
                                            _b64str = _b64.b64encode(pdf_bytes).decode("utf-8")
                                            st.markdown(
                                                f'<iframe src="data:application/pdf;base64,{_b64str}" '
                                                f'width="100%" height="500px" style="border:none;"></iframe>',
                                                unsafe_allow_html=True
                                            )
                                        
                                        # Botón WhatsApp para adjuntar y enviar el certificado PDF
                                        if tel_pac:
                                            fecha_hc = hrow.get('fecha', '')
                                            msg_pdf = (
                                                f"👁️ *Happy Vision — Certificado Visual*\n\n"
                                                f"Estimado/a *{nombre_pac}*, esperamos que su consulta del *{fecha_hc}* haya sido de su completa satisfacción.\n\n"
                                                f"Adjunto encontrará su *Certificado Visual* con el resumen de su evaluación optométrica. Le recomendamos guardarlo para sus registros personales.\n\n"
                                                f"Recuerde seguir las indicaciones de su optometrista y programar su próximo control a tiempo. Cuidar su visión es cuidar su calidad de vida. 💙\n\n"
                                                f"Ante cualquier consulta, estamos a su disposición.\n"
                                                f"📍 *Happy Vision* | 📞 +593 96 324 1158"
                                            )
                                            wa_pdf_url = f"https://wa.me/{tel_pac}?text={urllib.parse.quote(msg_pdf)}"
                                            if st.button("📲 WhatsApp (Certificado)", key=f"btn_wa_pdf_{hrow['id']}", use_container_width=True):
                                                from database import registrar_auditoria
                                                registrar_auditoria(
                                                    accion="Enviar WhatsApp",
                                                    entidad="Certificado PDF",
                                                    detalle=f"Paciente: {nombre_pac} | Tel: {tel_pac}",
                                                    usuario=st.session_state.get("user_login", ""),
                                                    nombre_usuario=st.session_state.get("user_name", ""),
                                                    sucursal=st.session_state.get("sucursal_activa", "")
                                                )
                                                st.markdown(f'<a href="{wa_pdf_url}" target="_blank" id="wa_link_{hrow["id"]}"><script>document.getElementById("wa_link_{hrow["id"]}").click();</script></a>', unsafe_allow_html=True)
                                                st.info(f"👉 [Click aquí para abrir WhatsApp]({wa_pdf_url})")
                                        else:
                                            st.caption("⚠️ Sin teléfono")

                                    with bacc3:
                                        with st.popover("💊 Enviar Indicacion", use_container_width=True):
                                            st.markdown("<p style='font-size:14px; font-weight:700; margin-bottom:2px;'>📋 Indicaciones para el Paciente</p>", unsafe_allow_html=True)
                                            st.caption("Selecciona una plantilla, edítala y envía.")
                                            
                                            wa_key = f"wa_msg_val_{hrow['id']}"
                                            # Inicializar solo si no existe (primera vez)
                                            if wa_key not in st.session_state:
                                                st.session_state[wa_key] = hrow.get("recomendaciones", "") or ""

                                            # Botones con plantillas editables
                                            c_s1, c_s2 = st.columns(2)
                                            if c_s1.button("👓 Lentes", key=f"btn_s1_{hrow['id']}", use_container_width=True):
                                                st.session_state[wa_key] = "✅ Uso permanente de lentes correctivos para todas sus actividades diarias (lectura, pantallas y distancia)."
                                                st.rerun()
                                            if c_s2.button("💧 Gotas", key=f"btn_s2_{hrow['id']}", use_container_width=True):
                                                st.session_state[wa_key] = "💧 Lubricante ocular: Aplicar 1 gota de [NOMBRE DEL MEDICAMENTO] en cada ojo cada 4 horas. No suspender sin indicación médica."
                                                st.rerun()
                                            
                                            c_s3, c_s4 = st.columns(2)
                                            if c_s3.button("🖥️ 20-20", key=f"btn_s3_{hrow['id']}", use_container_width=True):
                                                st.session_state[wa_key] = "🖥️ Higiene visual: Por cada 20 minutos frente a pantallas, enfoque un objeto a 6 metros de distancia durante 20 segundos. Parpadee conscientemente para lubricar sus ojos."
                                                st.rerun()
                                            if c_s4.button("📅 6 meses", key=f"btn_s4_{hrow['id']}", use_container_width=True):
                                                st.session_state[wa_key] = "📅 Control visual programado en 6 meses. Es importante cumplir este seguimiento para monitorear la evolución de su salud visual."
                                                st.rerun()

                                            # SIN value= para que Streamlit use el session_state del key directamente
                                            indicacion_editada = st.text_area(
                                                "✏️ Edita el mensaje antes de enviar:",
                                                key=wa_key,
                                                height=140,
                                                placeholder="Selecciona una plantilla arriba o escribe aquí..."
                                            )
                                            
                                            if tel_pac:
                                                fecha_hc = hrow.get('fecha', '')
                                                indicacion_editada = st.session_state.get(wa_key, "")
                                                full_wa_msg = (
                                                    f"👁️ *Happy Vision — Indicaciones Médicas*\n\n"
                                                    f"Estimado/a *{nombre_pac}*, a continuación las indicaciones de su consulta del *{fecha_hc}*:\n\n"
                                                    f"{indicacion_editada}\n\n"
                                                    f"Ante cualquier duda o molestia, comuníquese con nosotros.\n"
                                                    f"📍 *Happy Vision* | 📞 +593 96 324 1158"
                                                )
                                                wa_url = f"https://wa.me/{tel_pac}?text={urllib.parse.quote(full_wa_msg)}"
                                                if st.button("📲 Enviar por WhatsApp", key=f"btn_wa_ind_{hrow['id']}", use_container_width=True, type="primary"):
                                                    from database import registrar_auditoria
                                                    registrar_auditoria(
                                                        accion="Enviar WhatsApp",
                                                        entidad="Indicaciones Médicas",
                                                        detalle=f"Paciente: {nombre_pac} | Tel: {tel_pac}",
                                                        usuario=st.session_state.get("user_login", ""),
                                                        nombre_usuario=st.session_state.get("user_name", ""),
                                                        sucursal=st.session_state.get("sucursal_activa", "")
                                                    )
                                                    st.markdown(f'<a href="{wa_url}" target="_blank" id="wa_ind_link_{hrow["id"]}"><script>document.getElementById("wa_ind_link_{hrow["id"]}").click();</script></a>', unsafe_allow_html=True)
                                                    st.info(f"👉 [Click aquí para abrir WhatsApp]({wa_url})")
                                            else:
                                                st.caption("⚠️ Sin teléfono registrado")
                                    
                                # El bloque bacc4 (Crear Orden Lab) ha sido eliminado por solicitud del usuario.

                                except Exception as e:
                                    st.error(f"⚠️ Error generando PDF: {e}")

    elif not q:
        if len(df_p_all) == 0:
            st.info("No hay pacientes registrados. Usa ➕ Nuevo Paciente para agregar el primero.")
        else:
            st.markdown(
                f"<p style='color:#475569; font-size:13px; margin:0 0 12px 0;'>📋 <b>{len(df_p_all)}</b> paciente(s) registrado(s) en esta sucursal — ordenados alfabéticamente</p>",
                unsafe_allow_html=True
            )
            # Orden alfabético por apellidos
            if "apellidos" in df_p_all.columns:
                df_ord = df_p_all.sort_values(
                    by=["apellidos", "nombres"], key=lambda c: c.astype(str).str.upper().str.strip(), ascending=True
                )
            else:
                df_ord = df_p_all.sort_values(
                    by="nombre", key=lambda c: c.astype(str).str.upper().str.strip(), ascending=True
                )

            for _, rp in df_ord.iterrows():
                n_hist = len(st.session_state.df_historias[
                    st.session_state.df_historias["paciente_id"].astype(str) == str(rp["id"])
                ])

                _apellidos = str(rp.get("apellidos", "")).strip()
                _nombres   = str(rp.get("nombres", "")).strip()
                display_name = f"{_apellidos} {_nombres}" if _apellidos and _nombres else str(rp.get("nombre", ""))

                col_num, col_a, col_b, col_c, col_d, col_e, col_f = st.columns([0.5, 3.2, 1.8, 1.5, 1.4, 1.4, 0.6])

                col_num.markdown(
                    f"<div style='text-align:center; padding-top:6px;'>"
                    f"<span style='color:#93c5fd;font-size:22px;font-weight:800;line-height:1;'>{rp.get('id','')}</span></div>",
                    unsafe_allow_html=True
                )
                col_a.markdown(
                    f"**{display_name}**  \n"
                    f"<span style='font-size:12px;color:#64748b;'>"
                    f"🆔 Cédula: {rp.get('identificacion','')} &nbsp;·&nbsp; "
                    f"{rp.get('genero','')} &nbsp;·&nbsp; {rp.get('edad','')} años"
                    f"</span>",
                    unsafe_allow_html=True
                )
                col_b.caption(f"📞 {rp.get('telefono','')}")
                col_c.caption(f"📋 Historias: {n_hist}")
                if col_d.button("🔍 Ver", key=f"rap_cons_{rp['id']}", use_container_width=True):
                    st.session_state["clinica_buscar"] = rp.get("nombre","")
                    st.rerun()
                if col_e.button("✏️ Editar", key=f"rap_edit_{rp['id']}", use_container_width=True):
                    st.session_state["editar_paciente_id"] = rp["id"]
                    st.session_state["clinica_buscar"] = rp.get("nombre","")
                    st.rerun()
                # SOLO EL ADMIN PUEDE ELIMINAR PACIENTES
                if st.session_state.get("user_role") == "Administrador":
                    if col_f.button("🗑️", key=f"rap_del_{rp['id']}", use_container_width=True, help="Eliminar paciente"):
                        if n_hist > 0:
                            st.error(f"❌ No puedes eliminar a **{display_name}** porque tiene {n_hist} historia(s) clínica(s). Elimínalas primero.")
                        else:
                            from database import eliminar_paciente, registrar_auditoria
                            eliminar_paciente(rp["id"])
                            registrar_auditoria(
                                accion="Eliminar Paciente",
                                entidad="Paciente",
                                detalle=f"Paciente: {display_name} | Cédula: {rp.get('identificacion','')} | ID: {rp['id']}",
                                usuario=st.session_state.get("user_login", ""),
                                nombre_usuario=st.session_state.get("user_name", ""),
                                sucursal=st.session_state.get("sucursal_activa", "")
                            )
                            st.session_state.df_pacientes = st.session_state.df_pacientes[
                                st.session_state.df_pacientes["id"] != rp["id"]
                            ]
                            st.success(f"✅ Paciente **{display_name}** eliminado.")
                            st.rerun()
                st.divider()

    # ── FORMULARIO DE NUEVA CONSULTA ─────────────────────────────────
    if st.session_state.get("nueva_consulta_paciente"):
        c_pac_sel = st.session_state["nueva_consulta_paciente"]
        st.markdown(f"<div class='section-title'>Nueva Consulta para: <b>{c_pac_sel}</b></div>", unsafe_allow_html=True)

        with st.form("nueva_consulta_form", clear_on_submit=True):
            col_c1, col_c2 = st.columns(2)
            c_fecha = col_c1.date_input("📅 Fecha", value=date.today())
            col_c2.markdown(f"<p style='margin-top:28px; color:#93c5fd;'>Paciente: <b>{c_pac_sel}</b></p>", unsafe_allow_html=True)

            st.markdown("**(1) Datos de la Consulta**")
            c_motivo = st.text_input("Motivo de la consulta")

            st.markdown("**(2) Antecedentes**")
            ant_col1, ant_col2 = st.columns(2)
            c_ant_per = ant_col1.text_input("Antecedentes Personales", placeholder="Ej: Diabetes, cirugias...")
            c_ant_fam = ant_col2.text_input("Antecedentes Familiares", placeholder="Ej: Glaucoma familiar...")

            st.markdown("**(2) Agudezas Visuales**")
            ac1, ac2, ac3, ac4, ac5, ac6 = st.columns([1,2,2,1,2,2])
            ac1.markdown("<p style='margin-top:30px;'><b>S/C</b></p>", unsafe_allow_html=True)
            c_av_lej_sc_od = ac2.text_input("Lejos OD (S/C)")
            c_av_cer_sc_od = ac3.text_input("Cerca OD (S/C)")
            c_av_lej_sc_oi = ac2.text_input("Lejos OI (S/C)")
            c_av_cer_sc_oi = ac3.text_input("Cerca OI (S/C)")
            ac4.markdown("<p style='margin-top:30px;'><b>C/C</b></p>", unsafe_allow_html=True)
            c_rx_av_lej_od = ac5.text_input("Lejos OD (C/C)")
            c_rx_av_cer_od = ac6.text_input("Cerca OD (C/C)")
            c_rx_av_lej_oi = ac5.text_input("Lejos OI (C/C)")
            c_rx_av_cer_oi = ac6.text_input("Cerca OI (C/C)")

            st.markdown("**(3) LENSOMETRÍA (RX EN USO)**")
            lc1, lc2, lc3, lc4, lc5, lc6 = st.columns([1,2,2,2,2,2])
            lc1.write(" "); lc2.write("**ESF**"); lc3.write("**CYL**"); lc4.write("**EJE**"); lc5.write("**ADD**"); lc6.write(" ")
            lc1.write("**OD**")
            lo2 = lc2.text_input("LE o1", label_visibility="collapsed", placeholder="Esf")
            lo3 = lc3.text_input("LC o1", label_visibility="collapsed", placeholder="Cyl")
            lo4 = lc4.text_input("LJ o1", label_visibility="collapsed", placeholder="Eje")
            lo5 = lc5.text_input("LA o1", label_visibility="collapsed", placeholder="Add")
            lc6.write(" ")
            lc1.write("**OI**")
            li2 = lc2.text_input("LE i1", label_visibility="collapsed", placeholder="Esf")
            li3 = lc3.text_input("LC i1", label_visibility="collapsed", placeholder="Cyl")
            li4 = lc4.text_input("LJ i1", label_visibility="collapsed", placeholder="Eje")
            li5 = lc5.text_input("LA i1", label_visibility="collapsed", placeholder="Add")
            lc6.write(" ")
            c_lenso_od = f"{lo2}|{lo3}|{lo4}|{lo5}"
            c_lenso_oi = f"{li2}|{li3}|{li4}|{li5}"

            st.markdown("**(4) REFRACCIÓN (RX ACTUAL)**")
            rc1, rc2, rc3, rc4, rc5, rc6, rc7, rc8, rc9, rc10 = st.columns([1,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5])
            rc1.write(" "); rc2.write("**ESF**"); rc3.write("**CYL**"); rc4.write("**EJE**"); rc5.write("**ADD**")
            rc6.write("**DNP**"); rc7.write("**ALT**"); rc8.write("**DP**"); rc9.write("**A/V**"); rc10.write(" ")
            rc1.write("**OD**")
            ro2 = rc2.text_input("RE o1", label_visibility="collapsed", placeholder="Esf")
            ro3 = rc3.text_input("RC o1", label_visibility="collapsed", placeholder="Cyl")
            ro4 = rc4.text_input("RJ o1", label_visibility="collapsed", placeholder="Eje")
            ro5 = rc5.text_input("RA o1", label_visibility="collapsed", placeholder="Add")
            ro7 = rc6.text_input("RDP o1", label_visibility="collapsed", placeholder="DNP")
            ro8 = rc7.text_input("RAL o1", label_visibility="collapsed", placeholder="Alt")
            ro9 = rc8.text_input("RD p1",  label_visibility="collapsed", placeholder="DP")
            ro10= rc9.text_input("RAV o1", label_visibility="collapsed", placeholder="A/V")
            rc10.write(" ")
            rc1.write("**OI**")
            ri2 = rc2.text_input("RE i1", label_visibility="collapsed", placeholder="Esf")
            ri3 = rc3.text_input("RC i1", label_visibility="collapsed", placeholder="Cyl")
            ri4 = rc4.text_input("RJ i1", label_visibility="collapsed", placeholder="Eje")
            ri5 = rc5.text_input("RA i1", label_visibility="collapsed", placeholder="Add")
            ri7 = rc6.text_input("RDP i1", label_visibility="collapsed", placeholder="DNP")
            ri8 = rc7.text_input("RAL i1", label_visibility="collapsed", placeholder="Alt")
            ri9 = rc8.text_input("RD p2",  label_visibility="collapsed", placeholder="DP")
            ri10= rc9.text_input("RAV i1", label_visibility="collapsed", placeholder="A/V")
            rc10.write(" ")
            c_rx_od = f"{ro2}|{ro3}|{ro4}|{ro5}|{ro7}|{ro8}|{ro9}|{ro10}"
            c_rx_oi = f"{ri2}|{ri3}|{ri4}|{ri5}|{ri7}|{ri8}|{ri9}|{ri10}"

            st.markdown("**(5) Diagnóstico y Observaciones**")

            def _sugerir_cie10(esf_od, esf_oi, cyl_od, cyl_oi, add_od):
                sugs = []
                def _n(v):
                    try: return float(str(v).replace(",","."))
                    except: return 0.0
                if _n(esf_od) < -0.25 or _n(esf_oi) < -0.25: sugs.append("H52.1 Miopia")
                if _n(esf_od) > 0.25 or _n(esf_oi) > 0.25: sugs.append("H52.0 Hipermetropia")
                if abs(_n(cyl_od)) > 0.25 or abs(_n(cyl_oi)) > 0.25: sugs.append("H52.2 Astigmatismo")
                if _n(add_od) > 0.5: sugs.append("H52.4 Presbicia")
                if abs(_n(esf_od) - _n(esf_oi)) > 1.0: sugs.append("H52.3 Anisometropia")
                return sugs
            
            sugeridos = _sugerir_cie10(ro2, ri2, ro3, ri3, ro5)
            if sugeridos:
                st.caption(f"💡 Sugerencias por Rx: {', '.join(sugeridos)}")

            CIE10_OPCIONES = [
                "H52.1 Miopia", "H52.0 Hipermetropia", "H52.2 Astigmatismo",
                "H52.3 Anisometropia", "H52.4 Presbicia", "H52.6 Otros defectos refractivos",
                "H40.0 Hipertension ocular", "H40.1 Glaucoma primario angulo abierto",
                "H40.2 Glaucoma primario angulo cerrado",
                "H26.9 Catarata", "H26.0 Catarata infantil", "H26.1 Catarata traumatica",
                "H35.3 Degeneracion macular", "H35.0 Retinopatia de fondo",
                "H50.0 Estrabismo convergente", "H50.1 Estrabismo divergente",
                "H50.4 Heteroforia", "H55.0 Nistagmo",
                "H04.1 Ojo seco (Sindrome de ojo seco)", "H04.0 Dacrioadenitis",
                "H10.9 Conjuntivitis", "H10.1 Conjuntivitis atopica",
                "H16.9 Queratitis", "H16.0 Ulcera corneal", "H18.0 Pigmentacion corneal",
                "H57.1 Dolor ocular", "H57.0 Anomalias pupilares",
                "H02.4 Ptosis palpebral", "H02.0 Entropion",
                "H25.0 Catarata senil incipiente", "H25.9 Catarata senil",
                "H33.0 Desprendimiento de retina", "H34.0 Oclusion arteria retiniana",
                "H30.9 Coriorretinitis", "H20.0 Iridociclitis",
                "Z01.0 Examen visual de rutina", "Z96.1 Lentes intraoculares",
            ]
            c_diag_cie_multi = st.multiselect(
                "Buscador CIE-10 (Busca y selecciona los codigos a agregar)",
                options=CIE10_OPCIONES,
                placeholder="Escribe o selecciona..."
            )
            c_diag_libre = st.text_input("Detalle adicional / complemento", placeholder="Ej: OU, ambos ojos, bilateral")

            dcol1, dcol2, dcol3 = st.columns(3)
            c_necesita_lentes  = dcol1.radio("Paciente necesita lentes", ["SI", "NO"], horizontal=True)
            c_test_color       = dcol2.radio("Test de Color", ["Normal", "Se detecta daltonismo"], horizontal=True)
            from datetime import timedelta as _td
            c_proximo_control  = dcol3.date_input("Proximo control", value=date.today() + _td(days=365))

            c_obs = st.text_area("Observaciones / Recomendaciones (Opcional)", placeholder="Escribe observaciones adicionales...")
            # Campos internos sin UI (valores por defecto para campos legacy)
            c_diab, c_hiper, c_otra = "NO", "NO", ""
            c_est_mus, c_seg_ext, c_test_col, c_est_ref, c_disp, c_recom = "", "", "", "", "", ""

            fcols = st.columns([2, 1])
            if fcols[0].form_submit_button("💾 Guardar Historia Clínica", type="primary", use_container_width=True):
                c_diag = " | ".join(c_diag_cie_multi)
                if c_diag_libre.strip():
                    c_diag = (c_diag + " " + c_diag_libre.strip()).strip()

                p_match = st.session_state.df_pacientes[st.session_state.df_pacientes["nombre"] == c_pac_sel]
                if len(p_match) > 0:
                    p_id_match = p_match.iloc[0]["id"]
                    # Calcular nuevo ID de historia de forma segura
                    df_h_current = st.session_state.df_historias
                    if not df_h_current.empty and "id" in df_h_current.columns:
                        max_h_id = pd.to_numeric(df_h_current["id"], errors="coerce").max()
                        nueva_h_id = int(max_h_id + 1) if pd.notna(max_h_id) else 1
                    else:
                        nueva_h_id = 1

                    nueva_h = {
                        "id": nueva_h_id,
                        "paciente_id": p_id_match, "paciente_nombre": c_pac_sel,
                        "fecha": c_fecha.strftime("%Y-%m-%d"),
                        "ant_personales": c_ant_per, "ant_familiares": c_ant_fam, "motivo": c_motivo,
                        "diabetes": c_diab, "hipertension": c_hiper, "patologia_otra": c_otra, "observaciones": c_obs,
                        "lenso_od": c_lenso_od, "lenso_av_lej_od": c_av_lej_sc_od, "lenso_av_cer_od": c_av_cer_sc_od,
                        "lenso_oi": c_lenso_oi, "lenso_av_lej_oi": c_av_lej_sc_oi, "lenso_av_cer_oi": c_av_cer_sc_oi,
                        "rx_od": c_rx_od, "rx_av_lej_od": c_rx_av_lej_od, "rx_av_cer_od": c_rx_av_cer_od,
                        "rx_oi": c_rx_oi, "rx_av_lej_oi": c_rx_av_lej_oi, "rx_av_cer_oi": c_rx_av_cer_oi,
                        "estado_muscular": c_est_mus, "seg_externo": c_seg_ext,
                        "test_colores": c_test_col, "estado_refractivo": c_est_ref,
                        "diagnostico": c_diag,
                        "recomendaciones": c_recom,
                        "necesita_lentes": c_necesita_lentes,
                        "test_color": c_test_color,
                        "meses_proximo_control": c_proximo_control.strftime("%Y-%m-%d"),
                        "sucursal": sucursal_actual,
                        "optometrista": st.session_state.get("user_name", ""),
                        "optometrista_login": st.session_state.get("user_login", ""),
                    }
                    st.session_state.df_historias = pd.concat(
                        [st.session_state.df_historias, pd.DataFrame([nueva_h])], ignore_index=True
                    )
                    from database import guardar_historia
                    guardar_historia(nueva_h)
                    # AUDITORÍA: Nueva Historia
                    from database import registrar_auditoria
                    registrar_auditoria(
                        accion="Crear Historia Clínica",
                        entidad="Historia Clínica",
                        detalle=f"Paciente: {c_pac_sel} | ID Historia: {nueva_h_id} | Fecha: {nueva_h['fecha']}",
                        usuario=st.session_state.get("user_login", ""),
                        nombre_usuario=st.session_state.get("user_name", ""),
                        sucursal=sucursal_actual
                    )
                    st.session_state["nueva_consulta_paciente"] = None
                    st.success(f"Consulta guardada para {c_pac_sel}")
                    st.rerun()
            if fcols[1].form_submit_button("❌ Cancelar", use_container_width=True):
                st.session_state["nueva_consulta_paciente"] = None
                st.rerun()

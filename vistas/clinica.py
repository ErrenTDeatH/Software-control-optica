import streamlit as st
import pandas as pd
from datetime import date
from utils import wa_link, generar_pdf_historia, generar_msg_indicaciones, generar_pdf_historia_lc, generar_msg_indicaciones_lc, generar_msg_hc_lc
from database import eliminar_historia, actualizar_historia, guardar_historia_lc, actualizar_historia_lc, eliminar_historia_lc


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
    .hc-card { background:#fdf6ee; border:1px solid #e8d5b7; border-radius:12px; padding:16px 20px; margin-bottom:12px; }
    .hc-card-blue { background:linear-gradient(135deg,#fdf6ee,#f5e6cc); border:1px solid #d4a96a; border-radius:12px; padding:16px 20px; margin-bottom:12px; }
    .hc-card-green { background:linear-gradient(135deg,#faf5eb,#f0e8d0); border:1px solid #c9a96e; border-radius:12px; padding:16px 20px; margin-bottom:12px; }
    .hc-card-amber { background:linear-gradient(135deg,#fefce8,#fef9c3); border:1px solid #d4a017; border-radius:12px; padding:16px 20px; margin-bottom:12px; }
    .hc-section-title { font-size:13px; font-weight:700; color:#7c5c2e; text-transform:uppercase; letter-spacing:.06em; margin-bottom:10px; }
    .hc-label { font-size:11px; color:#a0856a; font-weight:600; text-transform:uppercase; letter-spacing:.05em; margin-bottom:2px; }
    .hc-value { font-size:15px; color:#3b2a1a; font-weight:600; margin-bottom:0; }
    .hc-value-mono { font-family:monospace; font-size:14px; color:#7c3f00; font-weight:700; }
    .hc2-header {
        background: linear-gradient(135deg,#2c1a0e,#7c3f00);
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
        background:#7c3f00; color:white; font-weight:700; font-size:11px;
        text-transform:uppercase; letter-spacing:.05em;
        padding:7px 10px; text-align:center;
    }
    .rx-table th.rx-th-eye { background:#2c1a0e; text-align:left; width:110px; }
    .rx-table td {
        padding:8px 10px; text-align:center; font-family:monospace;
        font-size:14px; font-weight:700; border-bottom:1px solid #e8d5b7;
        color:#3b2a1a; background:#fffdf8;
    }
    .rx-table td.rx-eye-label {
        font-family:sans-serif; font-size:11px; font-weight:800;
        color:white; text-align:left; white-space:nowrap;
    }
    .rx-table tr.rx-od td.rx-eye-label { background:#b45309; }
    .rx-table tr.rx-oi td.rx-eye-label { background:#92400e; }
    .rx-table tr:last-child td { border-bottom:none; }
    .rx-table td.rx-dash { color:#d4b896; font-weight:400; }
    .hc2-pill {
        display:inline-flex; align-items:center; gap:5px;
        padding:4px 12px; border-radius:20px; font-size:12px; font-weight:700;
    }
    .hc2-pill-blue   { background:#fef3c7; color:#92400e; }
    .hc2-pill-green  { background:#fdf6ee; color:#7c3f00; border:1px solid #d4a96a; }
    .hc2-pill-red    { background:#fee2e2; color:#dc2626; }
    .hc2-pill-amber  { background:#fef3c7; color:#92400e; }
    .hc2-pill-purple { background:#f5e6cc; color:#7c3f00; }
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
    <div class="hc2-section" style="background:linear-gradient(135deg,#fdf6ee,#f5e6cc);border:1px solid #d4a96a">
        <div class="hc2-section-title" style="color:#7c3f00">🔍 Lensometría &nbsp;·&nbsp; Rx en Uso &nbsp;·&nbsp; Agudeza Visual S/C</div>
        <table class="rx-table">
            <thead>
                <tr>
                    <th class="rx-th-eye">Ojo</th>
                    <th>ESF</th><th>CYL</th><th>EJE</th><th>ADD</th>
                    <th style="border-left:2px solid #b45309">AV Lejos</th>
                    <th>AV Cerca</th>
                </tr>
            </thead>
            <tbody>
                <tr class="rx-od">
                    <td class="rx-eye-label">🟠 OD &nbsp;Derecho</td>
                    {_c(lo_esf)}{_c(lo_cyl)}{_c(lo_eje)}{_c(lo_add)}
                    <td style="border-left:2px solid #b45309" class="{avl_od_cls}">{lo_avl}</td>
                    {_c(lo_avc)}
                </tr>
                <tr class="rx-oi">
                    <td class="rx-eye-label">🟤 OI &nbsp;Izquierdo</td>
                    {_c(li_esf)}{_c(li_cyl)}{_c(li_eje)}{_c(li_add)}
                    <td style="border-left:2px solid #b45309" class="{avl_oi_cls}">{li_avl}</td>
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
    <div class="hc2-section" style="background:linear-gradient(135deg,#faf5eb,#f0e8d0);border:1px solid #c9a96e">
        <div class="hc2-section-title" style="color:#7c3f00">✨ Refracción Final &nbsp;·&nbsp; Rx Actual &nbsp;·&nbsp; Agudeza Visual C/C</div>
        <table class="rx-table">
            <thead>
                <tr>
                    <th class="rx-th-eye">Ojo</th>
                    <th>ESF</th><th>CYL</th><th>EJE</th><th>ADD</th>
                    <th style="border-left:2px solid #92400e">DNP</th>
                    <th>ALT</th><th>DP</th><th>A/V</th>
                    <th style="border-left:2px solid #92400e">AV Lejos</th>
                    <th>AV Cerca</th>
                </tr>
            </thead>
            <tbody>
                <tr class="rx-od">
                    <td class="rx-eye-label">🟠 OD &nbsp;Derecho</td>
                    {_c(ro_esf)}{_c(ro_cyl)}{_c(ro_eje)}{_c(ro_add)}
                    <td style="border-left:2px solid #92400e" class="{ro_dnp_cls}">{ro_dnp}</td>
                    {_c(ro_alt)}{_c(ro_dp)}{_c(ro_av)}
                    <td style="border-left:2px solid #92400e" class="{ro_avl_cls}">{ro_avl}</td>
                    {_c(ro_avc)}
                </tr>
                <tr class="rx-oi">
                    <td class="rx-eye-label">🟤 OI &nbsp;Izquierdo</td>
                    {_c(ri_esf)}{_c(ri_cyl)}{_c(ri_eje)}{_c(ri_add)}
                    <td style="border-left:2px solid #92400e" class="{ri_dnp_cls}">{ri_dnp}</td>
                    {_c(ri_alt)}{_c(ri_dp)}{_c(ri_av)}
                    <td style="border-left:2px solid #92400e" class="{ri_avl_cls}">{ri_avl}</td>
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
    from database import cargar_pacientes, cargar_historias
    st.session_state.df_pacientes = cargar_pacientes()
    st.session_state.df_historias = cargar_historias()

    sucursal_actual = st.session_state.get("sucursal_activa", "Matriz")
    
    if "sucursal" in st.session_state.df_pacientes.columns:
        df_p_all = st.session_state.df_pacientes[st.session_state.df_pacientes["sucursal"] == sucursal_actual].copy()
    else:
        df_p_all = st.session_state.df_pacientes.copy()

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

<<<<<<< HEAD
                    # ── CONTROL ANUAL DE LA VISTA & HISTORIAL DE COMPRAS ──
                    from database import cargar_ventas_historial
                    from datetime import datetime
                    
                    # 1. Alerta de Control Anual (>12 meses)
                    if not hist_pac.empty:
                        try:
                            # Obtener la fecha de la última consulta
                            ultima_fecha_str = str(hist_pac.iloc[0].get("fecha", ""))[:10]
                            ultima_fecha = datetime.strptime(ultima_fecha_str, "%Y-%m-%d").date()
                            hoy = date.today()
                            meses_transcurridos = (hoy.year - ultima_fecha.year) * 12 + hoy.month - ultima_fecha.month
                            if meses_transcurridos >= 12:
                                st.markdown(f'''
                                    <div style="background:#fffbeb; border:1px solid #fef08a; border-left:4px solid #eab308;
                                                border-radius:8px; padding:12px 16px; margin: 10px 0 15px 0;">
                                        <b style="color:#854d0e; font-size:14px;">⚠️ Alerta de Control Anual</b><br>
                                        <span style="color:#a16207; font-size:12px;">
                                            La última consulta de este paciente fue el <b>{ultima_fecha.strftime('%d/%m/%Y')}</b> (hace <b>{meses_transcurridos} meses</b>).
                                            Se sugiere realizar un nuevo examen visual preventivo.
                                        </span>
                                    </div>
                                ''', unsafe_allow_html=True)
                        except Exception as e:
                            print(f"Error parseando fecha control anual: {e}")
                    
                    # 2. Historial de Compras
                    try:
                        df_compras = cargar_ventas_historial(None) # Carga todas las ventas
                        if not df_compras.empty:
                            id_paciente = str(pac.get("identificacion", "")).strip()
                            nom_paciente = str(pac.get("nombre", "")).strip()
                            
                            df_pac_compras = df_compras[
                                (df_compras["identificacion"].astype(str).str.strip() == id_paciente) | 
                                (df_compras["cliente"].astype(str).str.contains(nom_paciente, case=False, na=False))
                            ].copy()
                            
                            if not df_pac_compras.empty:
                                with st.expander(f"🛒 Historial de Compras ({len(df_pac_compras)} comprobantes)", expanded=False):
                                    st.markdown('''
                                        <table style='width:100%; border-collapse:collapse; font-size:12px; margin-top:5px;'>
                                            <tr style='background-color:#f8fafc; border-bottom:1px solid #e2e8f0; font-weight:bold;'>
                                                <td style='padding:6px;'>Fecha</td>
                                                <td style='padding:6px;'>Descripción / Detalles</td>
                                                <td style='padding:6px; text-align:right;'>Total</td>
                                                <td style='padding:6px; text-align:center;'>Método</td>
                                            </tr>
                                    ''', unsafe_allow_html=True)
                                    
                                    for _, row_v in df_pac_compras.iterrows():
                                        fecha_v = str(row_v.get("fecha", ""))[:10]
                                        detalles_v = ""
                                        det_raw = row_v.get("detalles", [])
                                        if isinstance(det_raw, list):
                                            detalles_v = ", ".join([str(d.get("descripcion", "")) for d in det_raw])
                                        else:
                                            detalles_v = str(det_raw)
                                            
                                        st.markdown(f'''
                                            <tr style='border-bottom:1px solid #f1f5f9;'>
                                                <td style='padding:6px; white-space:nowrap;'>📅 {fecha_v}</td>
                                                <td style='padding:6px;'>{detalles_v}</td>
                                                <td style='padding:6px; text-align:right; font-weight:bold;'>${float(row_v.get('total', 0)):.2f}</td>
                                                <td style='padding:6px; text-align:center;'>{row_v.get('metodo_pago', 'Efectivo')}</td>
                                            </tr>
                                        ''', unsafe_allow_html=True)
                                    st.markdown("</table>", unsafe_allow_html=True)
                    except Exception as e:
                        print(f"Error cargando historial de compras: {e}")

=======
>>>>>>> aeff6931d6ef494b1d01c194039daf01d34af7bb
                    ca, cb, cc, cd = st.columns([2, 1.3, 1.3, 1])
                    ca.caption(f"🗂️ {len(hist_pac)} consulta(s)")

                    with cb:
                        if st.button("📋 Nueva Historia Clínica", key=f"new_h_{pac['id']}", use_container_width=True, type="primary"):
                            st.session_state["nueva_consulta_paciente"] = pac["nombre"]
                            st.session_state.pop("nueva_lc_paciente", None)
                            st.rerun()

                    with cc:
                        if st.button("👁️ Historia LC", key=f"new_lc_{pac['id']}", use_container_width=True):
                            st.session_state["nueva_lc_paciente"] = {"nombre": pac["nombre"], "id": pac["id"]}
                            st.session_state.pop("nueva_consulta_paciente", None)
                            st.rerun()

                    with cd:
                        if st.button("✏️ Editar", key=f"edit_p_{pac['id']}", use_container_width=True):
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

                    # Historias normales del paciente
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

                    # ── SECCIÓN: Historias de Lentes de Contacto ─────────────────────────
                    df_lc_all = st.session_state.get("df_historias_lc")
                    if df_lc_all is not None and not df_lc_all.empty:
                        hist_lc_pac = df_lc_all[
                            df_lc_all["paciente_id"].astype(str) == str(pac["id"])
                        ].sort_values("fecha", ascending=False)
                    else:
                        hist_lc_pac = pd.DataFrame()

                    if not hist_lc_pac.empty:
                        st.markdown("""
                        <div style='background:linear-gradient(135deg,#2c1a0e,#7c3f00);border-radius:10px;
                        padding:10px 18px;margin:18px 0 10px 0;color:white;'>
                        <b style='font-size:13px;'>👁️ HISTORIAS CLÍNICAS — LENTES DE CONTACTO</b></div>
                        """, unsafe_allow_html=True)

                        for _, hlc in hist_lc_pac.iterrows():
                            hlc_id = hlc.get("id", "")
                            with st.expander(f"👁️ LC: {hlc.get('fecha','')} — {hlc.get('lc_motivo_consulta','Adaptación de Lentes de Contacto')}"):
                                if not st.session_state.get(f"editando_lc_{hlc_id}", False):
                                    # Header de la historia LC
                                    st.markdown(f"""
                                    <div style='display:flex;justify-content:space-between;align-items:center;
                                    background:#fdf6ee;border:1px solid #d4a96a;border-radius:8px;
                                    padding:10px 16px;margin-bottom:12px;'>
                                        <div>
                                            <span style='font-weight:700;color:#7c3f00;font-size:15px;'>👁️ Historia LC</span>
                                            <span style='color:#b38b5a;font-size:13px;margin-left:12px;'>📅 {hlc.get('fecha','')}</span>
                                        </div>
                                        <div>
                                            <span style='background:#7c3f00;color:white;padding:4px 10px;border-radius:20px;font-size:12px;'>
                                            👨‍⚕️ {hlc.get('optometrista','')}
                                            </span>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)

                                    # Bloque 1 — Anamnesis
                                    if any(hlc.get(k,"") for k in ["lc_usuario_previo","lc_tipo_lente_ant","lc_marca_ant","lc_motivo_consulta"]):
                                        st.markdown("<b style='color:#7c3f00;'>📝 Anamnesis</b>", unsafe_allow_html=True)
                                        lc_b1_1, lc_b1_2, lc_b1_3 = st.columns(3)
                                        lc_b1_1.metric("Usuario Previo LC", hlc.get("lc_usuario_previo","—") or "—")
                                        lc_b1_2.metric("Tipo Lente Anterior", hlc.get("lc_tipo_lente_ant","—") or "—")
                                        lc_b1_3.metric("Motivo Consulta", hlc.get("lc_motivo_consulta","—") or "—")
                                        if hlc.get("lc_marca_ant"): st.caption(f"Marca anterior: {hlc['lc_marca_ant']} | Horas uso: {hlc.get('lc_horas_uso','—')} h/día")

                                    # Bloque 2 — Refracción y Queratometría
                                    if any(hlc.get(k,"") for k in ["lc_rx_od","lc_rx_oi","lc_kera_od","lc_kera_oi"]):
                                        st.markdown("<b style='color:#7c3f00;'>🔬 Refracción y Queratometría</b>", unsafe_allow_html=True)
                                        st.markdown(f"""
                                        <table style='width:100%;border-collapse:collapse;font-size:13px;'>
                                        <thead><tr style='background:#f5e6cc;'>
                                            <th style='padding:6px 10px;text-align:left;color:#7c3f00;'>Ojo</th>
                                            <th style='padding:6px 10px;text-align:left;'>AV S/C</th>
                                            <th style='padding:6px 10px;text-align:left;'>Rx Gafas</th>
                                            <th style='padding:6px 10px;text-align:left;'>Queratometría</th>
                                        </tr></thead>
                                        <tbody>
                                        <tr style='background:#fdf6ee;'>
                                            <td style='padding:6px 10px;font-weight:700;color:#d97706;'>🟠 OD</td>
                                            <td style='padding:6px 10px;'>{hlc.get('lc_avsc_od','—') or '—'}</td>
                                            <td style='padding:6px 10px;'>{hlc.get('lc_rx_od','—') or '—'}</td>
                                            <td style='padding:6px 10px;'>{hlc.get('lc_kera_od','—') or '—'}</td>
                                        </tr>
                                        <tr style='background:#fff9f0;'>
                                            <td style='padding:6px 10px;font-weight:700;color:#92400e;'>🟤 OI</td>
                                            <td style='padding:6px 10px;'>{hlc.get('lc_avsc_oi','—') or '—'}</td>
                                            <td style='padding:6px 10px;'>{hlc.get('lc_rx_oi','—') or '—'}</td>
                                            <td style='padding:6px 10px;'>{hlc.get('lc_kera_oi','—') or '—'}</td>
                                        </tr>
                                        </tbody></table>
                                        """, unsafe_allow_html=True)

                                    # Bloque 3 — Biomicroscopía
                                    if any(hlc.get(k,"") for k in ["lc_parpados","lc_conjuntiva","lc_cornea","lc_but_od"]):
                                        st.markdown("<b style='color:#7c3f00;'>🔬 Biomicroscopía</b>", unsafe_allow_html=True)
                                        bb1,bb2,bb3,bb4 = st.columns(4)
                                        bb1.metric("Párpados", hlc.get("lc_parpados","—") or "—")
                                        bb2.metric("Conjuntiva", hlc.get("lc_conjuntiva","—") or "—")
                                        bb3.metric("Córnea (Fluor.)", hlc.get("lc_cornea","—") or "—")
                                        bb4.metric("BUT OD/OI", f"{hlc.get('lc_but_od','—')}/{hlc.get('lc_but_oi','—')}" or "—")

                                    # Bloque 5 — Lente Definitivo (el más importante)
                                    if any(hlc.get(k,"") for k in ["lc_final_od","lc_final_oi","lc_marca_final"]):
                                        st.markdown("<b style='color:#7c3f00;'>✔️ Lente Definitivo</b>", unsafe_allow_html=True)
                                        st.markdown(f"""
                                        <table style='width:100%;border-collapse:collapse;font-size:13px;'>
                                        <thead><tr style='background:#f5e6cc;'>
                                            <th style='padding:6px 10px;text-align:left;color:#7c3f00;'>Ojo</th>
                                            <th style='padding:6px 10px;text-align:left;'>Parámetros Finales</th>
                                        </tr></thead>
                                        <tbody>
                                        <tr style='background:#fdf6ee;'>
                                            <td style='padding:6px 10px;font-weight:700;color:#d97706;'>🟠 OD</td>
                                            <td style='padding:6px 10px;'>{hlc.get('lc_final_od','—') or '—'}</td>
                                        </tr>
                                        <tr style='background:#fff9f0;'>
                                            <td style='padding:6px 10px;font-weight:700;color:#92400e;'>🟤 OI</td>
                                            <td style='padding:6px 10px;'>{hlc.get('lc_final_oi','—') or '—'}</td>
                                        </tr>
                                        </tbody></table>
                                        """, unsafe_allow_html=True)
                                        lfd1,lfd2,lfd3 = st.columns(3)
                                        lfd1.metric("Marca/Lab.", hlc.get("lc_marca_final","—") or "—")
                                        lfd2.metric("Modalidad", hlc.get("lc_modalidad","—") or "—")
                                        lfd3.metric("Próx. Control", hlc.get("lc_proximo_control","—") or "—")

                                    if hlc.get("lc_observaciones"):
                                        st.markdown(f"**📝 Obs. Evolución:** {hlc['lc_observaciones']}")

                                    st.markdown("---")
                                    ed1, ed2 = st.columns(2)
                                    with ed1:
                                        if st.button("✏️ Editar Historia LC", key=f"edit_lc_{hlc_id}", type="primary", use_container_width=True):
                                            st.session_state[f"editando_lc_{hlc_id}"] = True
                                            st.rerun()
                                    with ed2:
                                        if st.button("🗑️ Eliminar Historia LC", key=f"del_lc_{hlc_id}", type="secondary", use_container_width=True):
                                            eliminar_historia_lc(hlc_id)
                                            from database import cargar_historias_lc
                                            st.session_state.df_historias_lc = cargar_historias_lc()
                                            st.success("Historia LC eliminada.")
                                            st.rerun()

                                    # --- RECOMENDACIONES ---
                                    st.markdown("#### 💡 Recomendaciones / Lo que se llevó el paciente (LC)")
                                    curr_rec_lc = hlc.get('recomendaciones', '')
                                    if str(curr_rec_lc) == "nan": curr_rec_lc = ""
                                    rec_editado_lc = st.text_area("Indicaciones médicas, líquidos recomendados, etc.", value=str(curr_rec_lc), key=f"rec_lc_{hlc_id}", height=80)
                                    if st.button("💾 Guardar recomendación", key=f"btn_rec_lc_{hlc_id}", use_container_width=True):
                                        from database import actualizar_historia_lc, cargar_historias_lc
                                        actualizar_historia_lc(hlc_id, {"recomendaciones": rec_editado_lc})
                                        st.toast("✅ Recomendación guardada en la nube.")
                                        st.session_state.df_historias_lc = cargar_historias_lc()
                                        st.rerun()

                                    st.markdown("---")
                                    bacc1_lc, bacc2_lc, bacc3_lc = st.columns(3)

                                    try:
                                        import base64 as _b64
                                        import urllib.parse
                                        
                                        def _normalizar_tel_lc(tel_raw):
                                            t = str(tel_raw).strip().replace(" ", "").replace("-", "").replace("+", "")
                                            if t.startswith("0"):
                                                t = "593" + t[1:]
                                            elif not t.startswith("593") and t:
                                                t = "593" + t
                                            return t

                                        _opto_login_lc = hlc.get("optometrista_login", "") or st.session_state.get("user_login", "")
                                        _ud_supabase_lc = {}
                                        try:
                                            from database import supabase as _supa
                                            if _supa and _opto_login_lc:
                                                _res = _supa.table("usuarios").select("*").eq("username", _opto_login_lc).execute()
                                                if _res.data:
                                                    _ud_supabase_lc = _res.data[0]
                                        except Exception: pass

                                        _opto_nombre_lc = hlc.get("optometrista", "") or st.session_state.get("user_name", "")

                                        opto_info_lc = {
                                            "username":     _opto_login_lc,
                                            "nombre":       _ud_supabase_lc.get("nombre")   or _opto_nombre_lc,
                                            "cargo":        _ud_supabase_lc.get("cargo")    or st.session_state.get("user_cargo", "Optometrista"),
                                            "registro":     _ud_supabase_lc.get("registro") or st.session_state.get("user_registro", ""),
                                            "telefono":     _ud_supabase_lc.get("telefono") or st.session_state.get("user_telefono", ""),
                                            "firma_base64": _ud_supabase_lc.get("firma_base64") or st.session_state.get("user_firma", "")
                                        }

                                        pdf_bytes_lc = generar_pdf_historia_lc(hlc.to_dict(), pac.to_dict(), opto_info_lc)
                                        pdf_bytes_ind = generar_pdf_historia_lc(hlc.to_dict(), pac.to_dict(), opto_info_lc, is_indicaciones=True)

                                        tel_pac_lc = _normalizar_tel_lc(pac.get("telefono", ""))
                                        nombre_pac_lc = pac.get('nombre', pac.get('nombres', ''))

                                        def _log_pdf_descarga_lc():
                                            from database import registrar_auditoria
                                            registrar_auditoria(
                                                accion="Descargar PDF LC",
                                                entidad="Certificado LC",
                                                detalle=f"Paciente: {nombre_pac_lc} | Historia LC ID: {hlc_id}",
                                                usuario=st.session_state.get("user_login", ""),
                                                nombre_usuario=st.session_state.get("user_name", ""),
                                                sucursal=st.session_state.get("sucursal_activa", "")
                                            )

                                        def _log_pdf_descarga_ind_lc():
                                            from database import registrar_auditoria
                                            registrar_auditoria(
                                                accion="Descargar PDF LC",
                                                entidad="Indicaciones LC",
                                                detalle=f"Paciente: {nombre_pac_lc} | Historia LC ID: {hlc_id}",
                                                usuario=st.session_state.get("user_login", ""),
                                                nombre_usuario=st.session_state.get("user_name", ""),
                                                sucursal=st.session_state.get("sucursal_activa", "")
                                            )

                                        with bacc1_lc:
                                            with st.popover("📥 Descargar PDFs LC", use_container_width=True):
                                                st.download_button(
                                                    label="📥 Certificado LC (PDF)",
                                                    data=pdf_bytes_lc,
                                                    file_name=f"Certificado_LC_{nombre_pac_lc.replace(' ','_')}.pdf",
                                                    mime="application/pdf",
                                                    use_container_width=True,
                                                    key=f"dl_pdf_lc_{hlc_id}",
                                                    on_click=_log_pdf_descarga_lc
                                                )
                                                st.download_button(
                                                    label="📥 Indicaciones LC (PDF)",
                                                    data=pdf_bytes_ind,
                                                    file_name=f"Indicaciones_LC_{nombre_pac_lc.replace(' ','_')}.pdf",
                                                    mime="application/pdf",
                                                    use_container_width=True,
                                                    key=f"dl_ind_lc_{hlc_id}",
                                                    on_click=_log_pdf_descarga_ind_lc
                                                )

                                        with bacc2_lc:
                                            with st.popover("👁️ Vista Previa y Enviar LC", use_container_width=True):
                                                with st.expander("👁️ Vista Previa Certificado"):
                                                    _b64str_lc = _b64.b64encode(pdf_bytes_lc).decode("utf-8")
                                                    st.markdown(
                                                        f'<iframe src="data:application/pdf;base64,{_b64str_lc}" '
                                                        f'width="100%" height="400px" style="border:none;"></iframe>',
                                                        unsafe_allow_html=True
                                                    )
                                                with st.expander("👁️ Vista Previa Indicaciones"):
                                                    _b64str_ind = _b64.b64encode(pdf_bytes_ind).decode("utf-8")
                                                    st.markdown(
                                                        f'<iframe src="data:application/pdf;base64,{_b64str_ind}" '
                                                        f'width="100%" height="400px" style="border:none;"></iframe>',
                                                        unsafe_allow_html=True
                                                    )
                                                
                                                if tel_pac_lc:
                                                    msg_pdf_lc = generar_msg_hc_lc(hlc.to_dict(), pac.to_dict())
                                                    wa_pdf_lc_url = f"https://wa.me/{tel_pac_lc}?text={urllib.parse.quote(msg_pdf_lc)}"
                                                    if st.button("📲 WhatsApp (Certificado LC)", key=f"btn_wa_pdf_lc_{hlc_id}", use_container_width=True):
                                                        from database import registrar_auditoria
                                                        registrar_auditoria(
                                                            accion="Enviar WhatsApp LC",
                                                            entidad="Certificado LC PDF",
                                                            detalle=f"Paciente: {nombre_pac_lc} | Tel: {tel_pac_lc}",
                                                            usuario=st.session_state.get("user_login", ""),
                                                            nombre_usuario=st.session_state.get("user_name", ""),
                                                            sucursal=st.session_state.get("sucursal_activa", "")
                                                        )
                                                        st.markdown(f'<a href="{wa_pdf_lc_url}" target="_blank" id="wa_lc_link_{hlc_id}"><script>document.getElementById("wa_lc_link_{hlc_id}").click();</script></a>', unsafe_allow_html=True)
                                                        st.info(f"👉 [Abrir WhatsApp Certificado]({wa_pdf_lc_url})")

                                                    msg_pdf_ind = generar_msg_indicaciones_lc(hlc.to_dict(), pac.to_dict())
                                                    wa_pdf_ind_url = f"https://wa.me/{tel_pac_lc}?text={urllib.parse.quote(msg_pdf_ind)}"
                                                    if st.button("📲 WhatsApp (Indicaciones LC)", key=f"btn_wa_pdf_ind_{hlc_id}", use_container_width=True):
                                                        from database import registrar_auditoria
                                                        registrar_auditoria(
                                                            accion="Enviar WhatsApp LC",
                                                            entidad="Indicaciones LC PDF",
                                                            detalle=f"Paciente: {nombre_pac_lc} | Tel: {tel_pac_lc}",
                                                            usuario=st.session_state.get("user_login", ""),
                                                            nombre_usuario=st.session_state.get("user_name", ""),
                                                            sucursal=st.session_state.get("sucursal_activa", "")
                                                        )
                                                        st.markdown(f'<a href="{wa_pdf_ind_url}" target="_blank" id="wa_ind_lc_link_{hlc_id}"><script>document.getElementById("wa_ind_lc_link_{hlc_id}").click();</script></a>', unsafe_allow_html=True)
                                                        st.info(f"👉 [Abrir WhatsApp Indicaciones]({wa_pdf_ind_url})")
                                                else:
                                                    st.caption("⚠️ Sin teléfono")

                                        with bacc3_lc:
                                            with st.popover("💊 Enviar Indicacion LC", use_container_width=True):
                                                st.markdown("<p style='font-size:14px; font-weight:700; margin-bottom:2px;'>📋 Indicaciones LC para el Paciente</p>", unsafe_allow_html=True)
                                                st.caption("Selecciona una plantilla, edítala y envía.")
                                                
                                                wa_key_lc = f"wa_msg_val_lc_{hlc_id}"
                                                if wa_key_lc not in st.session_state:
                                                    st.session_state[wa_key_lc] = hlc.get("recomendaciones", "") or ""

                                                c_s1, c_s2 = st.columns(2)
                                                if c_s1.button("🧼 Higiene LC", key=f"btn_s1_lc_{hlc_id}", use_container_width=True):
                                                    st.session_state[wa_key_lc] = "🧼 Lave y seque muy bien sus manos antes de colocar o retirar sus lentes de contacto. Nunca use saliva ni agua de grifo."
                                                    st.rerun()
                                                if c_s2.button("💧 Lubricación", key=f"btn_s2_lc_{hlc_id}", use_container_width=True):
                                                    st.session_state[wa_key_lc] = "💧 Aplique 1 gota de lágrimas artificiales específicas para lentes de contacto cada 4 horas para mantener la hidratación."
                                                    st.rerun()
                                                
                                                c_s3, c_s4 = st.columns(2)
                                                if c_s3.button("🕒 Uso Diario", key=f"btn_s3_lc_{hlc_id}", use_container_width=True):
                                                    st.session_state[wa_key_lc] = "🕒 No exceda las horas de uso diario recomendadas (máximo 8-10 horas) y recuerde retirárselos antes de dormir."
                                                    st.rerun()
                                                if c_s4.button("📅 Control LC", key=f"btn_s4_lc_{hlc_id}", use_container_width=True):
                                                    st.session_state[wa_key_lc] = "📅 Agende su control de seguimiento en 1 semana para verificar que la córnea y la adaptación del lente sigan saludables."
                                                    st.rerun()

                                                indicacion_editada_lc = st.text_area(
                                                    "✏️ Edita el mensaje antes de enviar:",
                                                    key=wa_key_lc,
                                                    height=140,
                                                    placeholder="Selecciona una plantilla arriba o escribe aquí..."
                                                )
                                                
                                                if tel_pac_lc:
                                                    fecha_hc_lc = hlc.get('fecha', '')
                                                    full_wa_msg_lc = (
                                                        f"👁️ *Happy Vision — Indicaciones Lentes de Contacto*\n\n"
                                                        f"Estimado/a *{nombre_pac_lc}*, a continuación las indicaciones de su consulta de lentes de contacto del *{fecha_hc_lc}*:\n\n"
                                                        f"{indicacion_editada_lc}\n\n"
                                                        f"Ante cualquier duda o molestia, comuníquese con nosotros.\n"
                                                        f"📍 *Happy Vision* | 📞 +593 96 324 1158"
                                                    )
                                                    wa_url_lc = f"https://wa.me/{tel_pac_lc}?text={urllib.parse.quote(full_wa_msg_lc)}"
                                                    if st.button("📲 Enviar por WhatsApp", key=f"btn_wa_ind_lc_send_{hlc_id}", use_container_width=True, type="primary"):
                                                        from database import registrar_auditoria
                                                        registrar_auditoria(
                                                            accion="Enviar WhatsApp",
                                                            entidad="Indicaciones LC WhatsApp",
                                                            detalle=f"Paciente: {nombre_pac_lc} | Tel: {tel_pac_lc}",
                                                            usuario=st.session_state.get("user_login", ""),
                                                            nombre_usuario=st.session_state.get("user_name", ""),
                                                            sucursal=st.session_state.get("sucursal_activa", "")
                                                        )
                                                        st.markdown(f'<a href="{wa_url_lc}" target="_blank" id="wa_ind_lc_send_link_{hlc_id}"><script>document.getElementById("wa_ind_lc_send_link_{hlc_id}").click();</script></a>', unsafe_allow_html=True)
                                                        st.info(f"👉 [Click aquí para abrir WhatsApp]({wa_url_lc})")
                                                else:
                                                    st.caption("⚠️ Sin teléfono registrado")

                                    except Exception as e:
                                        st.error(f"⚠️ Error generando PDF: {e}")
                                else:
                                    if st.button("⬅️ Volver a vista de lectura", key=f"cancel_edit_lc_{hlc_id}"):
                                        st.session_state[f"editando_lc_{hlc_id}"] = False
                                        st.rerun()

                                    with st.form(key=f"edit_lc_form_full_{hlc_id}", clear_on_submit=False):
                                        st.markdown(f"""
                                        <div style='background:linear-gradient(135deg,#2c1a0e,#7c3f00);border-radius:14px;
                                        padding:18px 24px;margin-bottom:14px;color:white;'>
                                            <h3 style='margin:0;font-size:1.15rem;'>✏️ Editando Historia Clínica - Lentes de Contacto</h3>
                                        </div>
                                        """, unsafe_allow_html=True)

                                        elc_fecha_val = hlc.get('fecha', str(date.today()))
                                        if len(str(elc_fecha_val)) >= 10: elc_fecha_val = elc_fecha_val[:10]
                                        elc_fecha = st.date_input("📅 Fecha de la Consulta", value=date.fromisoformat(elc_fecha_val), key=f"efec_{hlc_id}")

                                        import re

                                        # ── BLOQUE 1: ANAMNESIS ─────────────────────────────────
                                        st.markdown("""
                                        <div style='background:linear-gradient(135deg,#fdf6ee,#f5e6cc);border:1px solid #d4a96a;
                                        border-radius:10px;padding:14px 18px;margin:10px 0 8px 0;'>
                                        <b style='color:#7c3f00;font-size:13px;text-transform:uppercase;letter-spacing:.06em;'>
                                        📝 Bloque 1 — Anamnesis Especializada</b></div>
                                        """, unsafe_allow_html=True)
                                        ea1, ea2 = st.columns(2)
                                        e_lc_usu = ea1.selectbox("¿Usuario previo de LC?", ["", "Sí", "No"], index=["", "Sí", "No"].index(hlc.get('lc_usuario_previo', '')) if hlc.get('lc_usuario_previo', '') in ["", "Sí", "No"] else 0, key=f"eu1_{hlc_id}")
                                        e_lc_tip = ea2.selectbox("Tipo de lente anterior", ["", "Blando esférico", "Blando tórico", "Multifocal", "RGP", "Escleral", "Ninguno"], index=["", "Blando esférico", "Blando tórico", "Multifocal", "RGP", "Escleral", "Ninguno"].index(hlc.get('lc_tipo_lente_ant', '')) if hlc.get('lc_tipo_lente_ant', '') in ["", "Blando esférico", "Blando tórico", "Multifocal", "RGP", "Escleral", "Ninguno"] else 0, key=f"eu2_{hlc_id}")
                                        ea3, ea4 = st.columns(2)
                                        e_lc_mar = ea3.text_input("Marca/Laboratorio anterior", value=str(hlc.get('lc_marca_ant', '')), key=f"eu3_{hlc_id}")
                                        e_lc_hor = ea4.text_input("Horas de uso diario", value=str(hlc.get('lc_horas_uso', '')), key=f"eu4_{hlc_id}")
                                        ea5, ea6 = st.columns(2)
                                        e_lc_sol = ea5.selectbox("Solución de mantenimiento habitual", ["", "Solución multipropósito", "Peróxido de hidrógeno", "Jabón y agua (alerta)", "Ninguna"], index=["", "Solución multipropósito", "Peróxido de hidrógeno", "Jabón y agua (alerta)", "Ninguna"].index(hlc.get('lc_solucion_habitual', '')) if hlc.get('lc_solucion_habitual', '') in ["", "Solución multipropósito", "Peróxido de hidrógeno", "Jabón y agua (alerta)", "Ninguna"] else 0, key=f"eu5_{hlc_id}")
                                        e_lc_mot = ea6.selectbox("Motivo de la nueva consulta", ["", "Estética", "Deporte", "Renovación", "Incomodidad con los anteriores", "Queratocono", "Necesidad médica"], index=["", "Estética", "Deporte", "Renovación", "Incomodidad con los anteriores", "Queratocono", "Necesidad médica"].index(hlc.get('lc_motivo_consulta', '')) if hlc.get('lc_motivo_consulta', '') in ["", "Estética", "Deporte", "Renovación", "Incomodidad con los anteriores", "Queratocono", "Necesidad médica"] else 0, key=f"eu6_{hlc_id}")

                                        # ── BLOQUE 2: EXAMEN PRELIMINAR ──────────────────────────
                                        st.markdown("""
                                        <div style='background:linear-gradient(135deg,#fdf6ee,#f5e6cc);border:1px solid #d4a96a;
                                        border-radius:10px;padding:14px 18px;margin:10px 0 8px 0;'>
                                        <b style='color:#7c3f00;font-size:13px;text-transform:uppercase;letter-spacing:.06em;'>
                                        🔬 Bloque 2 — Examen Preliminar y Refracción</b></div>
                                        """, unsafe_allow_html=True)

                                        st.markdown("<small><b>AV Sin Corrección (S/C)</b></small>", unsafe_allow_html=True)
                                        eb1, eb2 = st.columns(2)
                                        e_lc_avsc_od = eb1.text_input("🟠 OD AV S/C", value=str(hlc.get('lc_avsc_od', '')), key=f"eb1_{hlc_id}")
                                        e_lc_avsc_oi = eb2.text_input("🟤 OI AV S/C", value=str(hlc.get('lc_avsc_oi', '')), key=f"eb2_{hlc_id}")

                                        st.markdown("<small><b>Refracción Subjetiva Actual (Rx Gafas)</b></small>", unsafe_allow_html=True)
                                        val_rx_od = hlc.get('lc_rx_od', '')
                                        val_rx_oi = hlc.get('lc_rx_oi', '')
                                        def parse_rx(rx_str):
                                            if not rx_str or '/' not in str(rx_str): return "", "", ""
                                            try:
                                                parts = str(rx_str).split('/')
                                                esf = parts[0].strip()
                                                rest = parts[1].split('x')
                                                cil = rest[0].strip()
                                                eje = rest[1].strip() if len(rest) > 1 else ""
                                                return esf, cil, eje
                                            except Exception:
                                                return str(rx_str), "", ""

                                        e_rx_od_esf_val, e_rx_od_cil_val, e_rx_od_eje_val = parse_rx(val_rx_od)
                                        e_rx_oi_esf_val, e_rx_oi_cil_val, e_rx_oi_eje_val = parse_rx(val_rx_oi)

                                        lerx1,lerx2,lerx3,lerx4 = st.columns([0.15,1,1,1])
                                        lerx1.markdown("<p style='margin-top:28px'><b>🟠</b></p>", unsafe_allow_html=True)
                                        e_rx_od_esf = lerx2.text_input("ESF OD", value=e_rx_od_esf_val, key=f"erx_od_esf_{hlc_id}")
                                        e_rx_od_cil = lerx3.text_input("CIL OD", value=e_rx_od_cil_val, key=f"erx_od_cil_{hlc_id}")
                                        e_rx_od_eje = lerx4.text_input("EJE OD", value=e_rx_od_eje_val, key=f"erx_od_eje_{hlc_id}")

                                        lerx5,lerx6,lerx7,lerx8 = st.columns([0.15,1,1,1])
                                        lerx5.markdown("<p style='margin-top:28px'><b>🟤</b></p>", unsafe_allow_html=True)
                                        e_rx_oi_esf = lerx6.text_input("ESF OI", value=e_rx_oi_esf_val, key=f"erx_oi_esf_{hlc_id}")
                                        e_rx_oi_cil = lerx7.text_input("CIL OI", value=e_rx_oi_cil_val, key=f"erx_oi_cil_{hlc_id}")
                                        e_rx_oi_eje = lerx8.text_input("EJE OI", value=e_rx_oi_eje_val, key=f"erx_oi_eje_{hlc_id}")

                                        e_lc_dv = st.text_input("📐 Distancia al Vértice (DV en mm)", value=str(hlc.get('lc_distancia_vertice', '')), key=f"eb5_{hlc_id}")

                                        st.markdown("<small><b>Queratometría / Topografía</b></small>", unsafe_allow_html=True)
                                        val_kera_od = hlc.get('lc_kera_od', '')
                                        val_kera_oi = hlc.get('lc_kera_oi', '')
                                        def parse_kera(k_str):
                                            if not k_str or '/' not in str(k_str): return "", "", ""
                                            try:
                                                parts = str(k_str).split('/')
                                                plana = parts[0].strip()
                                                rest = parts[1].split('@')
                                                curva = rest[0].strip()
                                                eje = rest[1].strip() if len(rest) > 1 else ""
                                                return plana, curva, eje
                                            except Exception:
                                                return str(k_str), "", ""

                                        e_k_od_p_val, e_k_od_c_val, e_k_od_e_val = parse_kera(val_kera_od)
                                        e_k_oi_p_val, e_k_oi_c_val, e_k_oi_e_val = parse_kera(val_kera_oi)

                                        lek1,lek2,lek3,lek4 = st.columns([0.15,1,1,1])
                                        lek1.markdown("<p style='margin-top:28px'><b>🟠</b></p>", unsafe_allow_html=True)
                                        e_lk_od_p = lek2.text_input("K Plana OD", value=e_k_od_p_val, key=f"ek1_{hlc_id}")
                                        e_lk_od_c = lek3.text_input("K Curva OD", value=e_k_od_c_val, key=f"ek2_{hlc_id}")
                                        e_lk_od_e = lek4.text_input("Eje OD", value=e_k_od_e_val, key=f"ek3_{hlc_id}")

                                        lek5,lek6,lek7,lek8 = st.columns([0.15,1,1,1])
                                        lek5.markdown("<p style='margin-top:28px'><b>🟤</b></p>", unsafe_allow_html=True)
                                        e_lk_oi_p = lek6.text_input("K Plana OI", value=e_k_oi_p_val, key=f"ek4_{hlc_id}")
                                        e_lk_oi_c = lek7.text_input("K Curva OI", value=e_k_oi_c_val, key=f"ek5_{hlc_id}")
                                        e_lk_oi_e = lek8.text_input("Eje OI", value=e_k_oi_e_val, key=f"ek6_{hlc_id}")

                                        eas1, eas2 = st.columns(2)
                                        e_ast_od = eas1.text_input("⚪ Astigmatismo Corneal OD (D)", value=str(hlc.get('lc_astig_corneal_od', '')), key=f"eas1_{hlc_id}")
                                        e_ast_oi = eas2.text_input("⚪ Astigmatismo Corneal OI (D)", value=str(hlc.get('lc_astig_corneal_oi', '')), key=f"eas2_{hlc_id}")

                                        # ── BLOQUE 3: BIOMICROSCOPÍA ────────────────────────────
                                        st.markdown("""
                                        <div style='background:linear-gradient(135deg,#fdf6ee,#f5e6cc);border:1px solid #d4a96a;
                                        border-radius:10px;padding:14px 18px;margin:10px 0 8px 0;'>
                                        <b style='color:#7c3f00;font-size:13px;text-transform:uppercase;letter-spacing:.06em;'>
                                        🔬 Bloque 3 — Evaluación de la Salud Ocular (Biomicroscopía)</b></div>
                                        """, unsafe_allow_html=True)
                                        em1, em2 = st.columns(2)
                                        e_lc_par = em1.selectbox("👁️ Párpados / Glándulas de Meibomio", ["", "Normal", "Disfunción leve", "Disfunción severa", "Blefaritis"], index=["", "Normal", "Disfunción leve", "Disfunción severa", "Blefaritis"].index(hlc.get('lc_parpados', '')) if hlc.get('lc_parpados', '') in ["", "Normal", "Disfunción leve", "Disfunción severa", "Blefaritis"] else 0, key=f"em1_{hlc_id}")
                                        e_lc_con = em2.selectbox("Conjuntiva (Hiperemia)", ["", "Grado 0 (Ninguna)", "Grado 1 (Leve)", "Grado 2 (Moderada)", "Grado 3 (Severa)"], index=["", "Grado 0 (Ninguna)", "Grado 1 (Leve)", "Grado 2 (Moderada)", "Grado 3 (Severa)"].index(hlc.get('lc_conjuntiva', '')) if hlc.get('lc_conjuntiva', '') in ["", "Grado 0 (Ninguna)", "Grado 1 (Leve)", "Grado 2 (Moderada)", "Grado 3 (Severa)"] else 0, key=f"em2_{hlc_id}")
                                        em3, em4 = st.columns(2)
                                        e_lc_eve = em3.selectbox("Eversión Palpebral (Papilas)", ["", "Ausentes", "Leves", "Conjuntivitis Papilar Gigante (GPC)"], index=["", "Ausentes", "Leves", "Conjuntivitis Papilar Gigante (GPC)"].index(hlc.get('lc_eversion', '')) if hlc.get('lc_eversion', '') in ["", "Ausentes", "Leves", "Conjuntivitis Papilar Gigante (GPC)"] else 0, key=f"em3_{hlc_id}")
                                        e_lc_cor = em4.selectbox("Córnea (Tinc. Fluoresceína)", ["", "Grado 0 (Limpia)", "Grado 1 (Punteado leve)", "Grado 2 (Tinc. confluente)", "Grado 3 (Úlcera/Infiltrado)"], index=["", "Grado 0 (Limpia)", "Grado 1 (Punteado leve)", "Grado 2 (Tinc. confluente)", "Grado 3 (Úlcera/Infiltrado)"].index(hlc.get('lc_cornea', '')) if hlc.get('lc_cornea', '') in ["", "Grado 0 (Limpia)", "Grado 1 (Punteado leve)", "Grado 2 (Tinc. confluente)", "Grado 3 (Úlcera/Infiltrado)"] else 0, key=f"em4_{hlc_id}")
                                        em5, em6, em7 = st.columns(3)
                                        e_lc_but_od = em5.text_input("BUT OD (seg)", value=str(hlc.get('lc_but_od', '')), key=f"em5_{hlc_id}")
                                        e_lc_but_oi = em6.text_input("BUT OI (seg)", value=str(hlc.get('lc_but_oi', '')), key=f"em6_{hlc_id}")
                                        e_lc_men = em7.selectbox("Menisco Lagrimal", ["", "Normal", "Alto", "Escaso"], index=["", "Normal", "Alto", "Escaso"].index(hlc.get('lc_menisco', '')) if hlc.get('lc_menisco', '') in ["", "Normal", "Alto", "Escaso"] else 0, key=f"em7_{hlc_id}")

                                        # ── BLOQUE 4: LENTE DE PRUEBA ────────────────────────────
                                        st.markdown("""
                                        <div style='background:linear-gradient(135deg,#fdf6ee,#f5e6cc);border:1px solid #d4a96a;
                                        border-radius:10px;padding:14px 18px;margin:10px 0 8px 0;'>
                                        <b style='color:#7c3f00;font-size:13px;text-transform:uppercase;letter-spacing:.06em;'>
                                        🔄 Bloque 4 — Registro de Pruebas (Lente de Prueba)</b></div>
                                        """, unsafe_allow_html=True)
                                        e_lc_pru_tip = st.selectbox("Tipo de Lente de Prueba", ["", "Blando Hidrogel", "Hidrogel de Silicona", "RGP", "Escleral"], index=["", "Blando Hidrogel", "Hidrogel de Silicona", "RGP", "Escleral"].index(hlc.get('lc_prueba_tipo', '')) if hlc.get('lc_prueba_tipo', '') in ["", "Blando Hidrogel", "Hidrogel de Silicona", "RGP", "Escleral"] else 0, key=f"ep1_{hlc_id}")

                                        val_pru_od = hlc.get('lc_prueba_od', '')
                                        val_pru_oi = hlc.get('lc_prueba_oi', '')

                                        def parse_prueba(s):
                                            if not s: return "", "", "", ""
                                            bc = re.search(r"BC:\\s*([^\\s]+)", str(s))
                                            td = re.search(r"TD:\\s*([^\\s]+)", str(s))
                                            sph_cil = re.search(r"TD:\\s*[^\\s]+\\s+([^\\s/]+)/([^\s/]+)", str(s))
                                            if not sph_cil:
                                                sph_cil = re.search(r"([^\\s/]+)/([^\\s/]+)$", str(s))
                                            val_bc = bc.group(1) if bc else ""
                                            val_td = td.group(1) if td else ""
                                            val_sph = sph_cil.group(1) if sph_cil else ""
                                            val_cil = sph_cil.group(2) if sph_cil else ""
                                            return val_bc, val_td, val_sph, val_cil

                                        e_pru_od_bc, e_pru_od_td, e_pru_od_esf, e_pru_od_cil = parse_prueba(val_pru_od)
                                        e_pru_oi_bc, e_pru_oi_td, e_pru_oi_esf, e_pru_oi_cil = parse_prueba(val_pru_oi)

                                        st.markdown("<small><b>Parámetros del Lente de Prueba</b></small>", unsafe_allow_html=True)
                                        lep1,lep2,lep3,lep4,lep5 = st.columns([0.15,1,1,1,1])
                                        lep1.markdown("<p style='margin-top:28px'><b>🟠</b></p>", unsafe_allow_html=True)
                                        e_lp_od_b = lep2.text_input("BC OD", value=e_pru_od_bc, key=f"ep2_{hlc_id}")
                                        e_lp_od_t = lep3.text_input("TD OD", value=e_pru_od_td, key=f"ep4_{hlc_id}")
                                        e_lp_od_e = lep4.text_input("Esf OD", value=e_pru_od_esf, key=f"ep5_{hlc_id}")
                                        e_lp_od_c = lep5.text_input("Cil OD", value=e_pru_od_cil, key=f"ep6_{hlc_id}")

                                        lep6,lep7,lep8,lep9,lep10 = st.columns([0.15,1,1,1,1])
                                        lep6.markdown("<p style='margin-top:28px'><b>🟤</b></p>", unsafe_allow_html=True)
                                        e_lp_oi_b = lep7.text_input("BC OI", value=e_pru_oi_bc, key=f"ep7_{hlc_id}")
                                        e_lp_oi_t = lep8.text_input("TD OI", value=e_pru_oi_td, key=f"ep8_{hlc_id}")
                                        e_lp_oi_e = lep9.text_input("Esf OI", value=e_pru_oi_esf, key=f"ep9_{hlc_id}")
                                        e_lp_oi_c = lep10.text_input("Cil OI", value=e_pru_oi_cil, key=f"ep10_{hlc_id}")

                                        ee1, ee2, ee3, ee4 = st.columns(4)
                                        e_lc_cen = ee1.selectbox("Centrado", ["", "Centrado", "Descentrado Sup.", "Descentrado Inf.", "Descentrado Nasal", "Descentrado Temporal"], index=["", "Centrado", "Descentrado Sup.", "Descentrado Inf.", "Descentrado Nasal", "Descentrado Temporal"].index(hlc.get('lc_centrado', '')) if hlc.get('lc_centrado', '') in ["", "Centrado", "Descentrado Sup.", "Descentrado Inf.", "Descentrado Nasal", "Descentrado Temporal"] else 0, key=f"ee1_{hlc_id}")
                                        e_lc_mov = ee2.selectbox("Movimiento al parpadeo", ["", "Adecuado (0.5-1mm)", "Escaso (apretado)", "Excesivo (flojo)"], index=["", "Adecuado (0.5-1mm)", "Escaso (apretado)", "Excesivo (flojo)"].index(hlc.get('lc_movimiento', '')) if hlc.get('lc_movimiento', '') in ["", "Adecuado (0.5-1mm)", "Escaso (apretado)", "Excesivo (flojo)"] else 0, key=f"ee2_{hlc_id}")
                                        e_lc_pus = ee3.selectbox("Push-up Test", ["", "Positiva (Aceptable)", "Negativa (Muy apretado)"], index=["", "Positiva (Aceptable)", "Negativa (Muy apretado)"].index(hlc.get('lc_pushup', '')) if hlc.get('lc_pushup', '') in ["", "Positiva (Aceptable)", "Negativa (Muy apretado)"] else 0, key=f"ee3_{hlc_id}")
                                        e_lc_rot = ee4.text_input("Rotación de eje (°)", value=str(hlc.get('lc_rotacion', '')), key=f"ee4_{hlc_id}")

                                        st.markdown("<small><b>Sobrerrefracción (Over-Refraction)</b></small>", unsafe_allow_html=True)
                                        val_sobre_od = hlc.get('lc_sobre_od', '')
                                        val_sobre_oi = hlc.get('lc_sobre_oi', '')
                                        
                                        def parse_sobre(s):
                                            if not s: return "", "", ""
                                            sph_align = re.search(r"^([^\\s/]+)/([^\\s/]+)", str(s))
                                            av = re.search(r"AV:\\s*(.*)", str(s))
                                            val_sph = sph_align.group(1) if sph_align else ""
                                            val_cil = sph_align.group(2) if sph_align else ""
                                            val_av = av.group(1) if av else ""
                                            return val_sph, val_cil, val_av

                                        e_ls_od_esf_val, e_ls_od_cil_val, e_ls_od_av_val = parse_sobre(val_sobre_od)
                                        e_ls_oi_esf_val, e_ls_oi_cil_val, e_ls_oi_av_val = parse_sobre(val_sobre_oi)

                                        les1,les2,les3,les4 = st.columns([0.15,1,1,1])
                                        les1.markdown("<p style='margin-top:28px'><b>🟠</b></p>", unsafe_allow_html=True)
                                        e_ls_od_e = les2.text_input("SR Esf OD", value=e_ls_od_esf_val, key=f"es1_{hlc_id}")
                                        e_ls_od_c = les3.text_input("SR Cil OD", value=e_ls_od_cil_val, key=f"es2_{hlc_id}")
                                        e_ls_od_a = les4.text_input("AV lograda OD", value=e_ls_od_av_val, key=f"es3_{hlc_id}")

                                        les5,les6,les7,les8 = st.columns([0.15,1,1,1])
                                        les5.markdown("<p style='margin-top:28px'><b>🟤</b></p>", unsafe_allow_html=True)
                                        e_ls_oi_e = les6.text_input("SR Esf OI", value=e_ls_oi_esf_val, key=f"es4_{hlc_id}")
                                        e_ls_oi_c = les7.text_input("SR Cil OI", value=e_ls_oi_cil_val, key=f"es5_{hlc_id}")
                                        e_ls_oi_a = les8.text_input("AV lograda OI", value=e_ls_oi_av_val, key=f"es6_{hlc_id}")

                                        # ── BLOQUE 5: LENTE DEFINITIVO ───────────────────────────
                                        st.markdown("""
                                        <div style='background:linear-gradient(135deg,#fdf6ee,#f5e6cc);border:1px solid #d4a96a;
                                        border-radius:10px;padding:14px 18px;margin:10px 0 8px 0;'>
                                        <b style='color:#7c3f00;font-size:13px;text-transform:uppercase;letter-spacing:.06em;'>
                                        ✔️ Bloque 5 — Diagnóstico y Lente Definitivo</b></div>
                                        """, unsafe_allow_html=True)

                                        st.markdown("<small><b>Lente Final Autorizado</b></small>", unsafe_allow_html=True)
                                        val_final_od = hlc.get('lc_final_od', '')
                                        val_final_oi = hlc.get('lc_final_oi', '')

                                        def parse_final(s):
                                            if not s: return "", "", "", "", ""
                                            bc = re.search(r"BC:\\s*([^\\s]+)", str(s))
                                            td = re.search(r"TD:\\s*([^\\s]+)", str(s))
                                            sph_cil = re.search(r"TD:\\s*[^\\s]+\\s+([^\\s/]+)/([^\s/]+)", str(s))
                                            if not sph_cil:
                                                sph_cil = re.search(r"([^\\s/]+)/([^\\s/]+)", str(s))
                                            add = re.search(r"Add:\\s*([^\\s]+)", str(s))
                                            val_bc = bc.group(1) if bc else ""
                                            val_td = td.group(1) if td else ""
                                            val_sph = sph_cil.group(1) if sph_cil else ""
                                            val_cil = sph_cil.group(2) if sph_cil else ""
                                            val_add = add.group(1) if add else ""
                                            return val_bc, val_td, val_sph, val_cil, val_add

                                        e_lf_od_bc, e_lf_od_td, e_lf_od_esf, e_lf_od_cil, e_lf_od_add = parse_final(val_final_od)
                                        e_lf_oi_bc, e_lf_oi_td, e_lf_oi_esf, e_lf_oi_cil, e_lf_oi_add = parse_final(val_final_oi)

                                        lef1,lef2,lef3,lef4,lef5,lef6 = st.columns([0.15,1,1,1,1,1])
                                        lef1.markdown("<p style='margin-top:28px'><b>🟠</b></p>", unsafe_allow_html=True)
                                        e_lf_od_b = lef2.text_input("BC OD ", value=e_lf_od_bc, key=f"ef1_{hlc_id}")
                                        e_lf_od_t = lef3.text_input("TD OD ", value=e_lf_od_td, key=f"ef2_{hlc_id}")
                                        e_lf_od_e = lef4.text_input("Esf OD ", value=e_lf_od_esf, key=f"ef3_{hlc_id}")
                                        e_lf_od_c = lef5.text_input("Cil OD ", value=e_lf_od_cil, key=f"ef4_{hlc_id}")
                                        e_lf_od_a = lef6.text_input("Add OD", value=e_lf_od_add, key=f"ef5_{hlc_id}")

                                        lef7,lef8,lef9,lef10,lef11,lef12 = st.columns([0.15,1,1,1,1,1])
                                        lef7.markdown("<p style='margin-top:28px'><b>🟤</b></p>", unsafe_allow_html=True)
                                        e_lf_oi_b = lef8.text_input("BC OI ", value=e_lf_oi_bc, key=f"ef6_{hlc_id}")
                                        e_lf_oi_t = lef9.text_input("TD OI ", value=e_lf_oi_td, key=f"ef7_{hlc_id}")
                                        e_lf_oi_e = lef10.text_input("Esf OI ", value=e_lf_oi_esf, key=f"ef8_{hlc_id}")
                                        e_lf_oi_c = lef11.text_input("Cil OI ", value=e_lf_oi_cil, key=f"ef9_{hlc_id}")
                                        e_lf_oi_a = lef12.text_input("Add OI", value=e_lf_oi_add, key=f"ef10_{hlc_id}")

                                        el1, el2, el3, el4 = st.columns(4)
                                        e_lc_mar_fin = el1.text_input("Marca / Laboratorio", value=str(hlc.get('lc_marca_final', '')), key=f"el1_{hlc_id}")
                                        e_lc_mod = el2.selectbox("Modalidad de Reemplazo", ["", "Diario", "Quincenal", "Mensual", "Trimestral", "Anual"], index=["", "Diario", "Quincenal", "Mensual", "Trimestral", "Anual"].index(hlc.get('lc_modalidad', '')) if hlc.get('lc_modalidad', '') in ["", "Diario", "Quincenal", "Mensual", "Trimestral", "Anual"] else 0, key=f"el2_{hlc_id}")
                                        e_lc_reg = el3.selectbox("Régimen de Uso", ["", "Uso diario (se los quita para dormir)", "Uso prolongado"], index=["", "Uso diario (se los quita para dormir)", "Uso prolongado"].index(hlc.get('lc_regimen', '')) if hlc.get('lc_regimen', '') in ["", "Uso diario (se los quita para dormir)", "Uso prolongado"] else 0, key=f"el3_{hlc_id}")
                                        e_lc_sol_fin = el4.text_input("Solución Recomendada", value=str(hlc.get('lc_solucion_final', '')), key=f"el4_{hlc_id}")

                                        # ── BLOQUE 6: ENTREGA Y EDUCACIÓN ───────────────────────
                                        st.markdown("""
                                        <div style='background:linear-gradient(135deg,#fdf6ee,#f5e6cc);border:1px solid #d4a96a;
                                        border-radius:10px;padding:14px 18px;margin:10px 0 8px 0;'>
                                        <b style='color:#7c3f00;font-size:13px;text-transform:uppercase;letter-spacing:.06em;'>
                                        🏥 Bloque 6 — Entrega, Educación y Controles</b></div>
                                        """, unsafe_allow_html=True)
                                        er1, er2 = st.columns(2)
                                        e_lc_ins = er1.selectbox("Enseñado Inserción/Remoción", ["", "Aprobado", "Requiere más práctica"], index=["", "Aprobado", "Requiere más práctica"].index(hlc.get('lc_insercion', '')) if hlc.get('lc_insercion', '') in ["", "Aprobado", "Requiere más práctica"] else 0, key=f"er1_{hlc_id}")

                                        e_fent_val = hlc.get('lc_fecha_entrega', str(date.today()))
                                        if not e_fent_val or str(e_fent_val) == "nan": e_fent_val = str(date.today())
                                        if len(str(e_fent_val)) >= 10: e_fent_val = e_fent_val[:10]
                                        e_lc_fent = er2.date_input("Fecha de Entrega", value=date.fromisoformat(e_fent_val), key=f"er2_{hlc_id}")

                                        e_lc_pcon = st.selectbox("Cronograma Próximos Controles", ["", "1 semana", "1 mes", "6 meses", "1 año"], index=["", "1 semana", "1 mes", "6 meses", "1 año"].index(hlc.get('lc_proximo_control', '')) if hlc.get('lc_proximo_control', '') in ["", "1 semana", "1 mes", "6 meses", "1 año"] else 0, key=f"er3_{hlc_id}")
                                        e_lc_obs = st.text_area("Observaciones / Evolución en controles", value=str(hlc.get('lc_observaciones', '')), key=f"er4_{hlc_id}")

                                        if st.form_submit_button("💾 Guardar Cambios LC", type="primary", use_container_width=True):
                                            constructed_rx_od = f"{e_rx_od_esf} / {e_rx_od_cil} x {e_rx_od_eje}"
                                            constructed_rx_oi = f"{e_rx_oi_esf} / {e_rx_oi_cil} x {e_rx_oi_eje}"
                                            constructed_kera_od = f"{e_lk_od_p} / {e_lk_od_c} @ {e_lk_od_e}"
                                            constructed_kera_oi = f"{e_lk_oi_p} / {e_lk_oi_c} @ {e_lk_oi_e}"
                                            constructed_prueba_od = f"BC:{e_lp_od_b} TD:{e_lp_od_t} {e_lp_od_e}/{e_lp_od_c}"
                                            constructed_prueba_oi = f"BC:{e_lp_oi_b} TD:{e_lp_oi_t} {e_lp_oi_e}/{e_lp_oi_c}"
                                            constructed_sobre_od = f"{e_ls_od_e}/{e_ls_od_c} AV:{e_ls_od_a}"
                                            constructed_sobre_oi = f"{e_ls_oi_e}/{e_ls_oi_c} AV:{e_ls_oi_a}"
                                            constructed_final_od = f"BC:{e_lf_od_b} TD:{e_lf_od_t} {e_lf_od_e}/{e_lf_od_c} Add:{e_lf_od_a}"
                                            constructed_final_oi = f"BC:{e_lf_oi_b} TD:{e_lf_oi_t} {e_lf_oi_e}/{e_lf_oi_c} Add:{e_lf_oi_a}"

                                            datos_act = {
                                                "fecha": elc_fecha.isoformat(),
                                                "lc_usuario_previo": e_lc_usu, "lc_tipo_lente_ant": e_lc_tip,
                                                "lc_marca_ant": e_lc_mar, "lc_horas_uso": e_lc_hor,
                                                "lc_solucion_habitual": e_lc_sol, "lc_motivo_consulta": e_lc_mot,
                                                "lc_avsc_od": e_lc_avsc_od, "lc_avsc_oi": e_lc_avsc_oi,
                                                "lc_rx_od": constructed_rx_od, "lc_rx_oi": constructed_rx_oi,
                                                "lc_distancia_vertice": e_lc_dv,
                                                "lc_kera_od": constructed_kera_od, "lc_kera_oi": constructed_kera_oi,
                                                "lc_astig_corneal_od": e_ast_od, "lc_astig_corneal_oi": e_ast_oi,
                                                "lc_parpados": e_lc_par, "lc_conjuntiva": e_lc_con, "lc_eversion": e_lc_eve,
                                                "lc_cornea": e_lc_cor, "lc_but_od": e_lc_but_od, "lc_but_oi": e_lc_but_oi, "lc_menisco": e_lc_men,
                                                "lc_prueba_tipo": e_lc_pru_tip,
                                                "lc_prueba_od": constructed_prueba_od, "lc_prueba_oi": constructed_prueba_oi,
                                                "lc_centrado": e_lc_cen, "lc_movimiento": e_lc_mov, "lc_pushup": e_lc_pus, "lc_rotacion": e_lc_rot,
                                                "lc_sobre_od": constructed_sobre_od, "lc_sobre_oi": constructed_sobre_oi,
                                                "lc_final_od": constructed_final_od, "lc_final_oi": constructed_final_oi,
                                                "lc_marca_final": e_lc_mar_fin, "lc_modalidad": e_lc_mod, "lc_regimen": e_lc_reg,
                                                "lc_solucion_final": e_lc_sol_fin,
                                                "lc_insercion": e_lc_ins, "lc_fecha_entrega": str(e_lc_fent),
                                                "lc_proximo_control": e_lc_pcon, "lc_observaciones": e_lc_obs
                                            }
                                            if actualizar_historia_lc(hlc_id, datos_act):
                                                st.session_state[f"editando_lc_{hlc_id}"] = False
                                                from database import cargar_historias_lc
                                                st.session_state.df_historias_lc = cargar_historias_lc()
                                                st.success("✅ Cambios guardados correctamente.")
                                                st.rerun()
                                            else:
                                                st.error("Error al guardar en la base de datos.")
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
                _df_hlc = st.session_state.get("df_historias_lc", None)
                n_hist_lc = len(_df_hlc[
                    _df_hlc["paciente_id"].astype(str) == str(rp["id"])
                ]) if _df_hlc is not None and not _df_hlc.empty else 0

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
                if n_hist_lc > 0:
                    col_c.caption(f"👁️ Historias LC: {n_hist_lc}")
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


    # ── FORMULARIO NUEVA HISTORIA DE LENTES DE CONTACTO ────────────────────
    if st.session_state.get("nueva_lc_paciente"):
        pac_lc = st.session_state["nueva_lc_paciente"]
        nombre_lc = pac_lc["nombre"]
        id_lc     = pac_lc["id"]
        sucursal_actual = st.session_state.get("sucursal_activa", "Matriz")
        optometrista_actual = st.session_state.get("user_name", "")
        opto_login = st.session_state.get("user_login", "")

        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#2c1a0e,#7c3f00);border-radius:14px;
        padding:18px 24px;margin-bottom:14px;color:white;'>
            <h3 style='margin:0;font-size:1.15rem;'>👁️ Historia Clínica — Lentes de Contacto</h3>
            <p style='margin:4px 0 0 0;font-size:0.9rem;opacity:0.85;'>Paciente: <b>{nombre_lc}</b></p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("nueva_lc_form", clear_on_submit=True):
            lc_fecha = st.date_input("📅 Fecha de la Consulta", value=date.today())

            # ── BLOQUE 1: ANAMNESIS ─────────────────────────────────
            st.markdown("""
            <div style='background:linear-gradient(135deg,#fdf6ee,#f5e6cc);border:1px solid #d4a96a;
            border-radius:10px;padding:14px 18px;margin:10px 0 8px 0;'>
            <b style='color:#7c3f00;font-size:13px;text-transform:uppercase;letter-spacing:.06em;'>
            📝 Bloque 1 — Anamnesis Especializada</b></div>
            """, unsafe_allow_html=True)
            la1, la2 = st.columns(2)
            lc_usuario_previo = la1.selectbox("¿Usuario previo de LC?", ["", "Sí", "No"])
            lc_tipo_lente_ant = la2.selectbox("Tipo de lente anterior",
                ["", "Blando esférico", "Blando tórico", "Multifocal", "RGP", "Escleral", "Ninguno"])
            la3, la4 = st.columns(2)
            lc_marca_ant       = la3.text_input("Marca/Laboratorio anterior")
            lc_horas_uso       = la4.text_input("Horas de uso diario", placeholder="Ej: 8")
            la5, la6 = st.columns(2)
            lc_solucion_hab    = la5.selectbox("Solución de mantenimiento habitual",
                ["", "Solución multipropósito", "Peróxido de hidrógeno", "Jabón y agua (alerta)", "Ninguna"])
            lc_motivo_consulta = la6.selectbox("Motivo de la nueva consulta",
                ["", "Estética", "Deporte", "Renovación", "Incomodidad con los anteriores", "Queratocono", "Necesidad médica"])

            # ── BLOQUE 2: EXAMEN PRELIMINAR ──────────────────────────
            st.markdown("""
            <div style='background:linear-gradient(135deg,#fdf6ee,#f5e6cc);border:1px solid #d4a96a;
            border-radius:10px;padding:14px 18px;margin:10px 0 8px 0;'>
            <b style='color:#7c3f00;font-size:13px;text-transform:uppercase;letter-spacing:.06em;'>
            🔬 Bloque 2 — Examen Preliminar y Refracción</b></div>
            """, unsafe_allow_html=True)

            st.markdown("<small><b>AV Sin Corrección (S/C)</b></small>", unsafe_allow_html=True)
            lb1, lb2 = st.columns(2)
            lc_avsc_od = lb1.text_input("🟠 OD AV S/C", placeholder="20/200")
            lc_avsc_oi = lb2.text_input("🟤 OI AV S/C", placeholder="20/200")

            st.markdown("<small><b>Refracción Subjetiva Actual (Rx Gafas)</b></small>", unsafe_allow_html=True)
            lrx1,lrx2,lrx3,lrx4 = st.columns([0.15,1,1,1])
            lrx1.markdown("<p style='margin-top:28px'><b>🟠</b></p>", unsafe_allow_html=True)
            lc_rx_od_esf = lrx2.text_input("ESF OD"); lc_rx_od_cil = lrx3.text_input("CIL OD"); lc_rx_od_eje = lrx4.text_input("EJE OD")
            lrx5,lrx6,lrx7,lrx8 = st.columns([0.15,1,1,1])
            lrx5.markdown("<p style='margin-top:28px'><b>🟤</b></p>", unsafe_allow_html=True)
            lc_rx_oi_esf = lrx6.text_input("ESF OI"); lc_rx_oi_cil = lrx7.text_input("CIL OI"); lc_rx_oi_eje = lrx8.text_input("EJE OI")

            lc_rx_od = f"{lc_rx_od_esf} / {lc_rx_od_cil} x {lc_rx_od_eje}"
            lc_rx_oi = f"{lc_rx_oi_esf} / {lc_rx_oi_cil} x {lc_rx_oi_eje}"

            lb3 = st.text_input("📐 Distancia al Vértice (DV en mm)", placeholder="Ej: 12 mm")
            lc_distancia_vertice = lb3

            st.markdown("<small><b>Queratometría / Topografía</b></small>", unsafe_allow_html=True)
            lk1,lk2,lk3,lk4 = st.columns([0.15,1,1,1])
            lk1.markdown("<p style='margin-top:28px'><b>🟠</b></p>", unsafe_allow_html=True)
            lk_od_plana = lk2.text_input("K Plana OD"); lk_od_curva = lk3.text_input("K Curva OD"); lk_od_eje = lk4.text_input("Eje OD")
            lk5,lk6,lk7,lk8 = st.columns([0.15,1,1,1])
            lk5.markdown("<p style='margin-top:28px'><b>🟤</b></p>", unsafe_allow_html=True)
            lk_oi_plana = lk6.text_input("K Plana OI"); lk_oi_curva = lk7.text_input("K Curva OI"); lk_oi_eje = lk8.text_input("Eje OI")
            lc_kera_od = f"{lk_od_plana} / {lk_od_curva} @ {lk_od_eje}"
            lc_kera_oi = f"{lk_oi_plana} / {lk_oi_curva} @ {lk_oi_eje}"

            las1, las2 = st.columns(2)
            lc_astig_corneal_od = las1.text_input("⚪ Astigmatismo Corneal OD (D)")
            lc_astig_corneal_oi = las2.text_input("⚪ Astigmatismo Corneal OI (D)")

            # ── BLOQUE 3: BIOMICROSCOPÍA ────────────────────────────
            st.markdown("""
            <div style='background:linear-gradient(135deg,#fdf6ee,#f5e6cc);border:1px solid #d4a96a;
            border-radius:10px;padding:14px 18px;margin:10px 0 8px 0;'>
            <b style='color:#7c3f00;font-size:13px;text-transform:uppercase;letter-spacing:.06em;'>
            🔬 Bloque 3 — Evaluación de la Salud Ocular (Biomicroscopía)</b></div>
            """, unsafe_allow_html=True)
            lm1, lm2 = st.columns(2)
            lc_parpados   = lm1.selectbox("👁️ Párpados / Glándulas de Meibomio",
                ["", "Normal", "Disfunción leve", "Disfunción severa", "Blefaritis"])
            lc_conjuntiva = lm2.selectbox("Conjuntiva (Hiperemia)",
                ["", "Grado 0 (Ninguna)", "Grado 1 (Leve)", "Grado 2 (Moderada)", "Grado 3 (Severa)"])
            lm3, lm4 = st.columns(2)
            lc_eversion   = lm3.selectbox("Eversión Palpebral (Papilas)",
                ["", "Ausentes", "Leves", "Conjuntivitis Papilar Gigante (GPC)"])
            lc_cornea     = lm4.selectbox("Córnea (Tinc. Fluoresceína)",
                ["", "Grado 0 (Limpia)", "Grado 1 (Punteado leve)", "Grado 2 (Tinc. confluente)", "Grado 3 (Úlcera/Infiltrado)"])
            lm5, lm6, lm7 = st.columns(3)
            lc_but_od = lm5.text_input("BUT OD (seg)", placeholder="> 10 seg")
            lc_but_oi = lm6.text_input("BUT OI (seg)", placeholder="> 10 seg")
            lc_menisco = lm7.selectbox("Menisco Lagrimal", ["", "Normal", "Alto", "Escaso"])

            # ── BLOQUE 4: LENTE DE PRUEBA ────────────────────────────
            st.markdown("""
            <div style='background:linear-gradient(135deg,#fdf6ee,#f5e6cc);border:1px solid #d4a96a;
            border-radius:10px;padding:14px 18px;margin:10px 0 8px 0;'>
            <b style='color:#7c3f00;font-size:13px;text-transform:uppercase;letter-spacing:.06em;'>
            🔄 Bloque 4 — Registro de Pruebas (Lente de Prueba)</b></div>
            """, unsafe_allow_html=True)
            lc_prueba_tipo = st.selectbox("Tipo de Lente de Prueba",
                ["", "Blando Hidrogel", "Hidrogel de Silicona", "RGP", "Escleral"])

            st.markdown("<small><b>Parámetros del Lente de Prueba</b></small>", unsafe_allow_html=True)
            lp1,lp2,lp3,lp4,lp5 = st.columns([0.15,1,1,1,1])
            lp1.markdown("<p style='margin-top:28px'><b>🟠</b></p>", unsafe_allow_html=True)
            lp_od_bc=lp2.text_input("BC OD"); lp_od_td=lp3.text_input("TD OD"); lp_od_esf=lp4.text_input("Esf OD"); lp_od_cil=lp5.text_input("Cil OD")
            lp6,lp7,lp8,lp9,lp10 = st.columns([0.15,1,1,1,1])
            lp6.markdown("<p style='margin-top:28px'><b>🟤</b></p>", unsafe_allow_html=True)
            lp_oi_bc=lp7.text_input("BC OI"); lp_oi_td=lp8.text_input("TD OI"); lp_oi_esf=lp9.text_input("Esf OI"); lp_oi_cil=lp10.text_input("Cil OI")
            lc_prueba_od = f"BC:{lp_od_bc} TD:{lp_od_td} {lp_od_esf}/{lp_od_cil}"
            lc_prueba_oi = f"BC:{lp_oi_bc} TD:{lp_oi_td} {lp_oi_esf}/{lp_oi_cil}"

            le1, le2, le3, le4 = st.columns(4)
            lc_centrado  = le1.selectbox("Centrado", ["", "Centrado", "Descentrado Sup.", "Descentrado Inf.", "Descentrado Nasal", "Descentrado Temporal"])
            lc_movimiento= le2.selectbox("Movimiento al parpadeo", ["", "Adecuado (0.5-1mm)", "Escaso (apretado)", "Excesivo (flojo)"])
            lc_pushup    = le3.selectbox("Push-up Test", ["", "Positiva (Aceptable)", "Negativa (Muy apretado)"])
            lc_rotacion  = le4.text_input("Rotación de eje (°)", placeholder="0° o grados")

            st.markdown("<small><b>Sobrerrefracción (Over-Refraction)</b></small>", unsafe_allow_html=True)
            ls1,ls2,ls3,ls4 = st.columns([0.15,1,1,1])
            ls1.markdown("<p style='margin-top:28px'><b>🟠</b></p>", unsafe_allow_html=True)
            ls_od_esf=ls2.text_input("SR Esf OD"); ls_od_cil=ls3.text_input("SR Cil OD"); ls_od_av=ls4.text_input("AV lograda OD")
            ls5,ls6,ls7,ls8 = st.columns([0.15,1,1,1])
            ls5.markdown("<p style='margin-top:28px'><b>🟤</b></p>", unsafe_allow_html=True)
            ls_oi_esf=ls6.text_input("SR Esf OI"); ls_oi_cil=ls7.text_input("SR Cil OI"); ls_oi_av=ls8.text_input("AV lograda OI")
            lc_sobre_od = f"{ls_od_esf}/{ls_od_cil} AV:{ls_od_av}"
            lc_sobre_oi = f"{ls_oi_esf}/{ls_oi_cil} AV:{ls_oi_av}"

            # ── BLOQUE 5: LENTE DEFINITIVO ───────────────────────────
            st.markdown("""
            <div style='background:linear-gradient(135deg,#fdf6ee,#f5e6cc);border:1px solid #d4a96a;
            border-radius:10px;padding:14px 18px;margin:10px 0 8px 0;'>
            <b style='color:#7c3f00;font-size:13px;text-transform:uppercase;letter-spacing:.06em;'>
            ✔️ Bloque 5 — Diagnóstico y Lente Definitivo</b></div>
            """, unsafe_allow_html=True)

            st.markdown("<small><b>Lente Final Autorizado</b></small>", unsafe_allow_html=True)
            lf1,lf2,lf3,lf4,lf5,lf6 = st.columns([0.15,1,1,1,1,1])
            lf1.markdown("<p style='margin-top:28px'><b>🟠</b></p>", unsafe_allow_html=True)
            lf_od_bc=lf2.text_input("BC OD "); lf_od_td=lf3.text_input("TD OD "); lf_od_esf=lf4.text_input("Esf OD "); lf_od_cil=lf5.text_input("Cil OD "); lf_od_add=lf6.text_input("Add OD")
            lf7,lf8,lf9,lf10,lf11,lf12 = st.columns([0.15,1,1,1,1,1])
            lf7.markdown("<p style='margin-top:28px'><b>🟤</b></p>", unsafe_allow_html=True)
            lf_oi_bc=lf8.text_input("BC OI "); lf_oi_td=lf9.text_input("TD OI "); lf_oi_esf=lf10.text_input("Esf OI "); lf_oi_cil=lf11.text_input("Cil OI "); lf_oi_add=lf12.text_input("Add OI")
            lc_final_od = f"BC:{lf_od_bc} TD:{lf_od_td} {lf_od_esf}/{lf_od_cil} Add:{lf_od_add}"
            lc_final_oi = f"BC:{lf_oi_bc} TD:{lf_oi_td} {lf_oi_esf}/{lf_oi_cil} Add:{lf_oi_add}"

            lf13, lf14, lf15, lf16 = st.columns(4)
            lc_marca_final  = lf13.text_input("Marca / Laboratorio")
            lc_modalidad    = lf14.selectbox("Modalidad de Reemplazo",
                ["", "Diario", "Quincenal", "Mensual", "Trimestral", "Anual"])
            lc_regimen      = lf15.selectbox("Régimen de Uso",
                ["", "Uso diario (se los quita para dormir)", "Uso prolongado"])
            lc_solucion_final = lf16.text_input("Solución Recomendada")

            # ── BLOQUE 6: ENTREGA Y EDUCACIÓN ───────────────────────
            st.markdown("""
            <div style='background:linear-gradient(135deg,#fdf6ee,#f5e6cc);border:1px solid #d4a96a;
            border-radius:10px;padding:14px 18px;margin:10px 0 8px 0;'>
            <b style='color:#7c3f00;font-size:13px;text-transform:uppercase;letter-spacing:.06em;'>
            🏥 Bloque 6 — Entrega, Educación y Controles</b></div>
            """, unsafe_allow_html=True)
            lg1, lg2 = st.columns(2)
            lc_insercion      = lg1.selectbox("Enseñado Inserción/Remoción",
                ["", "Aprobado", "Requiere más práctica"])
            lc_fecha_entrega  = lg2.date_input("Fecha de Entrega", value=date.today())
            lc_proximo_control= st.selectbox("Cronograma Próximos Controles",
                ["", "1 semana", "1 mes", "6 meses", "1 año"])
            lc_observaciones  = st.text_area("Observaciones / Evolución en controles",
                placeholder="Anotar cómo regresa en el control, tinc. corneal tardía, queja de resequedad, etc.")

            # Botón guardar
            flc1, flc2 = st.columns(2)
            if flc1.form_submit_button("💾 Guardar Historia LC", use_container_width=True, type="primary"):
                payload = {
                    "paciente_id":       str(id_lc),
                    "paciente_nombre":   nombre_lc,
                    "fecha":             str(lc_fecha),
                    "sucursal":          sucursal_actual,
                    "optometrista":      optometrista_actual,
                    "optometrista_login":opto_login,
                    "lc_usuario_previo": lc_usuario_previo,
                    "lc_tipo_lente_ant": lc_tipo_lente_ant,
                    "lc_marca_ant":      lc_marca_ant,
                    "lc_horas_uso":      lc_horas_uso,
                    "lc_solucion_habitual": lc_solucion_hab,
                    "lc_motivo_consulta":lc_motivo_consulta,
                    "lc_avsc_od":        lc_avsc_od,
                    "lc_avsc_oi":        lc_avsc_oi,
                    "lc_rx_od":          lc_rx_od,
                    "lc_rx_oi":          lc_rx_oi,
                    "lc_distancia_vertice": lc_distancia_vertice,
                    "lc_kera_od":        lc_kera_od,
                    "lc_kera_oi":        lc_kera_oi,
                    "lc_astig_corneal_od": lc_astig_corneal_od,
                    "lc_astig_corneal_oi": lc_astig_corneal_oi,
                    "lc_parpados":       lc_parpados,
                    "lc_conjuntiva":     lc_conjuntiva,
                    "lc_eversion":       lc_eversion,
                    "lc_cornea":         lc_cornea,
                    "lc_but_od":         lc_but_od,
                    "lc_but_oi":         lc_but_oi,
                    "lc_menisco":        lc_menisco,
                    "lc_prueba_tipo":    lc_prueba_tipo,
                    "lc_prueba_od":      lc_prueba_od,
                    "lc_prueba_oi":      lc_prueba_oi,
                    "lc_centrado":       lc_centrado,
                    "lc_movimiento":     lc_movimiento,
                    "lc_pushup":         lc_pushup,
                    "lc_rotacion":       lc_rotacion,
                    "lc_sobre_od":       lc_sobre_od,
                    "lc_sobre_oi":       lc_sobre_oi,
                    "lc_final_od":       lc_final_od,
                    "lc_final_oi":       lc_final_oi,
                    "lc_marca_final":    lc_marca_final,
                    "lc_modalidad":      lc_modalidad,
                    "lc_regimen":        lc_regimen,
                    "lc_solucion_final": lc_solucion_final,
                    "lc_insercion":      lc_insercion,
                    "lc_fecha_entrega":  str(lc_fecha_entrega),
                    "lc_proximo_control":lc_proximo_control,
                    "lc_observaciones":  lc_observaciones,
                }
                ok = guardar_historia_lc(payload)
                if ok:
                    from database import cargar_historias_lc
                    st.session_state.df_historias_lc = cargar_historias_lc()
                    st.session_state["nueva_lc_paciente"] = None
                    st.success(f"✅ Historia de Lentes de Contacto guardada para {nombre_lc}")
                    st.rerun()
                else:
                    st.error("❌ Error al guardar. Verifica que ejecutaste el SQL en Supabase.")
            if flc2.form_submit_button("❌ Cancelar", use_container_width=True):
                st.session_state["nueva_lc_paciente"] = None
                st.rerun()

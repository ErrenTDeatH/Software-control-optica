import streamlit as st
import pandas as pd
import re
from datetime import datetime
from database import supabase, registrar_auditoria, cargar_ordenes_trabajo
from fpdf import FPDF

def parse_rx_string(rx_str):
    if not rx_str or not isinstance(rx_str, str) or rx_str.strip() == "":
        return {"Esfera": "", "Cilindro": "", "Eje": ""}
    rx_str = rx_str.replace(",", ".").replace("X", "x").strip()
    parts = re.findall(r'[+-]?\d*\.?\d+', rx_str)
    res = {"Esfera": "", "Cilindro": "", "Eje": ""}
    if len(parts) >= 1: res["Esfera"] = parts[0]
    if len(parts) >= 2: res["Cilindro"] = parts[1]
    if len(parts) >= 3: res["Eje"] = parts[2]
    return res

def generar_pdf_orden(data, order_id="N/A"):
    pdf = FPDF()
    pdf.add_page()
    
    # Logo más grande
    try:
        pdf.image("logo.png", 10, 8, 45)
    except:
        pass
        
    # Encabezado con Número de Orden
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, f"ORDEN DE TRABAJO #{order_id}", ln=True, align='R')
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "HAPPY VISION", ln=True, align='R')
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 10, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='R')
    pdf.ln(15)
    
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f" PACIENTE: {data['paciente_nombre']}", ln=True, fill=True)
    pdf.ln(2)
    
    # Cuadro de Medidas
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(40, 8, "OJO", 1, 0, 'C', True)
    pdf.cell(30, 8, "ESFERA", 1, 0, 'C', True)
    pdf.cell(30, 8, "CILINDRO", 1, 0, 'C', True)
    pdf.cell(30, 8, "EJE", 1, 0, 'C', True)
    pdf.cell(30, 8, "ADICION", 1, 0, 'C', True)
    pdf.cell(30, 8, "A.V.", 1, 1, 'C', True)
    
    pdf.set_font("Arial", '', 11)
    od = data.get('receta_od')
    oi = data.get('receta_oi')
    if not isinstance(od, dict): od = {}
    if not isinstance(oi, dict): oi = {}
    pdf.cell(40, 8, "DERECHO (OD)", 1)
    pdf.cell(30, 8, str(od.get('Esf','')), 1, 0, 'C')
    pdf.cell(30, 8, str(od.get('Cil','')), 1, 0, 'C')
    pdf.cell(30, 8, str(od.get('Eje','')), 1, 0, 'C')
    pdf.cell(30, 8, str(od.get('Add','')), 1, 0, 'C')
    pdf.cell(30, 8, str(od.get('AV','')), 1, 1, 'C')
    
    pdf.cell(40, 8, "IZQUIERDO (OI)", 1)
    pdf.cell(30, 8, str(oi.get('Esf','')), 1, 0, 'C')
    pdf.cell(30, 8, str(oi.get('Cil','')), 1, 0, 'C')
    pdf.cell(30, 8, str(oi.get('Eje','')), 1, 0, 'C')
    pdf.cell(30, 8, str(oi.get('Add','')), 1, 0, 'C')
    pdf.cell(30, 8, str(oi.get('AV','')), 1, 1, 'C')
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 11); pdf.cell(0, 8, "DETALLES TÉCNICOS", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(90, 8, f"D.I.P: {data['dip']}", 0, 0); pdf.cell(90, 8, f"Altura Focal: {data['altura']}", 0, 1)
    pdf.cell(90, 8, f"Tipo Lente: {data['tipo_lente']}", 0, 0); pdf.cell(90, 8, f"Material: {data['material']}", 0, 1)
    pdf.ln(2); pdf.multi_cell(0, 8, f"Tratamientos: {data['protecciones']}")
    pdf.ln(2); pdf.set_font("Arial", 'B', 11); pdf.cell(0, 8, "Observaciones:", ln=True)
    pdf.set_font("Arial", '', 11); pdf.multi_cell(0, 8, str(data.get('observaciones') or ""))
    
    out = pdf.output(dest='S')
    if isinstance(out, str):
        return out.encode('latin-1')
    return bytes(out)

def render_nueva_orden():
    st.markdown("""<div class="page-header"><h1>📝 Gestión de Órdenes</h1><p>Centro técnico para la elaboración de lunas y montajes</p></div>""", unsafe_allow_html=True)
    tab_n, tab_h = st.tabs(["➕ Nueva Orden", "🔍 Historial"])

    with tab_n:
        st.markdown("<div class='section-title'>👤 Datos del Paciente</div>", unsafe_allow_html=True)
        pacientes_dict = {}
        pacientes_nombres = {}
        try:
            res_p = supabase.table("pacientes").select("id, nombres, apellidos, identificacion").execute()
            if res_p.data:
                df_p = pd.DataFrame(res_p.data)
                df_p["display"] = df_p["nombres"] + " " + df_p["apellidos"] + " (" + df_p["identificacion"] + ")"
                busc = st.text_input("🔍 Buscar paciente:", key="busc_orden")
                if busc: df_p = df_p[df_p["display"].str.contains(busc, case=False)]
                pacientes_dict = dict(zip(df_p["id"], df_p["display"]))
                pacientes_nombres = dict(zip(df_p["id"], df_p["nombres"] + " " + df_p["apellidos"]))
        except: pass

        paciente_id = st.selectbox("Confirmar Paciente:", options=list(pacientes_dict.keys()), format_func=lambda x: pacientes_dict.get(x, ""))
        
        rx_od_v = {"Esfera": "", "Cilindro": "", "Eje": "", "Adición": "", "A.V.": ""}
        rx_oi_v = {"Esfera": "", "Cilindro": "", "Eje": "", "Adición": "", "A.V.": ""}
        dip_v = ""; p_key = f"ord_{paciente_id}"

        if paciente_id:
            try:
                res_h = supabase.table("historias_clinicas").select("*").eq("paciente_id", paciente_id).order("fecha", desc=True).limit(1).execute()
                if res_h.data:
                    h = res_h.data[0]
                    p_od = parse_rx_string(h.get("rx_od", "")); p_oi = parse_rx_string(h.get("rx_oi", ""))
                    rx_od_v.update(p_od); rx_oi_v.update(p_oi)
                    rx_od_v["A.V."] = h.get("rx_av_lej_od", ""); rx_oi_v["A.V."] = h.get("rx_av_lej_oi", "")
                    rx_od_v["Adición"] = h.get("rx_add", ""); rx_oi_v["Adición"] = h.get("rx_add", "")
                    dip_v = h.get("rx_dip", "")
                    st.success(f"✅ Medidas cargadas de la historia clínica.")
            except: pass

        st.divider()
        st.markdown("<div class='section-title'>📋 Cuadro de Medidas</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("OD")
            o_esf = st.text_input("Esf (OD)", value=str(rx_od_v["Esfera"]), key=f"esf_od_{p_key}")
            o_cil = st.text_input("Cil (OD)", value=str(rx_od_v["Cilindro"]), key=f"cil_od_{p_key}")
            o_eje = st.text_input("Eje (OD)", value=str(rx_od_v["Eje"]), key=f"eje_od_{p_key}")
            o_add = st.text_input("Add (OD)", value=str(rx_od_v["Adición"]), key=f"add_od_{p_key}")
            o_av  = st.text_input("AV (OD)", value=str(rx_od_v["A.V."]), key=f"av_od_{p_key}")
        with c2:
            st.subheader("OI")
            i_esf = st.text_input("Esf (OI)", value=str(rx_oi_v["Esfera"]), key=f"esf_oi_{p_key}")
            i_cil = st.text_input("Cil (OI)", value=str(rx_oi_v["Cilindro"]), key=f"cil_oi_{p_key}")
            i_eje = st.text_input("Eje (OI)", value=str(rx_oi_v["Eje"]), key=f"eje_oi_{p_key}")
            i_add = st.text_input("Add (OI)", value=str(rx_oi_v["Adición"]), key=f"add_oi_{p_key}")
            i_av  = st.text_input("AV (OI)", value=str(rx_oi_v["A.V."]), key=f"av_oi_{p_key}")

        st.divider()
        d1, d2, d3 = st.columns(3)
        dip = d1.text_input("D.I.P.", value=str(dip_v), key=f"dip_{p_key}")
        altura = d2.text_input("Altura Focal", key=f"alt_{p_key}")
        tipo = d3.selectbox("Lente", ["Monofocal", "Bifocal", "Progresivo"], key=f"tipo_{p_key}")
        m1, m2 = st.columns(2)
        material = m1.multiselect("Material", ["CR-39", "Policarbonato", "Alto Índice", "Transitions"], key=f"mat_{p_key}")
        protecciones = m2.multiselect("Tratamientos", ["Antirreflejo", "Blue Defense", "Hidrofóbico"], key=f"prot_{p_key}")
        obs = st.text_area("Observaciones", key=f"obs_{p_key}")

        col_btn1, col_btn2 = st.columns([1, 1])
        if f"saved_{p_key}" not in st.session_state: st.session_state[f"saved_{p_key}"] = False

        with col_btn1:
            if st.button("💾 GUARDAR ORDEN", type="primary", use_container_width=True):
                if not paciente_id: st.error("⚠️ Elija un paciente.")
                else:
                    # CÁLCULO DE ID SECUENCIAL INTELIGENTE
                    try:
                        res_max = supabase.table("ordenes_trabajo").select("id").order("id", desc=True).limit(1).execute()
                        max_id = res_max.data[0]['id'] if res_max.data else 0
                        nuevo_id = int(max_id) + 1
                    except:
                        nuevo_id = 1

                    nueva = {
                        "id": nuevo_id,
                        "paciente_id": paciente_id, "paciente_nombre": pacientes_nombres[paciente_id],
                        "receta_od": {"Esf": o_esf, "Cil": o_cil, "Eje": o_eje, "Add": o_add, "AV": o_av},
                        "receta_oi": {"Esf": i_esf, "Cil": i_cil, "Eje": i_eje, "Add": i_add, "AV": i_av},
                        "dip": dip, "altura": altura, "tipo_lente": tipo,
                        "material": ", ".join(material), "protecciones": ", ".join(protecciones),
                        "observaciones": obs, "estado": "Pendiente",
                        "sucursal": st.session_state.get("sucursal_activa"),
                        "creado_por": st.session_state.get("user_login"), "creado_el": datetime.now().isoformat()
                    }
                    try:
                        res = supabase.table("ordenes_trabajo").insert(nueva).execute()
                        st.session_state[f"saved_{p_key}"] = True
                        st.session_state[f"order_id_{p_key}"] = nuevo_id
                        st.session_state[f"pdf_data_{p_key}"] = nueva
                        st.success(f"✅ Orden #{nuevo_id} guardada.")
                    except Exception as e: st.error(f"Error: {e}")

        with col_btn2:
            if st.session_state.get(f"saved_{p_key}"):
                oid = st.session_state.get(f"order_id_{p_key}", "N/A")
                pdata = st.session_state.get(f"pdf_data_{p_key}")
                if pdata:
                    pdf_bytes = generar_pdf_orden(pdata, oid)
                    st.download_button(
                        label=f"📄 DESCARGAR PDF #{oid}",
                        data=pdf_bytes,
                        file_name=f"Orden_{oid}_{pacientes_nombres.get(paciente_id, 'Orden').replace(' ','_')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            else:
                st.button("📄 DESCARGAR PDF", disabled=True, use_container_width=True)

    with tab_h:
        st.markdown("<div class='section-title'>🔍 Historial</div>", unsafe_allow_html=True)
        df_ord = cargar_ordenes_trabajo(st.session_state.get("sucursal_activa"))
        if not df_ord.empty:
            for _, r in df_ord.iterrows():
                with st.expander(f"📄 #{r['id']} - {r['paciente_nombre']} ({r['creado_el'][:10]})"):
                    rod = r.get("receta_od"); roi = r.get("receta_oi")
                    if not isinstance(rod, dict): rod = {}
                    if not isinstance(roi, dict): roi = {}
                    st.write(f"**OD:** {rod.get('Esf','')} {rod.get('Cil','')} x {rod.get('Eje','')}")
                    st.write(f"**OI:** {roi.get('Esf','')} {roi.get('Cil','')} x {roi.get('Eje','')}")
                    st.info(f"Estado: {r['estado']}")
                    
                    # DESCARGAR DESDE EL HISTORIAL
                    pdf_h = generar_pdf_orden(r, r['id'])
                    st.download_button(
                        label=f"📥 Descargar PDF #{r['id']}",
                        data=pdf_h,
                        file_name=f"Orden_{r['id']}_{r['paciente_nombre'].replace(' ','_')}.pdf",
                        mime="application/pdf",
                        key=f"dl_h_{r['id']}",
                        use_container_width=True
                    )
                    
                    # SOLO EL ADMIN PUEDE ELIMINAR
                    if st.session_state.get("user_role") == "Administrador":
                        if st.button(f"🗑️ Eliminar #{r['id']}", key=f"del_{r['id']}"):
                            supabase.table("ordenes_trabajo").delete().eq("id", r['id']).execute()
                            st.rerun()

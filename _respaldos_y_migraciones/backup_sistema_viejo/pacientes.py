import streamlit as st
import pandas as pd
from datetime import date
from utils import guardar_datos
from database import eliminar_paciente


def render_pacientes():
    st.markdown("""
    <div class="page-header">
        <h1>👥 Registro de Pacientes</h1>
        <p>Directorio completo de pacientes ordenado alfabeticamente por apellidos</p>
    </div>
    """, unsafe_allow_html=True)

    # FILTRAR POR SUCURSAL ACTIVA
    sucursal_actual = st.session_state.get("sucursal_activa", "Matriz")
    
    # Filtrar solo si no es Administrador Global "Admin"
    # Si quisieramos que admin viera todo junto, podríamos saltar el filtro, pero para separar 
    # la info por local es mejor que el admin también trabaje en una sucursal a la vez.
    if "sucursal" in st.session_state.df_pacientes.columns:
        df_p_page = st.session_state.df_pacientes[st.session_state.df_pacientes["sucursal"] == sucursal_actual].copy()
    else:
        df_p_page = st.session_state.df_pacientes.copy()
        
    if "sucursal" in st.session_state.df_historias.columns:
        df_h_page = st.session_state.df_historias[st.session_state.df_historias["sucursal"] == sucursal_actual].copy()
    else:
        df_h_page = st.session_state.df_historias.copy()

    # ── FORMULARIO AGREGAR PACIENTE (arriba del listado) ──────────────
    with st.expander("➕ Agregar Nuevo Paciente", expanded=False):
        with st.form("form_nuevo_pac_page", clear_on_submit=True):
            fc1, fc2, fc3, fc4 = st.columns([1, 1.5, 1.5, 1])
            np_id       = fc1.text_input("Cedula / ID")
            np_nombres  = fc2.text_input("Nombres *")
            np_apellidos= fc3.text_input("Apellidos *")
            np_gen      = fc4.selectbox("Genero", ["Masculino", "Femenino", "Otro"])
            fc5, fc6, fc7 = st.columns([1.5, 1, 1.5])
            np_fnac = fc5.date_input("Fecha de Nacimiento", value=date(1990,1,1), min_value=date(1900,1,1), max_value=date.today(), help="Si no la conoces, usa el campo de Edad a la derecha.")
            np_edad_input = fc6.number_input("O Edad (Años)", min_value=0, max_value=120, value=0, help="Ingresa la edad si no conoces la fecha de nacimiento.")
            np_tel  = fc7.text_input("Telefono")
            
            fc8, fc9, fc10 = st.columns([1.5, 1.5, 1])
            np_cor = fc8.text_input("Correo")
            np_ocu = fc9.text_input("Ocupacion")
            np_dir = fc10.text_input("Direccion")
            if st.form_submit_button("Registrar Paciente", type="primary", use_container_width=True):
                # Limpieza de datos de entrada
                id_input = str(np_id).strip()
                nom_input = np_nombres.strip()
                ape_input = np_apellidos.strip()
                nombre_completo_input = f"{ape_input} {nom_input}"

                # 1. Validaciones básicas
                if not nom_input or not ape_input:
                    st.warning("⚠️ Nombres y Apellidos son obligatorios.")
                
                else:
                    # 2. Verificar duplicados de forma robusta (Directo en DB para máxima seguridad)
                    from database import supabase
                    id_limpia = id_input.strip()
                    
                    existe_en_db = False
                    if id_limpia and supabase:
                        try:
                            # Buscamos en la base de datos si ya existe esa cédula EN CUALQUIER SUCURSAL
                            check_db = supabase.table("pacientes").select("id, nombre, sucursal").eq("identificacion", id_limpia).execute()
                            if check_db.data:
                                existe_en_db = True
                                nombre_existente = check_db.data[0].get("nombre", "Desconocido")
                                sucursal_existente = check_db.data[0].get("sucursal", "otra sucursal")
                        except:
                            # Si falla la red, usamos la caché local como respaldo
                            ids_locales = st.session_state.df_pacientes["identificacion"].astype(str).str.strip().tolist()
                            if id_limpia in ids_locales:
                                existe_en_db = True
                                nombre_existente = "Caché local"
                                sucursal_existente = "Desconocida"

                    if existe_en_db:
                        st.error(f"🚫 ERROR CRÍTICO: El paciente con cédula **{id_limpia}** ya está registrado como **{nombre_existente}** en la **{sucursal_existente}**. No se permiten duplicados.")
                        st.stop()
                    
                    # 3. Verificar nombres similares (Advertencia)
                    nombres_existentes = df_p_page["nombre"].str.strip().str.lower().tolist()
                    if nombre_completo_input.lower() in nombres_existentes:
                        st.warning(f"⚠️ AVISO: Ya existe un paciente con el nombre '{nombre_completo_input}' en esta sucursal.")
                        if not st.checkbox("Confirmar que es una persona diferente (mismo nombre, distinta cédula)", key="confirm_homonimo"):
                            st.stop()
                    
                    # 3. Guardar si todo está bien
                    df_p = st.session_state.df_pacientes
                    hoy = date.today()
                    
                    # Priorizar edad manual si se ingresó
                    if np_edad_input > 0:
                        edad_calc = np_edad_input
                        fnac_final = "" # No hay fecha exacta
                    else:
                        edad_calc = hoy.year - np_fnac.year - ((hoy.month, hoy.day) < (np_fnac.month, np_fnac.day))
                        fnac_final = np_fnac.strftime("%Y-%m-%d")
                    
                    # Calcular el nuevo ID de forma segura
                    if not df_p.empty and "id" in df_p.columns:
                        max_id = pd.to_numeric(df_p["id"], errors="coerce").max()
                        nuevo_id = int(max_id + 1) if pd.notna(max_id) else 1
                    else:
                        nuevo_id = 1

                    nuevo_p = {
                        "id": nuevo_id,
                        "identificacion": id_input, 
                        "nombre": nombre_completo_input,
                        "nombres": nom_input, 
                        "apellidos": ape_input,
                        "genero": np_gen, 
                        "edad": str(edad_calc),
                        "fecha_nacimiento": fnac_final,
                        "telefono": np_tel.strip(), 
                        "correo": np_cor.strip(),
                        "ocupacion": np_ocu.strip(), 
                        "direccion": np_dir.strip(),
                        "sucursal": sucursal_actual
                    }
                    st.session_state.df_pacientes = pd.concat(
                        [st.session_state.df_pacientes, pd.DataFrame([nuevo_p])], ignore_index=True
                    )
                    guardar_datos()
                    st.success(f"✅ Paciente **{nombre_completo_input}** registrado correctamente.")
                    st.rerun()

    st.markdown("---")

    # ── BUSCADOR ──────────────────────────────────────────────────────
    busq_p = st.text_input("Buscar por apellido, nombre o cedula:", placeholder="Escribe para filtrar...")

    if busq_p:
        mask_p = (
            df_p_page["nombre"].str.contains(busq_p, case=False, na=False) |
            df_p_page["identificacion"].astype(str).str.contains(busq_p, case=False, na=False) |
            (df_p_page.get("apellidos", df_p_page["nombre"]).astype(str).str.contains(busq_p, case=False, na=False))
        )
        df_vista = df_p_page[mask_p]
    else:
        # Orden alfabetico por apellidos, luego por nombres
        if "apellidos" in df_p_page.columns:
            df_vista = df_p_page.sort_values(
                by=["apellidos", "nombres"],
                key=lambda c: c.astype(str).str.upper().str.strip(),
                ascending=True
            )
        else:
            df_vista = df_p_page.sort_values(
                by="nombre",
                key=lambda c: c.astype(str).str.upper().str.strip(),
                ascending=True
            )

    # ── LISTADO DE PACIENTES ──────────────────────────────────────────
    if len(df_vista) == 0:
        st.info("No se encontraron pacientes.")
    else:
        st.markdown(f"**{len(df_vista)} paciente(s) registrado(s)**")
        for _, prow in df_vista.iterrows():
            n_hist = len(df_h_page[df_h_page["paciente_id"].astype(str) == str(prow["id"])])

            # Mostrar: Apellidos, Nombres
            _apellidos = str(prow.get("apellidos", "")).strip()
            _nombres   = str(prow.get("nombres", "")).strip()
            if _apellidos and _nombres:
                display_name = f"{_apellidos} {_nombres}"
            else:
                display_name = str(prow.get("nombre", ""))

            col_num, col_a, col_b, col_c, col_d, col_e, col_f = st.columns([0.5, 3, 2, 1.8, 0.7, 1.4, 0.6])
            col_num.markdown(
                f"<div style='text-align:center;'>"
                f"<span style='color:#93c5fd;font-size:18px;font-weight:800;'>"
                f"{prow.get('id','')}</span></div>",
                unsafe_allow_html=True
            )
            col_a.markdown(f"**{display_name}**")
            col_b.caption(f"ID {prow.get('identificacion','')}")
            col_c.caption(f"Tel: {prow.get('telefono','')}")
            col_d.caption(f"{n_hist} HC")
            if col_e.button("📋 Ver HC", key=f"verac_{prow['id']}", use_container_width=True):
                st.session_state.page = "Clinica"
                st.session_state["clinica_buscar"] = str(prow.get("nombre", ""))
                st.rerun()
            
            with col_f:
                if st.button("🗑️", key=f"del_p_{prow['id']}", help="Eliminar paciente permanentemente"):
                    if n_hist > 0:
                        st.error(f"No puedes eliminar a este paciente porque tiene {n_hist} historias clínicas. Debes borrarlas primero.")
                    else:
                        eliminar_paciente(prow['id'])
                        st.session_state.df_pacientes = st.session_state.df_pacientes[
                            st.session_state.df_pacientes["id"] != prow["id"]
                        ]
                        st.success("Paciente eliminado.")
                        st.rerun()
            st.divider()

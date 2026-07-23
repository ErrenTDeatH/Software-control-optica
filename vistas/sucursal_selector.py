import streamlit as st
from database import cargar_sucursales

def render_sucursal_selector():
    """Renders the branch selection screen."""
    # Forzar que el Administrador siempre vea todas las sedes reales
    if "Administrador" in st.session_state.get("user_role", ""):
        df_s = cargar_sucursales()
        if not df_s.empty:
            st.session_state.sucursales_asignadas = df_s["nombre"].tolist()
        else:
            st.session_state.sucursales_asignadas = ["Matriz"]

    if st.session_state.get("logged_in") and not st.session_state.get("sucursal_activa"):
        st.markdown("<h2 style='text-align: center; margin-top: 10vh; color: #1e293b; font-weight: 800;'>🏢 Selecciona tu Entorno de Trabajo</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b; margin-bottom: 5vh;'>Haz clic en el cuadro de la óptica a la que deseas acceder</p>", unsafe_allow_html=True)
        
        sucursales = st.session_state.get("sucursales_asignadas", ["Matriz"])
        
        # Asegurarnos de que las columnas queden centradas si son pocas
        if len(sucursales) == 1:
            cols = st.columns([1, 2, 1])
            work_cols = [cols[1]]
        elif len(sucursales) == 2:
            cols = st.columns([1, 2, 2, 1])
            work_cols = [cols[1], cols[2]]
        elif len(sucursales) == 3:
            cols = st.columns([1, 2, 2, 2, 1])
            work_cols = [cols[1], cols[2], cols[3]]
        else:
            work_cols = st.columns(len(sucursales))
            
        for i, sucursal in enumerate(sucursales):
            with work_cols[i]:
                st.markdown(f"""
                <div style="background: white; border: 2px solid #e2e8f0; border-radius: 16px; padding: 30px 10px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); margin-bottom: 15px;">
                    <div style="font-size: 3.5rem; margin-bottom: 10px;">
                        {'🏛️' if sucursal == 'Matriz' else '🏬' if '1' in sucursal else '🏪'}
                    </div>
                    <h3 style="color: #0f172a; margin: 0; font-size: 1.4rem;">{sucursal}</h3>
                    <p style="color: #64748b; font-size: 0.85rem; margin-top: 5px;">Base de datos aislada</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Entrar a {sucursal}", key=f"btn_suc_{sucursal}", use_container_width=True, type="primary"):
                    st.session_state.sucursal_activa = sucursal
                    st.rerun()
                    
        st.stop()

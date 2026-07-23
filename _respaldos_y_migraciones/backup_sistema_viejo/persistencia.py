"""
utils/persistencia.py — Guardar y cargar datos de la aplicación
"""

import json
import streamlit as st
from database import guardar_todos_pacientes, guardar_todas_historias


def guardar_datos():
    """
    Guarda los DataFrames actuales a CSV y sincroniza con SQLite.
    Llamar esta función después de cualquier cambio en pacientes o historias.
    """
    if "df_pacientes" in st.session_state:
        st.session_state.df_pacientes.to_csv("pacientes.csv", index=False)
        guardar_todos_pacientes(st.session_state.df_pacientes)

    if "df_historias" in st.session_state:
        st.session_state.df_historias.to_csv("historias.csv", index=False)
        guardar_todas_historias(st.session_state.df_historias)

    # Guardar configuración del optometrista
    with open("optometrista.json", "w", encoding="utf-8") as f:
        json.dump({
            "opto_nombre":    st.session_state.get("opto_nombre", ""),
            "opto_registro":  st.session_state.get("opto_registro", ""),
            "opto_cargo":     st.session_state.get("opto_cargo", ""),
            "opto_direccion": st.session_state.get("opto_direccion", ""),
            "opto_telefono":  st.session_state.get("opto_telefono", ""),
        }, f)

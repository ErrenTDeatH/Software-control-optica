import streamlit as st
import pandas as pd
from database import cargar_inventario, guardar_producto, eliminar_producto


def render_inventario():
    st.markdown("""
        <div class="page-header">
            <h1 style='margin:0; color:#1e293b;'>📦 Control de Inventario</h1>
            <p style='margin:5px 0 0 0; color:#64748b;'>Gestión de monturas y productos</p>
        </div>
    """, unsafe_allow_html=True)

    sucursal_activa = st.session_state.get("sucursal_activa", "Matriz")
    
    # CSS Refinado: Diseño Premium de Tabla
    st.markdown("""
        <style>
        /* Estilo general de las filas */
        .inventory-row {
            padding: 4px 8px;
            border-bottom: 1px solid #f1f5f9;
            transition: background-color 0.2s ease;
            display: flex;
            align-items: center;
        }
        .inventory-row:hover {
            background-color: #f8fafc !important;
        }
        .row-even {
            background-color: #ffffff;
        }
        .row-odd {
            background-color: #fafbfc;
        }
        .row-low-stock {
            background-color: #fff1f2 !important; /* Rojo suave */
            border-left: 4px solid #ef4444 !important;
        }

        /* Ajuste de celdas */
        [data-testid="stMain"] .cell-content {
            font-size: 14px;
            display: flex;
            align-items: center;
            height: 38px;
            color: #334155;
            margin: 0 !important;
        }
        
        /* Botones estilo CAJA */
        [data-testid="stMain"] div[data-testid="stButton"] > button {
            border: 1px solid #e2e8f0 !important;
            background: white !important;
            padding: 4px 12px !important;
            color: #1e293b !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            border-radius: 6px !important;
            height: 32px !important;
        }
        [data-testid="stMain"] div[data-testid="stButton"] > button:hover {
            border-color: #3b82f6 !important;
            color: #3b82f6 !important;
        }

        /* Cabecera de Producto */
        .product-header-box {
            background-color: #f1f5f9;
            border-radius: 8px;
            padding: 12px;
            margin: 10px 0;
            text-align: center;
            color: #0f172a;
            font-weight: 700;
            font-size: 15px;
            border-left: 4px solid #3b82f6;
        }

        .header-label {
            font-size: 13px;
            font-weight: 800;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        </style>
    """, unsafe_allow_html=True)

    # ── TABLA PRINCIPAL ────────────────────────────────────────
    df = cargar_inventario(sucursal_activa)

    if df.empty:
        st.info("📭 No hay productos registrados en esta sucursal.")
        return

    # Normalización de columnas
    for col, default in [("nombre", ""), ("categoria", ""), ("proveedor", ""),
                         ("costo_compra", 0.0), ("precio_venta", 0.0),
                         ("cantidad_disponible", 0), ("codigo_referencia", "")]:
        if col not in df.columns:
            df[col] = default

    # Buscador, Filtros y Botón de Agregar (En una sola fila)
    f1, f2, f3, f4 = st.columns([2, 1, 1, 1])
    busq = f1.text_input("🔍 Buscar por código, marca o producto...", label_visibility="collapsed", placeholder="Buscar...")
    f_cat = f2.selectbox("Categoría", ["Todas"] + sorted(df["categoria"].unique().tolist()), label_visibility="collapsed")
    
    if f3.button("➕ Nuevo Producto", type="primary", use_container_width=True):
        st.session_state.show_add_form = not st.session_state.get("show_add_form", False)

    # Formulario para Agregar Producto
    if st.session_state.get("show_add_form"):
        st.markdown('<div class="edit-container" style="background:#f0f7ff; border-color:#3b82f6; padding:20px; border-radius:12px; border:1px solid #bae6fd; margin-bottom:20px;">', unsafe_allow_html=True)
        st.subheader("🆕 Registrar Nuevo Producto")
        with st.form("form_nuevo_prod", border=False):
            c1, c2, c3 = st.columns(3)
            n_cod = c1.text_input("Código de Referencia*")
            n_cat = c2.text_input("Categoría (Ej: Monturas, Accesorios)")
            n_mar = c3.text_input("Marca")
            
            c4, c5 = st.columns([2, 1])
            n_nom = c4.text_input("Nombre / Descripción del Producto*")
            n_pro = c5.text_input("Proveedor")
            
            c6, c7, c8 = st.columns(3)
            n_cos = c6.number_input("Costo Compra ($)", min_value=0.0, step=0.01)
            n_pvp = c7.number_input("Precio de Venta ($)", min_value=0.0, step=0.01)
            n_stock = c8.number_input("Stock Inicial", min_value=0, step=1)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("🚀 Guardar Producto en Inventario", use_container_width=True):
                if not n_cod or not n_nom:
                    st.error("Código y Nombre son obligatorios.")
                else:
                    guardar_producto({
                        "codigo_referencia": n_cod,
                        "nombre": n_nom,
                        "categoria": n_cat,
                        "marca": n_mar,
                        "proveedor": n_pro,
                        "costo_compra": n_cos,
                        "precio_venta": n_pvp,
                        "cantidad_disponible": n_stock,
                        "sucursal": sucursal_activa
                    })
                    st.session_state.show_add_form = False
                    st.success(f"Producto {n_nom} registrado con éxito.")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    df_f = df.copy()
    if busq:
        df_f = df_f[df_f.apply(lambda r: busq.lower() in str(r).lower(), axis=1)]
    if f_cat != "Todas":
        df_f = df_f[df_f["categoria"] == f_cat]

    with f4:
        from utils.pdf import generar_pdf_inventario
        pdf_bytes = generar_pdf_inventario(df_f, sucursal_activa, st.session_state.get("user_name", ""))
        st.download_button("📥 PDF Control", data=pdf_bytes, file_name=f"Control_Inventario_{sucursal_activa}.pdf", mime="application/pdf", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # ── ENCABEZADOS ────────────────────────────────────────────
    cols_ratio = [1.2, 3.2, 1.2, 1.2, 1.8, 0.9, 0.9, 0.9]
    h = st.columns(cols_ratio)
    labels = ["CÓDIGO", "PRODUCTO", "CATEGORÍA", "MARCA", "PROVEEDOR", "COSTO", "PVP", "STOCK"]
    for i, label in enumerate(labels):
        h[i].markdown(f"<p class='header-label'>{label}</p>", unsafe_allow_html=True)
    
    st.markdown("<hr style='margin:10px 0; opacity:0.2;'>", unsafe_allow_html=True)
    
    # ── FILAS DE DATOS ─────────────────────────────────────────
    for idx, (_, row) in enumerate(df_f.iterrows()):
        # Lógica de Stock Bajo
        stock_val = float(row.get("cantidad_disponible", 0))
        is_low = stock_val <= 3
        
        row_class = "row-odd" if idx % 2 == 0 else "row-even"
        if is_low: row_class = "row-low-stock"
        
        # Iniciar contenedor de fila
        st.markdown(f'<div class="{row_class}">', unsafe_allow_html=True)
        cols = st.columns(cols_ratio)
        
        # 1. Código
        with cols[0]:
            if st.button(row.get('codigo_referencia') or "---", key=f"c_{row['id']}"):
                st.session_state.inv_exp = row['id'] if st.session_state.get("inv_exp") != row['id'] else None
                st.rerun()

        def draw(val, idx, bold=False, color=None, is_money=False):
            style = f"font-weight:700;" if bold else ""
            if color: style += f"color:{color};"
            display = f"${float(val):.2f}" if is_money else str(val)
            with cols[idx]:
                st.markdown(f'<div class="cell-content" style="{style}">{display}</div>', unsafe_allow_html=True)

        draw(row.get('nombre', ''), 1, bold=True)
        draw(row.get('categoria', ''), 2)
        draw(row.get('marca', ''), 3)
        draw(row.get('proveedor', ''), 4)
        draw(row.get('costo_compra', 0), 5, is_money=True)
        draw(row.get('precio_venta', 0), 6, is_money=True, color="#2563eb", bold=True)
        
        stock = int(row.get('cantidad_disponible', 0))
        draw(stock, 7, bold=True, color="#ef4444" if stock <= 3 else "#22c55e")

        # Acciones Expandidas
        if st.session_state.get("inv_exp") == row['id']:
            st.markdown('<div style="padding: 15px; background: white; border: 1px solid #e2e8f0; border-radius: 8px; margin: 10px 0;">', unsafe_allow_html=True)
            a1, a2, a3, a4 = st.columns([1.2, 1.2, 1.2, 1.2])
            
            if a1.button("➕ Stock", key=f"p_{row['id']}", use_container_width=True):
                guardar_producto({"id": row['id'], "cantidad_disponible": stock+1}); st.rerun()
            if a2.button("➖ Stock", key=f"m_{row['id']}", use_container_width=True):
                if stock > 0: guardar_producto({"id": row['id'], "cantidad_disponible": stock-1}); st.rerun()
            if a3.button("✏️ Editar", key=f"e_{row['id']}", use_container_width=True):
                st.session_state[f"ed_{row['id']}"] = not st.session_state.get(f"ed_{row['id']}", False)
                st.rerun()
            if st.session_state.get("user_role") == "Administrador":
                if a4.button("🗑️ Borrar", key=f"d_{row['id']}", use_container_width=True):
                    eliminar_producto(row['id']); st.rerun()
            else:
                a4.button("🗑️ Protegido", key=f"d_{row['id']}", use_container_width=True, disabled=True)
            
            st.markdown(f'<div class="product-header-box">📦 Gestionando: {row.get("nombre", "Sin nombre")}</div>', unsafe_allow_html=True)

            if st.session_state.get(f"ed_{row['id']}"):
                with st.form(f"f_{row['id']}", border=False):
                    c1, c2, c3 = st.columns([1, 1, 1])
                    n_cod = c1.text_input("Código", value=row.get('codigo_referencia', ''))
                    n_cat = c2.text_input("Categoría", value=row.get('categoria', ''))
                    n_mar = c3.text_input("Marca", value=row.get('marca', ''))
                    c4, c5 = st.columns([2, 1])
                    n_nom = c4.text_input("Nombre / Producto", value=row.get('nombre', ''))
                    n_pro = c5.text_input("Proveedor", value=row.get('proveedor', ''))
                    c6, c7 = st.columns([1, 1])
                    n_cos = c6.number_input("Costo Compra ($)", value=float(row.get('costo_compra', 0)), step=0.01)
                    n_pvp = c7.number_input("PVP ($)", value=float(row.get('precio_venta', 0)), step=0.01)
                    if st.form_submit_button("💾 Guardar Cambios", use_container_width=True):
                        guardar_producto({"id": row['id'], "codigo_referencia": n_cod, "categoria": n_cat, "marca": n_mar, "nombre": n_nom, "proveedor": n_pro, "costo_compra": n_cos, "precio_venta": n_pvp})
                        st.session_state[f"ed_{row['id']}"] = False; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)


    # Alerta de stock bajo
    try:
        if not df.empty:
            stock_num = pd.to_numeric(df["cantidad_disponible"], errors='coerce').fillna(0)
            bajo_stock = df[stock_num <= 3]
            if not bajo_stock.empty:
                codigos = [str(x) for x in bajo_stock["codigo_referencia"].tolist() if pd.notna(x) and str(x).strip()]
                codigos_str = ", ".join(codigos) if codigos else "Varios productos sin código"
                st.warning(f"⚠️ **{len(bajo_stock)} producto(s) con stock ≤ 3:** {codigos_str}")
    except Exception as e:
        import traceback
        st.error(f"Error calculando stock bajo: {str(e)}")
        st.error(traceback.format_exc())

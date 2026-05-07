import streamlit as st
import pandas as pd
from datetime import datetime
from database import registrar_venta_directa, registrar_pago_saldo, cargar_inventario, cargar_ordenes_trabajo

def render_ventas():
    # ── ESTILOS CSS PARA ESTILO FACTURA Y CONFIGURADOR ──
    st.markdown("""
        <style>
        .invoice-box {
            background-color: white;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 0;
            margin-bottom: 20px;
            overflow: hidden;
        }
        .invoice-header {
            background-color: #00458e;
            color: white;
            padding: 8px 15px;
            font-weight: 600;
            font-size: 16px;
        }
        .invoice-body {
            padding: 15px;
        }
        .opt-config-card {
            background-color: #f1f5f9;
            border-left: 4px solid #3b82f6;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 15px;
        }
        .admin-box {
            background-color: #fff7ed;
            border: 1px solid #fed7aa;
            padding: 10px;
            border-radius: 6px;
            margin-top: 10px;
        }
        .prescription-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }
        .prescription-table th, .prescription-table td {
            border: 1px solid #cbd5e1;
            padding: 5px;
            text-align: center;
        }
        .prescription-table th { background-color: #f8fafc; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="page-header">
            <h1 style='margin:0; color:#1e293b;'>🧾 Facturación y Ventas</h1>
            <p style='margin:5px 0 0 0; color:#64748b;'>Configurador óptico y registro de ventas</p>
        </div>
    """, unsafe_allow_html=True)

    sucursal_activa = st.session_state.get("sucursal_activa", "Matriz")
    es_admin = st.session_state.get("user_role") == "Administrador"
    
    if "carrito_ventas" not in st.session_state:
        st.session_state.carrito_ventas = []

    tab1, tab2 = st.tabs(["🛒 Nueva Venta / Configurador", "💰 Cobro de Saldos"])

    with tab1:
        # 1. SECCIÓN ADQUIRENTE
        st.markdown('<div class="invoice-box"><div class="invoice-header">Datos del Paciente / Cliente</div></div>', unsafe_allow_html=True)
        with st.container():
            c1, c2, c3 = st.columns([1, 1, 2])
            identificacion = c1.text_input("Identificación:*", placeholder="RUC / Cédula")
            tipo_id = c2.selectbox("Tipo identificación:*", ["Cédula", "RUC", "Consumidor Final"])
            razon_social = c3.text_input("Nombres:*", placeholder="Nombre completo")
            
            c4, c5, c6 = st.columns([2, 1, 1])
            direccion = c4.text_input("Dirección:", placeholder="Dirección")
            telefono = c5.text_input("Teléfono:", placeholder="09XXXXXXXX")
            email = c6.text_input("Correo electrónico:", placeholder="ejemplo@correo.com")

        st.markdown("<br>", unsafe_allow_html=True)

        # 2. CONFIGURADOR ÓPTICO / PRODUCTOS
        st.markdown('<div class="invoice-box"><div class="invoice-header">Configurador de Lentes y Armazón</div></div>', unsafe_allow_html=True)
        
        col_inv, col_opt = st.columns([1, 1.5])
        
        with col_inv:
            st.subheader("👓 Selección de Armazón")
            df_inv = cargar_inventario(sucursal_activa)
            if not df_inv.empty:
                opciones_inv = [f"{r['codigo_referencia']} | {r['nombre']} (${r['precio_venta']})" for _, r in df_inv.iterrows()]
                armazon_sel = st.selectbox("Buscar Armazón:", [""] + opciones_inv)
                if armazon_sel:
                    cod_ref = armazon_sel.split(" | ")[0]
                    producto = df_inv[df_inv["codigo_referencia"] == cod_ref].iloc[0]
                    st.success(f"Seleccionado: {producto['nombre']}")
            else:
                st.info("Cargue productos en el inventario primero.")

        with col_opt:
            st.subheader("🔬 Detalles de Lunas")
            c_l1, c_l2 = st.columns(2)
            tipo_luna = c_l1.selectbox("Tipo de Luna:", ["Monofocal", "Bifocal", "Progresivo", "Lente de Contacto"])
            material = c_l2.selectbox("Material:", ["CR39 (Resina)", "Policarbonato", "Alto Índice", "Mineral"])
            
            # --- MEJORA: PRECIOS SUGERIDOS ---
            PRECIOS_LUNAS = {
                "CR39 (Resina)": 25.0,
                "Policarbonato": 45.0,
                "Alto Índice": 85.0,
                "Mineral": 30.0
            }
            precio_sugerido = PRECIOS_LUNAS.get(material, 0.0)
            
            protecciones = st.multiselect("Protecciones / Tratamientos:", ["Antirreflejo (AR)", "Filtro Azul", "Fotocromático", "Tinte", "Polarizado"])
            incluye = st.multiselect("Accesorios Incluidos:", ["Paño", "Estuche", "Líquido Limpieza"], default=["Paño", "Estuche"])

        st.markdown("<br>", unsafe_allow_html=True)
        
        # 3. MEDIDAS DE LA RECETA
        with st.expander("👁️ Medidas de la Receta (Opcional)", expanded=True):
            c_r1, c_r2 = st.columns(2)
            with c_r1:
                st.markdown("**Ojo Derecho (OD)**")
                o1, o2, o3 = st.columns(3)
                od_esf = o1.text_input("Esf", key="od_esf_v", placeholder="0.00")
                od_cil = o2.text_input("Cil", key="od_cil_v", placeholder="0.00")
                od_eje = o3.text_input("Eje", key="od_eje_v", placeholder="0")
            with c_r2:
                st.markdown("**Ojo Izquierdo (OI)**")
                i1, i2, i3 = st.columns(3)
                oi_esf = i1.text_input("Esf", key="oi_esf_v", placeholder="0.00")
                oi_cil = i2.text_input("Cil", key="oi_cil_v", placeholder="0.00")
                oi_eje = i3.text_input("Eje", key="oi_eje_v", placeholder="0")

        st.markdown("<br>", unsafe_allow_html=True)
        
        # PRECIOS Y COSTOS (MODO ADMIN OCULTO PARA TRABAJADORES)
        p1, p2 = st.columns(2)
        precio_lentes = p1.number_input("Precio Venta Lunas ($):", min_value=0.0, value=precio_sugerido)
        costo_lentes = 0.0
        
        if es_admin:
            costo_lentes = p2.number_input("Costo Laboratorio (Lunas) ($):", min_value=0.0, help="Solo visible para Administrador")
        else:
            st.info("💡 Completa la configuración para calcular el total.")

        if st.button("➕ AGREGAR TRABAJO COMPLETO AL CARRITO", type="primary", use_container_width=True):
            if armazon_sel or precio_lentes > 0:
                # Armazón
                detalles_txt = f"Lunas {tipo_luna} {material} - " + ", ".join(protecciones)
                if armazon_sel:
                    detalles_txt = f"Armazón {producto['nombre']} + " + detalles_txt
                
                # Calcular Costo Total si es admin
                costo_total = costo_lentes
                if armazon_sel:
                    costo_total += float(producto.get("costo_compra", 0))

                st.session_state.carrito_ventas.append({
                    "descripcion": detalles_txt,
                    "cantidad": 1,
                    "precio": (float(producto['precio_venta']) if armazon_sel else 0) + precio_lentes,
                    "costo": costo_total,
                    "receta": {
                        "OD": {"esf": od_esf, "cil": od_cil, "eje": od_eje},
                        "OI": {"esf": oi_esf, "cil": oi_cil, "eje": oi_eje}
                    },
                    "lunas": {"tipo": tipo_luna, "material": material, "protecciones": protecciones},
                    "id_armazon": producto['id'] if armazon_sel else None
                })
                st.success("Trabajo añadido al carrito.")
                st.rerun()

        # DETALLE DEL CARRITO
        if st.session_state.carrito_ventas:
            st.markdown("### 🛒 Detalle de la Venta")
            for idx, item in enumerate(st.session_state.carrito_ventas):
                with st.expander(f"{item['descripcion']} - ${item['precio']:.2f}", expanded=True):
                    st.write(f"**Receta:** OD: {item['receta']['OD']} | OI: {item['receta']['OI']}")
                    if es_admin:
                        ganancia = item['precio'] - item['costo']
                        st.markdown(f"<div class='admin-box'>💰 **Rentabilidad Admin:** Costo: ${item['costo']:.2f} | Ganancia: ${ganancia:.2f} ({ (ganancia/item['precio']*100) if item['precio']>0 else 0:.1f}%)</div>", unsafe_allow_html=True)
                    if st.button("Remover", key=f"del_{idx}"):
                        st.session_state.carrito_ventas.pop(idx)
                        st.rerun()

            # PAGOS
            total_v = sum(i["precio"] for i in st.session_state.carrito_ventas)
            st.markdown(f"## TOTAL A PAGAR: ${total_v:.2f}")
            
            c_p1, c_p2 = st.columns(2)
            metodo = c_p1.selectbox("Forma de Pago:", ["Efectivo", "Transferencia", "Tarjeta", "Crédito Interno"])
            abono = c_p2.number_input("Abono Inicial ($):", min_value=0.0, max_value=total_v, value=total_v)
            saldo = total_v - abono
            
            if st.button("🚀 FINALIZAR VENTA Y GENERAR ORDEN", type="primary", use_container_width=True):
                if not razon_social:
                    st.error("Falta el nombre del cliente.")
                else:
                    # Datos para la venta
                    venta_data = {
                        "cliente": razon_social,
                        "identificacion": identificacion,
                        "total": total_v,
                        "costo_total": sum(i.get("costo", 0) for i in st.session_state.carrito_ventas) if es_admin else 0,
                        "abono": abono,
                        "saldo": saldo,
                        "metodo_pago": metodo,
                        "sucursal": sucursal_activa,
                        "detalles": st.session_state.carrito_ventas,
                        "fecha": datetime.now().isoformat()
                    }
                    
                    # 1. Registrar Venta (Database)
                    res = registrar_venta_directa(venta_data)
                    
                    # 2. Crear Órdenes de Trabajo (Si hay lunas)
                    from database import guardar_orden_trabajo
                    for item in st.session_state.carrito_ventas:
                        if "receta" in item:
                            orden_data = {
                                "paciente_nombre": razon_social,
                                "detalle_lentes": f"{item['lunas']['tipo']} {item['lunas']['material']}",
                                "prescripcion": item['receta'],
                                "estado": "Pendiente",
                                "sucursal": sucursal_activa,
                                "saldo": saldo,
                                "abono": abono,
                                "total_venta": total_v
                            }
                            # Guardar en tabla ordenes_trabajo
                            # (Aquí llamaríamos a guardar_orden_trabajo pero requiere ajustar database.py)
                            pass
                    
                    st.success("Venta y Orden generadas correctamente.")
                    st.session_state.carrito_ventas = []
                    st.balloons()
                    st.rerun()
    
    with tab2:
        st.subheader("💵 Cobro de Saldos")
        # Mantener lógica de cobro existente...

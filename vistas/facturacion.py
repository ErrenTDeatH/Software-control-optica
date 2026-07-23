import streamlit as st
import pandas as pd
from datetime import datetime, date
from database import cargar_ventas_historial, registrar_auditoria
from database_facturas import guardar_factura, cargar_facturas, anular_factura
from utils.firma_sri import cargar_config_empresa, validar_config_sri, firmar_y_enviar_sri


def render_facturacion():
    st.markdown("""
        <style>
        .invoice-preview {
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        .invoice-header-band {
            background: #1e40af;
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .badge-emitida  { background:#dcfce7; color:#16a34a; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:700; }
        .badge-borrador { background:#fef9c3; color:#854d0e; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:700; }
        .badge-anulada  { background:#fee2e2; color:#dc2626; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:700; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="page-header">
            <h1 style='margin:0; color:#1e293b;'>🧾 Facturación</h1>
            <p style='margin:5px 0 0 0; color:#64748b;'>Emisión de comprobantes legales y gestión tributaria</p>
        </div>
    """, unsafe_allow_html=True)

    sucursal_activa = st.session_state.get("sucursal_activa", "Matriz")
    usuario_actual = st.session_state.get("user_login", "admin")
    nombre_actual = st.session_state.get("user_name", "")

    tab1, tab2 = st.tabs(["📄 Emitir Factura", "🗂️ Historial de Facturas"])

    # ══════════════════════════════════════════════════════════════
    # TAB 1: EMITIR FACTURA
    # ══════════════════════════════════════════════════════════════
    with tab1:
        st.markdown("""
            <div style="background:#eff6ff; border-left:5px solid #2563eb; border-radius:6px; padding:15px 20px; margin-bottom:20px;">
                <b style="color:#1e40af;">💡 Flujo de Trabajo</b><br>
                <span style="font-size:13px; color:#3730a3;">
                    Selecciona una venta existente para pre-llenar los datos automáticamente,
                    o completa el formulario manualmente para una factura nueva.
                </span>
            </div>
        """, unsafe_allow_html=True)

        # 🔍 Capturar pre-llenado desde venta directa reciente
        pref = st.session_state.get("prefilled_factura", None)
        if pref:
            venta_data = pref
            # Guardamos los items temporalmente en st.session_state.items_factura
            st.session_state.items_factura = pref.get("items", [{"descripcion": "", "cantidad": 1, "precio_unitario": 0.0}])
            # Limpiamos para evitar que se quede pegado en siguientes cargas manuales
            st.session_state.prefilled_factura = None

        # Pre-llenar desde venta existente
        df_ventas = cargar_ventas_historial(sucursal_activa)
        
        if not pref and not df_ventas.empty:
            with st.expander("🔗 Vincular con venta existente (opcional)", expanded=False):
                opciones_v = [f"Venta #{r['id']} | {r.get('cliente','---')} | ${r.get('total',0)} | {str(r.get('fecha',''))[:10]}"
                              for _, r in df_ventas.iterrows()]
                venta_sel = st.selectbox("Seleccionar Venta:", ["— Nueva factura manual —"] + opciones_v, key="fact_venta_sel")
                if venta_sel != "— Nueva factura manual —":
                    v_id = int(venta_sel.split(" #")[1].split(" |")[0])
                    venta_data = df_ventas[df_ventas["id"] == v_id].iloc[0]
                    st.success(f"✅ Venta #{v_id} vinculada: **{venta_data.get('cliente')}** — Total: **${float(venta_data.get('total', 0)):.2f}**")

        st.divider()

        # DATOS DEL COMPROBANTE
        col_comp, col_num = st.columns(2)
        tipo_comp = col_comp.selectbox("Tipo de Comprobante:", ["Factura", "Nota de Venta (RISE)", "Proforma", "Liquidación de Compra"])
        fecha_fact = col_num.date_input("Fecha de Emisión:", value=date.today())

        # DATOS FISCALES DEL CLIENTE
        st.subheader("👤 Datos del Adquirente")
        c1, c2 = st.columns(2)
        
        # Obtener valores pre-llenados
        val_cliente = ""
        val_identificacion = ""
        val_email = ""
        val_telefono = ""
        val_direccion = ""
        
        if venta_data is not None:
            if isinstance(venta_data, pd.Series):
                val_cliente = venta_data.get("cliente", "")
                val_identificacion = venta_data.get("identificacion", "")
            else: # Es un dict (prefilled_factura)
                val_cliente = venta_data.get("cliente", "")
                val_identificacion = venta_data.get("identificacion", "")
                val_email = venta_data.get("email", "")
                val_telefono = venta_data.get("telefono", "")
                val_direccion = venta_data.get("direccion", "")

        razon_social = c1.text_input("Razón Social / Nombres:*", value=val_cliente)
        identificacion = c2.text_input("RUC / Cédula / Pasaporte:*", value=val_identificacion)
        c3, c4 = st.columns(2)
        email_fact = c3.text_input("Correo Electrónico:", value=val_email)
        telefono_fact = c4.text_input("Teléfono:", value=val_telefono)
        direccion_fact = st.text_input("Dirección Fiscal:", value=val_direccion)

        st.divider()

        # ITEMS DE LA FACTURA
        st.subheader("📋 Detalle de Productos / Servicios")

        if "items_factura" not in st.session_state:
            # Pre-llenar desde venta si fue seleccionada (y no venía de pref)
            if venta_data is not None and isinstance(venta_data, pd.Series):
                detalles = venta_data.get("detalles", [])
                if isinstance(detalles, list) and detalles:
                    st.session_state.items_factura = [
                        {"descripcion": i.get("descripcion", "Producto"), "cantidad": i.get("cantidad", 1),
                         "precio_unitario": float(i.get("precio", 0))}
                        for i in detalles
                    ]
                else:
                    st.session_state.items_factura = [
                        {"descripcion": "Servicios Optométricos / Productos", "cantidad": 1,
                         "precio_unitario": float(venta_data.get("total", 0))}
                    ]
            else:
                st.session_state.items_factura = [{"descripcion": "", "cantidad": 1, "precio_unitario": 0.0}]

        # Editor de items
        for i, item in enumerate(st.session_state.items_factura):
            ic1, ic2, ic3, ic4 = st.columns([3, 1, 1.5, 0.5])
            desc = ic1.text_input("Descripción", value=item["descripcion"], key=f"item_desc_{i}", label_visibility="collapsed" if i > 0 else "visible")
            cant = ic2.number_input("Cant", value=item["cantidad"], min_value=1, step=1, key=f"item_cant_{i}", label_visibility="collapsed" if i > 0 else "visible")
            punit = ic3.number_input("P. Unitario ($)", value=item["precio_unitario"], min_value=0.0, step=0.01, key=f"item_punit_{i}", label_visibility="collapsed" if i > 0 else "visible")
            if ic4.button("🗑", key=f"del_item_{i}") and len(st.session_state.items_factura) > 1:
                st.session_state.items_factura.pop(i)
                st.rerun()
            st.session_state.items_factura[i] = {"descripcion": desc, "cantidad": cant, "precio_unitario": punit}

        if st.button("➕ Agregar ítem"):
            st.session_state.items_factura.append({"descripcion": "", "cantidad": 1, "precio_unitario": 0.0})
            st.rerun()

        st.divider()

        # TOTALES
        subtotal = sum(i["cantidad"] * i["precio_unitario"] for i in st.session_state.items_factura)
        c_tot1, c_tot2 = st.columns(2)
        descuento = c_tot1.number_input("Descuento ($):", min_value=0.0, max_value=subtotal, value=0.0, step=0.50)
        iva_pct = c_tot2.selectbox("IVA:", ["15% (General)", "5% (Reducido)", "0% (Exento)"])
        iva_val = {"15% (General)": 0.15, "5% (Reducido)": 0.05, "0% (Exento)": 0.0}[iva_pct]
        base_imponible = subtotal - descuento
        iva_monto = base_imponible * iva_val
        total = base_imponible + iva_monto

        # Preview totales
        st.markdown(f"""
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:15px; margin:10px 0;">
                <table style="width:100%; font-size:14px;">
                    <tr><td>Subtotal:</td><td style="text-align:right;"><b>${subtotal:.2f}</b></td></tr>
                    <tr><td>Descuento:</td><td style="text-align:right; color:#dc2626;">-${descuento:.2f}</td></tr>
                    <tr><td>Base Imponible:</td><td style="text-align:right;"><b>${base_imponible:.2f}</b></td></tr>
                    <tr><td>IVA ({iva_pct}):</td><td style="text-align:right;">${iva_monto:.2f}</td></tr>
                    <tr style="border-top:2px solid #1e40af; font-size:18px; font-weight:800;">
                        <td>TOTAL:</td><td style="text-align:right; color:#1e40af;">${total:.2f}</td>
                    </tr>
                </table>
            </div>
        """, unsafe_allow_html=True)

        # MÉTODO DE PAGO
        c_mp1, c_mp2 = st.columns(2)
        metodo_pago = c_mp1.selectbox("Forma de Pago:", ["Efectivo", "Tarjeta de Crédito", "Tarjeta de Débito", "Transferencia", "Cheque", "Crédito"])
        monto_pagado = c_mp2.number_input("Monto Recibido ($):", min_value=0.0, value=total, step=0.50)
        saldo_pendiente = max(0.0, total - monto_pagado)

        st.divider()

        # BOTONES DE ACCIÓN
        b1, b2 = st.columns(2)
        if b1.button("💾 Guardar como Borrador", use_container_width=True):
            if not razon_social or not identificacion:
                st.error("Razón Social e Identificación son obligatorios.")
            else:
                factura_obj = {
                    "tipo": tipo_comp.upper().replace(" ", "_"),
                    "fecha": str(fecha_fact),
                    "cliente_nombre": razon_social,
                    "cliente_cedula": identificacion,
                    "cliente_email": email_fact,
                    "items": st.session_state.items_factura,
                    "subtotal": subtotal,
                    "descuento": descuento,
                    "iva": iva_monto,
                    "total": total,
                    "estado": "BORRADOR",
                    "metodo_pago": metodo_pago,
                    "monto_pagado": monto_pagado,
                    "saldo": saldo_pendiente,
                    "venta_id": int(venta_data["id"]) if venta_data is not None else None,
                    "optometrista": nombre_actual,
                    "sucursal": sucursal_activa,
                    "emitida_por": usuario_actual
                }
                result = guardar_factura(factura_obj)
                if result:
                    st.success("✅ Borrador guardado correctamente.")
                    del st.session_state["items_factura"]
                    st.rerun()
                else:
                    st.error("Error al guardar. Verifica la conexión.")

        if b2.button("🧾 EMITIR FACTURA", type="primary", use_container_width=True):
            if not razon_social or not identificacion:
                st.error("Razón Social e Identificación son obligatorios.")
            elif total <= 0:
                st.error("El total de la factura debe ser mayor a $0.")
            else:
                factura_obj = {
                    "tipo": tipo_comp.upper().replace(" ", "_"),
                    "fecha": str(fecha_fact),
                    "cliente_nombre": razon_social,
                    "cliente_cedula": identificacion,
                    "cliente_email": email_fact,
                    "items": st.session_state.items_factura,
                    "subtotal": subtotal,
                    "descuento": descuento,
                    "iva": iva_monto,
                    "total": total,
                    "estado": "EMITIDA",
                    "metodo_pago": metodo_pago,
                    "monto_pagado": monto_pagado,
                    "saldo": saldo_pendiente,
                    "venta_id": int(venta_data["id"]) if venta_data is not None else None,
                    "optometrista": nombre_actual,
                    "sucursal": sucursal_activa,
                    "emitida_por": usuario_actual
                }
                # 1. Guardar en Supabase
                result = guardar_factura(factura_obj)
                if result:
                    factura_id = result.get("id")
                    registrar_auditoria("Emitir Factura", "Facturación",
                                        f"Factura #{factura_id} | Cliente: {razon_social} | Total: ${total:.2f}",
                                        usuario_actual, sucursal=sucursal_activa)

                    # 2. Intentar envío al SRI
                    cfg_sri = cargar_config_empresa(sucursal_activa)
                    es_valida, errores_cfg = validar_config_sri(cfg_sri)

                    if not es_valida:
                        st.warning(f"✅ Factura guardada (ID #{factura_id}), pero **no se pudo enviar al SRI** porque la configuración está incompleta:")
                        for err in errores_cfg:
                            st.error(f"• {err}")
                        st.info("Ve a ⚙️ Configuración → 🏛️ Emisor y SRI para completar la configuración.")
                    else:
                        with st.spinner("📡 Enviando al SRI... Espera un momento."):
                            factura_obj["id"] = factura_id
                            sri_result = firmar_y_enviar_sri(factura_obj, cfg_sri)

                        if sri_result["success"]:
                            # Actualizar la factura con clave de acceso
                            guardar_factura({
                                "id": factura_id,
                                "clave_acceso": sri_result["clave_acceso"],
                                "numero_autorizacion": sri_result["numero_autorizacion"],
                                "xml_sri": sri_result["xml_firmado"][:5000] if sri_result["xml_firmado"] else "",
                                "estado": "AUTORIZADA"
                            })
                            st.success(f"🎉 **Factura AUTORIZADA por el SRI**")
                            st.code(f"Clave de Acceso: {sri_result['clave_acceso']}", language=None)
                            amb = cfg_sri.get("ambiente_sri", "PRUEBAS")
                            if amb == "PRUEBAS":
                                st.info("🟡 Comprobante en **AMBIENTE DE PRUEBAS** — sin valor legal. Cambia a PRODUCCIÓN cuando estés listo.")
                        else:
                            st.error(f"❌ {sri_result['mensaje']}")
                            for err in sri_result.get("errores_sri", []):
                                st.caption(f"Detalle SRI: {err[:300]}")
                            st.warning(f"La factura quedó guardada (ID #{factura_id}) pero sin autorización SRI.")

                    st.balloons()
                    del st.session_state["items_factura"]
                    st.rerun()
                else:
                    st.error("Error al guardar la factura en la base de datos.")

    # ══════════════════════════════════════════════════════════════
    # TAB 2: HISTORIAL
    # ══════════════════════════════════════════════════════════════
    with tab2:
        st.subheader("🗂️ Historial de Facturas")

        col_f1, col_f2 = st.columns(2)
        filtro_estado = col_f1.selectbox("Filtrar por estado:", ["Todos", "EMITIDA", "BORRADOR", "ANULADA"], key="fact_hist_estado")
        estado_param = None if filtro_estado == "Todos" else filtro_estado

        df_fact = cargar_facturas(sucursal=sucursal_activa, estado=estado_param)

        if df_fact.empty:
            st.info("📭 No hay facturas registradas aún.")
        else:
            # Resumen rápido
            emitidas = len(df_fact[df_fact.get("estado", pd.Series()) == "EMITIDA"]) if "estado" in df_fact.columns else 0
            total_fact = df_fact["total"].astype(float).sum() if "total" in df_fact.columns else 0

            m1, m2, m3 = st.columns(3)
            m1.metric("Total Facturas", len(df_fact))
            m2.metric("Emitidas", emitidas)
            m3.metric("Monto Total", f"${total_fact:,.2f}")

            st.markdown("<br>", unsafe_allow_html=True)

            # Lista de facturas
            for _, row in df_fact.iterrows():
                estado = row.get("estado", "BORRADOR")
                badge_class = {"EMITIDA": "badge-emitida", "BORRADOR": "badge-borrador", "ANULADA": "badge-anulada"}.get(estado, "badge-borrador")
                fecha_str = str(row.get("fecha", ""))[:10]

                with st.container():
                    c1, c2, c3, c4, c5 = st.columns([0.6, 2.5, 1.5, 1.5, 1])
                    c1.markdown(f"**#{row.get('id', '?')}**")
                    c2.markdown(f"**{row.get('cliente_nombre', '---')}**  \n"
                                f"<span style='font-size:12px; color:#64748b;'>{row.get('cliente_cedula', '')} · {fecha_str}</span>",
                                unsafe_allow_html=True)
                    c3.markdown(f"<span class='{badge_class}'>{estado}</span>", unsafe_allow_html=True)
                    c4.metric("", f"${float(row.get('total', 0)):,.2f}")

                    with c5:
                        # Descarga PDF
                        try:
                            from utils.pdf import generar_pdf_factura
                            pdf_bytes = generar_pdf_factura(row.to_dict(), st.session_state.get("user_name", ""))
                            st.download_button("📥 PDF", data=pdf_bytes,
                                               file_name=f"Factura_{row.get('id', 'N')}.pdf",
                                               mime="application/pdf",
                                               key=f"pdf_fact_{row.get('id', '')}")
                        except Exception:
                            pass

                        if estado == "EMITIDA" and st.button("🚫 Anular", key=f"anular_{row.get('id')}"):
                            anular_factura(int(row["id"]), usuario_actual, sucursal_activa)
                            st.success(f"Factura #{row['id']} anulada.")
                            st.rerun()

                    st.markdown("<hr style='margin:6px 0; opacity:0.12;'>", unsafe_allow_html=True)

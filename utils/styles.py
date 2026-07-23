import streamlit as st
import os
import base64
from utils.config import config

def apply_custom_styles():
    """Applies custom CSS styles to the Streamlit app."""
    main_bg_url = getattr(config, "MAIN_BG_URL", "")
    main_bg_path = getattr(config, "MAIN_BG_PATH", "main_bg.png")
    main_bg_style = ""

    if main_bg_url:
        main_bg_style = f"background-image: url('{main_bg_url}') !important; background-size: cover !important; background-position: center !important; background-attachment: fixed !important;"
    elif os.path.exists(main_bg_path):
        try:
            with open(main_bg_path, "rb") as f:
                bin_str = base64.b64encode(f.read()).decode()
            main_bg_style = f"background-image: url('data:image/png;base64,{bin_str}') !important; background-size: cover !important; background-position: center !important; background-attachment: fixed !important;"
        except Exception:
            main_bg_style = ""

    primary_color = getattr(config, "PRIMARY_COLOR", "#2563eb")

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"], .stApp {{
        font-family: 'Inter', sans-serif !important;
        {main_bg_style}
    }}

    /* ── Contenedor Principal (Glassmorphism para fondos de imagen) ── */
    .block-container {{
        background: rgba(255, 255, 255, 0.92) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border-radius: 20px;
        padding: 40px !important;
        margin-top: 25px;
        margin-bottom: 25px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
    }}

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #f0f9ff 0%, #e0f2fe 100%) !important;
        border-right: 1px solid #bae6fd !important;
    }}
    [data-testid="stSidebarContent"] {{
        padding-top: 0px !important;
    }}
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div {{
        color: #334155 !important;
    }}
    [data-testid="stSidebar"] button {{
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
    }}
    [data-testid="stSidebar"] button p,
    [data-testid="stSidebar"] button span {{
        color: #1e293b !important;
        font-weight: 600 !important;
    }}
    [data-testid="stSidebar"] button:hover {{
        background-color: #f1f5f9 !important;
        border-color: #3b82f6 !important;
    }}
    [data-testid="stSidebarNav"] {{ display: none; }}

    /* ── Logo Block ── */
    .logo-container {{
        background: linear-gradient(135deg, #ffffff, #f0f9ff);
        border: 1px solid #bae6fd;
        border-radius: 14px;
        padding: 18px 14px;
        text-align: center;
        margin-bottom: 18px;
        cursor: pointer;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: transform 0.2s ease;
    }}
    .logo-container:hover {{
        border-color: #3b82f6;
        box-shadow: 0 0 20px rgba(59,130,246,0.3);
    }}
    .logo-hint {{
        color: #2563eb !important;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin: 0 0 6px 0;
        font-weight: 700;
    }}

    /* ── Page Header ── */
    .page-header {{
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border-radius: 20px;
        padding: 35px 45px;
        margin-bottom: 35px;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(226, 232, 240, 0.8);
        border-left: 12px solid {primary_color};
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.05);
    }}
    .page-header::after {{
        content: "";
        position: absolute;
        top: -50px; right: -50px;
        width: 200px; height: 200px;
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.05), rgba(14, 165, 233, 0.1));
        border-radius: 50%;
    }}
    .page-header h1 {{
        margin: 0;
        font-size: 2.2rem;
        font-weight: 800;
        color: #0f172a;
        letter-spacing: -0.5px;
    }}
    .page-header p {{
        margin: 6px 0 0 0;
        color: #64748b;
        font-size: 1.05rem;
        font-weight: 500;
    }}

    /* ── KPI Cards ── */
    .kpi-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
        gap: 14px;
        margin-bottom: 24px;
    }}
    .kpi-card {{
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border: 1px solid #1e3a5f;
        border-radius: 14px;
        padding: 20px 18px;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        cursor: default;
    }}
    .kpi-card p {{
        color: #e2e8f0 !important;
    }}
    .kpi-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        border-color: #3b82f6;
    }}
    .kpi-icon {{ font-size: 1.6rem; margin-bottom: 8px; }}
    .kpi-value {{
        font-size: 1.8rem; font-weight: 800;
        background: linear-gradient(135deg, #38bdf8, #818cf8);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; line-height: 1;
    }}
    .kpi-value-green {{
        font-size: 1.8rem; font-weight: 800;
        background: linear-gradient(135deg, #22c55e, #4ade80);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; line-height: 1;
    }}
    .kpi-value-red {{
        font-size: 1.8rem; font-weight: 800;
        background: linear-gradient(135deg, #f87171, #fb923c);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; line-height: 1;
    }}
    .kpi-label {{
        font-size: 0.75rem; color: #94a3b8 !important; margin-top: 6px;
        font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;
    }}

    /* ── Stock Alerts ── */
    .alert-critical {{
        background: linear-gradient(135deg, #450a0a, #7f1d1d);
        border: 1px solid #ef4444; border-left: 4px solid #ef4444;
        border-radius: 10px; padding: 12px 16px; margin: 6px 0;
    }}
    .alert-warning {{
        background: linear-gradient(135deg, #431407, #7c2d12);
        border: 1px solid #f97316; border-left: 4px solid #f97316;
        border-radius: 10px; padding: 12px 16px; margin: 6px 0;
    }}
    .alert-ok {{
        background: linear-gradient(135deg, #052e16, #14532d);
        border: 1px solid #22c55e; border-left: 4px solid #22c55e;
        border-radius: 10px; padding: 12px 16px; margin: 6px 0;
    }}
    .alert-text {{ color: #f1f5f9 !important; font-size: 0.88rem; }}
    .alert-sub  {{ color: #94a3b8 !important; font-size: 0.78rem; margin-top: 4px; }}

    /* ── Section Titles ── */
    .section-title {{
        font-size: 1.25rem; font-weight: 800; color: #1e293b;
        margin: 24px 0 14px 0; padding-bottom: 8px;
        border-bottom: 2px solid #cbd5e1;
    }}

    /* ── Divider ── */
    .fancy-divider {{
        height: 1px;
        background: linear-gradient(90deg, transparent, #94a3b8, transparent);
        margin: 20px 0;
    }}

    /* ── Badge Status ── */
    .badge {{ display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; }}
    .badge-green  {{ background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }}
    .badge-yellow {{ background: #fef9c3; color: #854d0e; border: 1px solid #fef08a; }}
    .badge-red    {{ background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }}
    .badge-blue   {{ background: #dbeafe; color: #1e40af; border: 1px solid #bfdbfe; }}
    </style>
    """, unsafe_allow_html=True)

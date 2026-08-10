import streamlit as st


# =========================================================
# TICKET-GENIE DESIGN SYSTEM
# =========================================================

PRIMARY = "#176B67"
PRIMARY_LIGHT = "#E6F4F2"
PRIMARY_DARK = "#0F4F4B"

BACKGROUND = "#F6F8F8"
CARD = "#FFFFFF"

TEXT = "#1F2937"
MUTED = "#6B7280"

BORDER = "#E2E8E7"

SUCCESS = "#2F855A"
WARNING = "#B7791F"
DANGER = "#C53030"


def apply_styles():
    st.markdown(
        f"""
        <style>

        /* ================================
           GLOBAL
        ================================= */

        .stApp {{
            background-color: {BACKGROUND};
            color: {TEXT};
        }}

        .block-container {{
            padding-top: 2rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 1500px;
        }}


        /* ================================
           SIDEBAR
        ================================= */

        section[data-testid="stSidebar"] {{
            background-color: {PRIMARY_DARK};
        }}

        section[data-testid="stSidebar"] * {{
            color: white;
        }}


        /* ================================
           HEADINGS
        ================================= */

        .page-title {{
            font-size: 32px;
            font-weight: 700;
            color: {TEXT};
            margin-bottom: 4px;
        }}

        .page-subtitle {{
            color: {MUTED};
            font-size: 15px;
            margin-bottom: 24px;
        }}


        /* ================================
           CARDS
        ================================= */

        .card {{
            background: {CARD};
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
        }}

        .card-title {{
            font-size: 16px;
            font-weight: 650;
            color: {TEXT};
        }}

        .card-description {{
            font-size: 13px;
            color: {MUTED};
            margin-top: 4px;
        }}


        /* ================================
           METRICS
        ================================= */

        .metric-card {{
            background: {CARD};
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 18px;
        }}

        .metric-label {{
            font-size: 13px;
            color: {MUTED};
        }}

        .metric-value {{
            font-size: 28px;
            font-weight: 700;
            color: {TEXT};
            margin-top: 5px;
        }}


        /* ================================
           QUICK HELP
        ================================= */

        .quick-card {{
            background: {CARD};
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 18px;
            min-height: 100px;
        }}

        .quick-icon {{
            font-size: 22px;
        }}

        .quick-title {{
            font-weight: 650;
            margin-top: 8px;
        }}

        .quick-description {{
            color: {MUTED};
            font-size: 12px;
        }}


        /* ================================
           AI PANEL
        ================================= */

        .ai-card {{
            background: {PRIMARY_LIGHT};
            border: 1px solid #C6E5E1;
            border-radius: 12px;
            padding: 18px;
        }}

        .ai-title {{
            color: {PRIMARY_DARK};
            font-weight: 700;
        }}


        /* ================================
           BUTTONS
        ================================= */

        .stButton > button {{
            border-radius: 8px;
            font-weight: 600;
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(title, subtitle):
    st.markdown(
        f'<div class="page-title">{title}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="page-subtitle">{subtitle}</div>',
        unsafe_allow_html=True,
    )


def section_title(title, description=None):
    st.markdown(
        f"""
        <div style="
            font-size:20px;
            font-weight:650;
            margin-top:24px;
            margin-bottom:10px;
        ">
            {title}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if description:
        st.caption(description)

.ai-card {
    background: #eef7f3;
    border: 1px solid #cfe6dc;
    border-radius: 14px;
    padding: 18px 20px;
    margin-top: 10px;
}

.ai-title {
    font-size: 16px;
    font-weight: 700;
    color: #24594a;
    margin-bottom: 8px;
}

.ai-text {
    font-size: 14px;
    line-height: 1.6;
    color: #53645e;
}

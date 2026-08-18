import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
import calendar
import os
import tempfile
import shutil
import io
from datetime import datetime

st.set_page_config(
    page_title="Pro Calendar Generator",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ---------- THEME SELECTOR + PRINT SHORTCUT (TOP-RIGHT) ----------
col1, col2, col3 = st.columns([5, 1.3, 1.4])
with col2:
    theme = st.selectbox(
        "Theme",
        ["Light", "Dark", "Navy Blue"],
        index=2,
        label_visibility="collapsed"
    )
with col3:
    print_clicked_top = st.button(
        "🖨️ Print",
        key="print_btn_top",
        help="Generate & download the calendar PDF directly",
        use_container_width=True
    )

# ---------- THEME COLORS ----------
if theme == "Light":
    bg = "#ffffff"
    text = "#000000"
    sidebar_bg = "#f0f2f6"
    card_bg = "#ffffff"
    border = "#d0d0d0"
    heading = "#0066cc"
    input_text = "#000000"
    gold = "#b8860b"
elif theme == "Dark":
    bg = "#0e1117"
    text = "#fafafa"
    sidebar_bg = "#262730"
    card_bg = "#1e1e1e"
    border = "#444444"
    heading = "#64ffda"
    input_text = "#fafafa"
    gold = "#f5c542"
else:  # Navy Blue
    bg = "#0a192f"
    text = "#e6f1ff"
    sidebar_bg = "#112240"
    card_bg = "#1a2a4a"
    border = "#3d5a80"
    heading = "#64ffda"
    input_text = "#ffffff"
    gold = "#f5c542"

# ---------- CSS ----------
css = f"""
<style>
    .stApp {{ background-color: {bg} !important; }}
    header[data-testid="stHeader"] {{
        background-color: {bg} !important;
        border-bottom: 1px solid {border} !important;
    }}
    header[data-testid="stHeader"] * {{ color: {text} !important; }}
    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
        border-right: 1px solid {border} !important;
        padding: 0.1rem 0.1rem !important;
    }}
    .main > div {{ background-color: {bg} !important; }}
    .stApp * {{ color: {text} !important; }}
    h1, h2, h3, h4, h5, h6, .stMarkdown h1, .stMarkdown h2 {{ color: {heading} !important; }}

    /* ---------- MOBILE UI COMPACT ---------- */
    @media (max-width: 768px) {{
        .main > div {{ padding-top: 0rem !important; padding-bottom: 0rem !important; }}

        .app-header-title h1 {{ font-size: 1.35rem !important; }}
        .app-header-title svg {{ width: 40px !important; height: 40px !important; }}
        .app-header-sub {{ font-size: 0.8rem !important; }}

        /* Sidebar: compact but with real, non-negative spacing so nothing overlaps */
        section[data-testid="stSidebar"] {{ padding: 0.4rem 0.5rem !important; }}
        section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{ gap: 0.55rem !important; }}
        section[data-testid="stSidebar"] .stHeading h2 {{ font-size: 1rem !important; margin: 0 !important; padding: 0 !important; }}
        section[data-testid="stSidebar"] .stMarkdown p {{ font-size: 0.75rem !important; margin: 0 0 6px 0 !important; }}
        section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{ font-size: 0.8rem !important; margin: 0 0 2px 0 !important; }}
        .stDivider {{ margin: 0.15rem 0 !important; padding: 0 !important; }}
        hr {{ margin: 0.15rem 0 !important; }}
        .stButton button {{ font-size: 13px !important; padding: 4px 0px !important; min-height: 32px !important; }}
        .stButton button[kind="primary"] {{ font-size: 15px !important; padding: 6px 0px !important; min-height: 36px !important; }}
        .stFileUploader {{ min-height: 55px !important; padding: 8px 8px !important; margin-top: 4px !important; }}
        .stFileUploader * {{ font-size: 11px !important; line-height: 1.2 !important; }}
        .stFileUploader button {{ padding: 2px 10px !important; font-size: 11px !important; margin: 3px 0 !important; }}
        .stFileUploader svg {{ width: 16px !important; height: 16px !important; }}
        div[data-testid="stNumberInputContainer"], div[data-testid="stNumberInput"] > div {{ min-height: 32px !important; }}
        div[data-testid="stNumberInput"] input {{ height: 32px !important; }}
        div[data-testid="stNumberInput"] button {{ height: 32px !important; }}
        .stSelectbox > div {{ min-height: 32px !important; padding: 0px 10px !important; }}
    }}

    /* ---------- UNIFIED DROPDOWN BOX ---------- */
    .stSelectbox {{ width: 100% !important; }}
    .stSelectbox > div {{
        background-color: {card_bg} !important;
        border: 1px solid {border} !important;
        border-radius: 8px !important;
        padding: 0px 12px !important;
        min-height: 34px !important;
        display: flex !important;
        align-items: center !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
        transition: 0.2s !important;
    }}
    .stSelectbox > div:hover {{
        border-color: {heading} !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
    }}
    .stSelectbox > div > div {{
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
        margin: 0 !important;
        color: {input_text} !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        width: 100% !important;
    }}
    .stSelectbox svg {{
        fill: {input_text} !important;
        margin-right: 0px !important;
        opacity: 0.7 !important;
    }}
    .stSelectbox div[data-baseweb="select"] {{
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
    }}
    .stSelectbox div[data-baseweb="select"] > div {{
        border: none !important;
        background: transparent !important;
    }}

    /* ---------- YEAR BOX (FIXED: single unified pill, testid-based) ---------- */
    div[data-testid="stNumberInput"] {{
        width: 100% !important;
    }}
    /* The real flex row that holds [- ] [input] [+] */
    div[data-testid="stNumberInputContainer"],
    div[data-testid="stNumberInput"] > div {{
        display: flex !important;
        align-items: stretch !important;
        width: 100% !important;
        background-color: {card_bg} !important;
        border: 1px solid {border} !important;
        border-radius: 8px !important;
        overflow: hidden !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
        transition: 0.2s !important;
        padding: 0 !important;
    }}
    div[data-testid="stNumberInputContainer"]:hover,
    div[data-testid="stNumberInput"] > div:hover {{
        border-color: {heading} !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
    }}
    /* Kill BaseWeb's own bordered wrapper around the input so it doesn't
       show up as a second box floating inside the pill */
    div[data-testid="stNumberInput"] div[data-baseweb="input"] {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        flex: 1 1 auto !important;
        min-width: 0 !important;
    }}
    div[data-testid="stNumberInput"] div[data-baseweb="base-input"] {{
        background: transparent !important;
        border: none !important;
    }}
    /* Input field itself */
    div[data-testid="stNumberInput"] input {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0px 8px !important;
        margin: 0px !important;
        height: 34px !important;
        color: {input_text} !important;
        text-align: left !important;
        padding-left: 14px !important;
        width: 100% !important;
        font-size: 14px !important;
        font-weight: 600 !important;
    }}
    /* Step buttons */
    div[data-testid="stNumberInput"] button {{
        background: {card_bg} !important;
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        padding: 0px 12px !important;
        color: {text} !important;
        min-width: 32px !important;
        flex: 0 0 auto !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 18px !important;
        transition: 0.2s !important;
        margin: 0 !important;
        line-height: 1 !important;
        cursor: pointer !important;
    }}
    div[data-testid="stNumberInputStepDown"] {{
        border-right: 1px solid {border} !important;
        order: -1 !important;
    }}
    div[data-testid="stNumberInputStepUp"] {{
        border-left: 1px solid {border} !important;
    }}
    div[data-testid="stNumberInput"] button:hover {{
        background-color: {heading} !important;
        color: {bg} !important;
    }}

    /* ---------- UPLOAD BOX ---------- */
    .stFileUploader {{
        background-color: {card_bg} !important;
        border: 2px dashed {border} !important;
        border-radius: 16px !important;
        padding: 25px 12px !important;
        min-height: 140px !important;
        width: 100% !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
        transition: 0.3s !important;
    }}
    .stFileUploader:hover {{
        border-color: {heading} !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.2) !important;
    }}
    .stFileUploader *,
    .stFileUploader div,
    .stFileUploader span,
    .stFileUploader p,
    .stFileUploader label {{
        color: {gold} !important;
        background-color: transparent !important;
        font-size: 14px !important;
        line-height: 1.4 !important;
        font-weight: 500 !important;
    }}
    .stFileUploader button {{
        background-color: {heading} !important;
        color: {bg} !important !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 6px 16px !important;
        margin: 6px 0 !important;
    }}
    .stFileUploader button:hover {{
        background-color: #1a5a8c !important;
        color: white !important;
    }}

    /* ---------- BUTTONS ---------- */
    .stButton button {{
        background-color: #1a5a8c !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: bold !important;
    }}
    .stButton button:hover {{ background-color: #2a6a9c !important; }}

    .stButton button[kind="primary"] {{
        background-color: #e63946 !important;
        color: white !important;
        font-size: 22px !important;
        font-weight: 900 !important;
        padding: 10px 0px !important;
        border-radius: 12px !important;
        box-shadow: 0 0 20px rgba(230, 57, 70, 0.5) !important;
        border: 2px solid #ff6b6b !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        transition: 0.2s !important;
        min-height: 40px !important;
    }}
    .stButton button[kind="primary"]:hover {{
        background-color: #ff6b6b !important;
        color: #0a192f !important;
        transform: scale(1.02) !important;
        box-shadow: 0 0 40px rgba(230, 57, 70, 0.8) !important;
    }}

    .stAlert, .stSuccess, .stError, .stWarning {{
        background-color: {card_bg} !important;
        border-left: 4px solid {heading} !important;
    }}
    .stDownloadButton button {{
        background-color: {bg} !important;
        border: 1px solid {border} !important;
        color: {heading} !important;
    }}
    .stDownloadButton button:hover {{
        background-color: #1a5a8c !important;
        color: white !important;
    }}
    hr {{ border-color: {border} !important; }}
    footer {{ visibility: hidden; }}

    /* ---------- TOP-CORNER PRINT/PDF SHORTCUT BUTTON (blue, shining) ---------- */
    div[data-testid="stHorizontalBlock"]:first-of-type > div:nth-child(3) button {{
        background: linear-gradient(135deg, #1565c0, #42a5f5) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        border: 1px solid #90caf9 !important;
        border-radius: 10px !important;
        box-shadow: 0 0 14px rgba(30,136,229,0.65) !important;
        animation: printGlow 2.4s ease-in-out infinite;
        transition: 0.2s !important;
    }}
    div[data-testid="stHorizontalBlock"]:first-of-type > div:nth-child(3) button:hover {{
        background: linear-gradient(135deg, #1976d2, #64b5f6) !important;
        box-shadow: 0 0 26px rgba(30,136,229,0.95) !important;
        transform: scale(1.03) !important;
    }}
    @keyframes printGlow {{
        0%, 100% {{ box-shadow: 0 0 10px rgba(30,136,229,0.55); }}
        50% {{ box-shadow: 0 0 22px rgba(30,136,229,0.95); }}
    }}

    /* ---------- FOOTER SOCIAL BADGES (small, shining blue pills, matching Print button) ---------- */
    .app-footer {{
        margin-top: 2.5rem;
        padding-top: 1.2rem;
        border-top: 1px solid {border};
        text-align: center;
    }}
    .app-footer .social-row {{
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
        margin-bottom: 0.7rem;
    }}
    .app-footer .social-badge {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        border-radius: 8px;
        background: linear-gradient(135deg, #1565c0, #42a5f5);
        border: 1px solid #90caf9;
        box-shadow: 0 0 10px rgba(30,136,229,0.65);
        animation: printGlow 2.4s ease-in-out infinite;
        transition: 0.25s;
        text-decoration: none;
    }}
    .app-footer .social-badge img {{
        width: 14px;
        height: 14px;
        filter: brightness(0) invert(1);
    }}
    .app-footer .social-badge img.logo-native {{
        width: 18px;
        height: 18px;
        filter: none;
        background: #ffffff;
        border-radius: 4px;
        padding: 1px;
        object-fit: contain;
    }}
    .app-footer .social-badge:hover {{
        transform: translateY(-3px) scale(1.15);
        background: linear-gradient(135deg, #1976d2, #64b5f6);
        box-shadow: 0 0 22px rgba(30,136,229,0.95);
    }}
    .app-footer .copyright-line {{
        font-size: 0.78rem;
        opacity: 0.8;
        margin: 0;
    }}

    /* ---------- HIDE NATIVE STREAMLIT MENU (System/Light/Dark/Print) ----------
       This menu is Streamlit's own built-in theme switcher — it cannot be
       synced with our custom Light/Dark/Navy Blue dropdown, so we hide it
       to avoid two separate, conflicting theme controls confusing users. */
    #MainMenu {{ display: none !important; visibility: hidden !important; }}
    div[data-testid="stMainMenu"] {{ display: none !important; visibility: hidden !important; }}
    button[data-testid="stMainMenuButton"] {{ display: none !important; }}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

st.markdown(f"""
<div class="app-header-title" style="display:flex; align-items:center; gap:14px; margin-top:0.6rem; margin-bottom:0.4rem; flex-wrap:wrap;">
  <svg width="48" height="48" viewBox="0 0 64 64" style="flex-shrink:0;">
    <path d="M14 4 H40 L50 14 V60 H14 Z" fill="#E63946" stroke="#b71c2c" stroke-width="1"/>
    <path d="M40 4 L50 14 H40 Z" fill="#ff6b6b"/>
    <text x="32" y="40" font-family="Helvetica, Arial, sans-serif" font-size="13" font-weight="900" fill="white" text-anchor="middle">PDF</text>
  </svg>
  <h1 style="margin:0; padding:0; color:{heading}; line-height:1.2;">Professional Calendar Generator</h1>
</div>
""", unsafe_allow_html=True)
st.markdown('<p class="app-header-sub" style="margin:0 0 0.5rem 0;">Upload 13 photos, select year, and get a print-ready PDF instantly!</p>', unsafe_allow_html=True)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:8px; margin:0.2rem 0 0.3rem 0;">
      <svg width="24" height="24" viewBox="0 0 64 64" style="flex-shrink:0;">
        <path d="M14 4 H40 L50 14 V60 H14 Z" fill="#E63946" stroke="#b71c2c" stroke-width="1"/>
        <path d="M40 4 L50 14 H40 Z" fill="#ff6b6b"/>
        <text x="32" y="40" font-family="Helvetica, Arial, sans-serif" font-size="13" font-weight="900" fill="white" text-anchor="middle">PDF</text>
      </svg>
      <h2 style="margin:0; padding:0; color:{heading}; font-size:1.1rem;">Settings</h2>
    </div>
    """, unsafe_allow_html=True)
    year = st.number_input("Year", min_value=2024, max_value=2040, value=2027, step=1)
    country = st.selectbox("Country (Holidays)", [
        "India", "Switzerland", "USA", "United Kingdom", 
        "Germany", "France", "UAE", "Canada", "Australia", "Singapore"
    ])
    st.divider()
    st.subheader("🖼️ Upload Images")
    st.markdown("**Upload 13 images:** 1 Cover + 12 Months")
    uploaded_files = st.file_uploader("Select Images", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)
    generate_btn = st.button("📄 Create PDF", type="primary", use_container_width=True)

# ---------- HOLIDAYS ----------
def get_holidays(year, country):
    h = {}
    if country == "Switzerland":
        h = {(1,1):"New Year", (1,2):"Berchtold", (3,26):"Good Fri", (3,29):"Easter Mon", (5,6):"Ascension", (5,17):"Whit Mon", (8,1):"National", (12,25):"Christmas", (12,26):"St. Stephen"}
    elif country == "USA":
        h = {(1,1):"New Year", (1,18):"MLK", (2,15):"Presidents", (5,31):"Memorial", (7,4):"Independence", (9,6):"Labor", (10,11):"Columbus", (11,11):"Veterans", (11,25):"Thanksgiving", (12,25):"Christmas"}
    elif country == "India":
        h = {(1,26):"Republic", (3,17):"Holi", (4,2):"Good Fri", (8,15):"Independence", (10,2):"Gandhi", (11,4):"Diwali", (12,25):"Christmas"}
    elif country == "United Kingdom":
        h = {(1,1):"New Year", (4,2):"Good Fri", (4,5):"Easter Mon", (5,3):"Early May", (5,31):"Spring", (8,30):"Summer", (12,25):"Christmas", (12,26):"Boxing"}
    elif country == "Germany":
        h = {(1,1):"New Year", (4,2):"Good Fri", (4,5):"Easter Mon", (5,1):"Labour", (5,6):"Ascension", (5,17):"Whit Mon", (10,3):"Unity", (12,25):"Christmas", (12,26):"Boxing"}
    elif country == "France":
        h = {(1,1):"New Year", (4,5):"Easter Mon", (5,1):"Labour", (5,8):"VE Day", (5,6):"Ascension", (5,17):"Whit Mon", (7,14):"Bastille", (8,15):"Assumption", (11,1):"All Saints", (11,11):"Armistice", (12,25):"Christmas"}
    elif country == "UAE":
        h = {(1,1):"New Year", (3,26):"Good Fri", (5,6):"Ascension", (7,30):"Islamic NY", (11,4):"Prophet BD", (12,2):"National Day", (12,25):"Christmas"}
    elif country == "Canada":
        h = {(1,1):"New Year", (4,2):"Good Fri", (4,5):"Easter Mon", (5,24):"Victoria", (7,1):"Canada", (9,6):"Labor", (10,11):"Thanksgiving", (11,11):"Remembrance", (12,25):"Christmas", (12,26):"Boxing"}
    elif country == "Australia":
        h = {(1,1):"New Year", (1,26):"Australia", (4,2):"Good Fri", (4,5):"Easter Mon", (4,25):"Anzac", (6,14):"King's BD", (12,25):"Christmas", (12,26):"Boxing"}
    elif country == "Singapore":
        h = {(1,1):"New Year", (3,17):"Holi", (4,2):"Good Fri", (5,1):"Labour", (5,6):"Ascension", (8,15):"Independence", (11,4):"Diwali", (12,25):"Christmas"}
    return h

def generate_pdf(year, country, uploaded_files):
    temp_dir = tempfile.mkdtemp()
    img_dir = os.path.join(temp_dir, "images")
    os.makedirs(img_dir)
    
    month_counter = 1
    for f in uploaded_files:
        if "cover" in f.name.lower():
            with open(os.path.join(img_dir, "cover.jpg"), "wb") as out:
                out.write(f.getbuffer())
        elif month_counter <= 12:
            with open(os.path.join(img_dir, f"{month_counter:02d}.jpg"), "wb") as out:
                out.write(f.getbuffer())
            month_counter += 1

    holidays = get_holidays(year, country)
    
    def find_image(num):
        path = os.path.join(img_dir, "cover.jpg") if num == 0 else os.path.join(img_dir, f"{num:02d}.jpg")
        return path if os.path.exists(path) and os.path.getsize(path) > 0 else None

    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)

    c.setPageSize(A4)
    c.setFillColor(colors.red)
    c.rect(0, 0, 210*mm, 297*mm, fill=1, stroke=0)
    c.setStrokeColor(colors.white)
    c.setLineWidth(2)
    c.rect(10*mm, 10*mm, 190*mm, 277*mm, fill=0, stroke=1)
    img = find_image(0)
    if img:
        try:
            c.drawImage(img, 30*mm, 60*mm, 150*mm, 150*mm, preserveAspectRatio=True)
        except:
            pass
    else:
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 60)
        c.drawCentredString(105*mm, 180*mm, str(year))
    c.setFillColor(colors.white)
    c.setFont("Helvetica", 10)
    c.drawCentredString(105*mm, 25*mm, f"{country} Calendar")
    c.showPage()

    for m in range(1, 13):
        c.setPageSize(A4)
        c.setFillColor(colors.white)
        c.rect(0, 0, 210*mm, 297*mm, fill=1, stroke=0)
        c.setFillColor(colors.lightgrey)
        c.rect(23*mm, 23*mm, 170*mm, 240*mm, fill=1, stroke=0)
        c.setStrokeColor(colors.black)
        c.setLineWidth(2)
        c.rect(20*mm, 20*mm, 170*mm, 240*mm, fill=0, stroke=1)
        img = find_image(m)
        if img:
            try:
                c.drawImage(img, 25*mm, 25*mm, 160*mm, 220*mm, preserveAspectRatio=True)
            except:
                pass
        else:
            c.setFillColor(colors.black)
            c.setFont("Helvetica-Bold", 24)
            c.drawCentredString(105*mm, 140*mm, f"PHOTO {m:02d}")
        c.setFillColor(colors.red)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(105*mm, 14*mm, calendar.month_name[m].upper())
        c.showPage()

        c.setPageSize(A4)
        c.setFillColor(colors.white)
        c.rect(0, 0, 210*mm, 297*mm, fill=1, stroke=0)
        c.setFillColor(colors.red)
        c.rect(15*mm, 270*mm, 180*mm, 18*mm, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(105*mm, 276*mm, f"{calendar.month_name[m].upper()} {year}")
        left, top, cw, ch = 20*mm, 250*mm, 24*mm, 13*mm
        for i, day in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            c.setFillColor(colors.red if i in (5, 6) else colors.black)
            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(left + i*cw + cw/2, top - 5, day)
        cal = calendar.monthcalendar(year, m)
        for r, week in enumerate(cal):
            y_pos = top - (r+1)*ch - 8*mm
            for col, day in enumerate(week):
                if day:
                    x = left + col*cw
                    if col in (5, 6):
                        c.setFillColor(colors.lightgrey)
                        c.rect(x, y_pos-2*mm, cw, ch+1*mm, fill=1, stroke=0)
                    c.setFillColor(colors.red if ((m, day) in holidays or col == 6) else colors.black)
                    c.setFont("Helvetica", 11)
                    c.drawCentredString(x + cw/2, y_pos + 3*mm, str(day))
                    if (m, day) in holidays:
                        c.setFillColor(colors.red)
                        c.circle(x + cw/2, y_pos - 2*mm, 1.2*mm, fill=1)
        c.showPage()

    c.save()
    pdf_buffer.seek(0)
    shutil.rmtree(temp_dir)
    return pdf_buffer

if generate_btn or print_clicked_top:
    if not uploaded_files:
        st.error("❌ Please upload at least 1 image.")
    elif len(uploaded_files) < 2:
        st.warning("⚠️ You uploaded only a few. For best results, upload 13 images (Cover + 12 months).")
    else:
        with st.spinner("⏳ Generating your PDF..."):
            try:
                pdf_data = generate_pdf(year, country, uploaded_files)
                st.success("✅ PDF Ready!")
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_data,
                    file_name=f"{year}_Calendar_{country}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error: {e}")

# ---------- FOOTER: SOCIAL PROFILE BADGES + COPYRIGHT ----------
st.markdown("""
<div class="app-footer">
  <div class="social-row">
    <a class="social-badge" href="https://x.com/udprocks190" target="_blank" rel="noopener noreferrer" title="X (Twitter)">
      <img class="logo-native" src="data:image/png;base64,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" />
    </a>
    <a class="social-badge" href="https://www.linkedin.com/in/jitendrapatel87" target="_blank" rel="noopener noreferrer" title="LinkedIn">
      <img src="https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/linkedin.svg"
           onerror="this.onerror=function(){this.parentElement.innerHTML='<span style=\\'color:#fff;font-weight:900;font-size:12px;\\'>in</span>';};this.src='https://unpkg.com/simple-icons@latest/icons/linkedin.svg';" />
    </a>
    <a class="social-badge" href="https://www.fiverr.com/jitendrapate405" target="_blank" rel="noopener noreferrer" title="Fiverr">
      <img class="logo-native" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFAAAAAtCAYAAAA5reyyAAAKnElEQVR42u2be3BU1R3HP79z7+5md2M27/CKREF5RBEURFBAsVbtoFjb+hqtos74QOmo9TUC1vqs05lqq1bH96NSp61OR6J2BqmCESlQ0YAoiBogYsg7kGx2995z+se9u0kkTh3dPHQ8MzuTe2dyz+987+98z+/3/f2uGGMMgzC00RgMllg97hp2x+upi9fTmGym1ekEIN+OUBwsZGS4jOHhMkAy/+EaF0FQogZjGdgDPaHBoI3B8hfclGhmZcPbrGhYw7q2zdTGv6A11YE2STDa+ydRKAmSH4gyOjyMabHD+FHJMcwtmUlRqNAHUqNEkB7gDsSQgfRA17gZj9vYupmHP32eF794nYb4F4ABFQIVALEQBBEPDGMMBgPGBZ0CnQCEkvAwzhx2IpcfdB6T8yv3m+N7A2BPr6vt3MVtW/7Is3XLcZxOsKNYKogAGtMNVl/G+qAqBAO4OglOB7Yd4YKR87h1wiJGR0YNqDf2O4Aag/IX8thnf+Wmzb+nKdEIgRi2KFyfC7+R8QiWKByjIdVGUaiYeyqv59KKs/eb+zsJoDYaJYqETnLFxiU8+ekyCORhqyCOcbJL5mLj6CSk9rKg4hz+POW3hFQoY8N3DsC04W2pdn669kr+Xf8mdqgE17jf2OO+nkdaOIkGTiibw0vTHyIWyOtXEPsFwDSLxZ1OTn57AdWNawmEiknp1IAQe0AFSCUaObb4GP418wkidiQDcLaH6g/wtNEoA+esv5bqhoEFDyClUwRCxVQ3rOGc9dcgpjvuHPIAaqOxxGLxlvtYXldFIGdgwesFYk4Jy+teYfGW+7DEQqfjyqG6hV2jsUSxunEds1efix3I9U/ZwRkC3imd2seqWcuYVTwtY+OQ80CDQfw3v7DmDhCF8cLjQRuZ+UWxsOYOUjqF+LYOOQBd/6R7eseL1DS/i2173jfYwzUa286lpvldnt7xIsqPPYcYgF6WkdRJ7t3+FGJH+oVvvg0vix3h3u1PkdRJfwuboQOgazSC8Fr9Kra1fYiywmiGBoBeiqhRVphtbR/yWv0qBMmaF6rsmQnP7XoZ6SU2ecMShS2Wn5/i/T0AeaqXMxvSWbH4Nva0edABNP72bUu1s7JpPcaO9Hq7guA6HTjJZrSbwBiNk2hG+4pKf/qe1gmCYmNMysuA7Agrm9bTlmrHEpWVw0Rlg188eeoDmuJ7UCqQMUwQjNvFzKKpXDlmAZNiE8izo9w0/irGHTAW0UmUdPui9Pj1fAHqSzmEfMV1+q4ShegEMwsn83jlTVxWfgbKOCgVpCm+h42tH/SyfZA90Bv/aa0BnUD5j7REYZy9LBl3OdWzlvHgEb/hpNLjmJ5fyd2V13Np+ZkYZ1/Gi7tTwG45yxILY1y0TmJ8YPxcB4PxrwVjHD9k8bjYQmG0w+yCIxgRLmF2wZHk+jkxJunZmqVjJGuK9NZ9teAvUHxhM2TnclnFuRjgqo1L+OfuFXSguWrjUl5tXINl5xIUwWCRNC6WKCyf4B3ATbYSCRUQs6PUJ1vRTgeWHcH2F590OkAFiNkHsM/tICgB4jpByu0kL5DLKw1riNkR1rVvoz3ZRsAKk0I8W7OlAmWDqAHquvaAWBlPcVN7+duMRxiRU4Y2LkvHX80dE68loZPsSTRzcGQUR+YfxsG55VhicddHD3FB+XxGhocTscL8bN2vmJI3niXjF1IYLOCD9q1c+N8bKc4p5bkpd7HX6eDurY9wbvnpxJN7KQ4VMCI8jKr6N9kZ382iMRcy5vWfcPNHDwAWqCAaA6I8W7MkLnzrLZyW3VtSbRkP9KJ/m+qmjcTdOIKwtuV9XtpVRW3n50yKTaAsp5Tq5vc4MFJOaaiED9q30ZrqoDwyiu0dO5lbOJU/TFpMbefn3LblfibmHcqyaffRkmhmd6KRiuiBPDz5do4vnk5TsoW1rZsYGRnJpRVnc/vE68AYclQQkSCWldNNOGLR4rT5XDkEAExTvku3QGqMARXkdx8/SUuyDSWKRZvu4pI1l/Bo7Qtoo0mYFIvfX8rWvZ+g0dTs+5Rmpx2ABRsXM/aAMWjjMVvlAWMBGBsdTbOzl8dqX0AbQ228jqlvnMFl79/G3dsfw9FJlFhcU3MnE1acTIvTgRFrv5jPzYi5MhQ40ACCJfs/SikrcyDYEoBgPiIKJcoD2Y2zrK6KW8dfzc1jL+HU0jnsiu/mo7YtjMgpwaBpTrayde9Wbtq8mYgKUd+5m6AEUCI8v7OKDfWrIVxGPoKtgnzeVc99Hz8OKoSoYJ8Wd9tqvjWIWQhjPIAK7ZhXNUsHFSbFCYVHEvXFzFNKZjA8PJJjC6ZgMByaW8HoWCXP1lWhjcvlB59PQTDGX3a+jJto4pU9q7HEoiRUxKb27UTsKEWhQvKUzbGFR6ExTMo7hIPzKxHg9NI5AARVkFOGzUX6VFwEjOvZ2sP2QQ+kAUbklILRXjwmAm4XNx9yMQXBfADumXgdx5bO5KLRvwADs4qPZn75PLY3beCtpvVE7ShJN8Fzdcshp4w/ffIMz+z4B5NiE3h++gMsHbeQo/MPY/6o+cwf8WOM0cwbfiInlc3GaJf7D7sFgOJgAXeOW4TRiQw/9yIboz1bs6TKZC2MOTR3tF8IF49j7Fwuee92ioIxDNDlJqjr2sPkN870fVTY0bUbCRVz1obrGRYqpksn+aijFqwcutBcuOFG7t3+NKPDw2lINLOudRPRQB7VLe95cSDCZ127wQoyZdVZhCxvy7al9oEK9xEoCxjt2TpUBNV0IfvNhnc4/q0LUIGob7h4BXB/W4N4RXOd7OYfFQRl+8VyB0S84jrdNWDtxMGkQCywwt5LyqSB/jPEArer10lLH/ynRKFTHbxx3LPMKTkmK0X4bx8H+lwzOX8iReFSmpKtiNieh6iQB0qP01l8TkxfG2MQCSB2sFd6Zfwiu7LDCBEvzzDa61qwo72fgUH1eC7Gy1X4UrqndYqicCmT8yf2sn1w40A/c4gF8phbNBVxOjOSufYXnf6ZPq7TYKXv9ZVru8bNlAa+6hk97/VVRLBEIU4nc4umEgvkZSS4ISOoApw/6rRBl/H/n7x//qjTvpTFDwEA09LQKWWzOSQ2Hu3GM6LCUBgKhXbjHBIbzyllszMS3JASVF2jCaogN4y5CON0Dlq/3lfxtHE6uWHMRQRV0M9MsqNFZq2smSZ917gc9ebPqWnbgvUlcXUwhiUK1+nk8NgENsz5O5ZYSBY7t7LmJuK3nAVUgAcPX9wdVA9yPSQdPD94+GICKuAnb5JFesj22zYus4qnccu4hTiJRmwVGDQAbRXASTRyy7iFflHdzWpRPatbuOdW1kZjIZy29gqW171KIKdkwNs7AipAqquBeSNP5eXpD+Oi/fKBDG0Au6X5dHfWxVQ3vjOo3VlhO9KrZpLdE75fuEfAGKJ2lKoZj3JC6SxSXXuwxe7XtltBsMUm1bWHE0pnUTXjUaJ2FIzpt3n7LdZQotB+hvLazCdYUHEeTqIJY1xsyf7HAbbYGOPiJJpYcNB5vDrziX5vruy3LdwrFRvwHulfc2nFOfvN/Z0FsPtg6d8u/V+OnMfS72OXfl/SF/zwnUhWvBGgKdHEyoY1rGh4h3Vtm374Uulrc+P35Fu5/wEeMpnl4u3rzAAAAABJRU5ErkJggg==" />
    </a>
    <a class="social-badge" href="https://www.upwork.com/freelancers/~0182dcb9abc981430b?mp_source=share" target="_blank" rel="noopener noreferrer" title="Upwork">
      <img class="logo-native" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFAAAABQCAYAAACOEfKtAAARoUlEQVR42u2de3RcVb3HP3vvc2YymTRpkzRpQvqgBfpAKBSFUiwtSEHo1cUVUQS8UF2uC6IuFXV5XaxFvd57xaX4AhQFLrRaCnq1oJa0tLWoQKvARVpp+gpt06RJ32keM5k55+x9/zhzTmeSybtoLs1eazL5Y86Z3/me3+v7+/32GWGMMeRZnvFQQgFwpOsI6w6s448H1/O31tc5lGwm4SUw5D30/90SCAqtQioKqnnX2AtYUHkVi6qvoaygtAcWPY7tDqDBYIxBCkljZyMPbf8Bv254iv2JRgxgC1ASpOAdtbQBT4NjQACT45O4fuJHuWvG56iJ16CNRgiBQPQOoDEGIfwPPLzjIf5jy700J48yxoaokggEGgMm0D3zDoEvA4sQSAQGQ8rTtDtQFSvjnvO/zh3T7+qBUQ6ABoNAkPJS3Ln5kzxRv4KxEYgqC0977xhzHQykSirSnsvxNNw+7RZ+PPcxoioaYhUCGJito10+9ofreaaxlgkxC/c0BC4fkJZUtCRdrq+5lpULnsGWVmjO0rd/jRSSOzffzqrGWqpiNo52T3vwAst0tEtVzGZVYy13bV6CFBJtNAAyiDCP7PwRj9evpCpmk9YOoyt3pbVDVczmsfoneXTnwyih8IyH0Eab5kQz71k9gy6vEyXMqOb1Yc6uEcRUEa8u3s6EwglIgeDB7ffTnGwnKuUoeP2Yc1RKWpJtPLj9fgQCcSR5xMyrncWh1GFswSiAA9DCtIbKggpevu5N5Nqm1exPHCIqxSh4A9TCAiXYnzjI803PITe2rMPPvcUoOoPQQ4PghZb1yC2t/4stTRiWR9dAaJ/BloYtx19DHuxqxhKMGu8gDdkScLCrBdnptmYKA6MQDsYPKgEdbityFLjhAOn5VG50DX2NAjgK4CiAowCOAji6hrys04H8Z+dvf3cABSKniZJLaYZG/6QYuOJrYwaV5EshkfhlOc94eJkGmACUAClUpjmmTwl9tfoGDxxjSHsmb6mhQA2+BGGATnfggg/0O5RQaDw6XE3K0ygBcQUxK4YtorgmTaeboNP1MEBMQaElAYFnvFMPoF99NYyPjqcqNgltvG7mAPUd20jr1IBB9PvKUWaOm9mjv9qbFPUddXR5yV770L42G46nPaISLim7mMsrrmJ22RzOGnMOY+0SIrIAx6Q4ljrOjrY6XjmymY0ta9naWocUUGxLtBlaJV6UP5X/KEtYHEm5fH76Z/j2xQ/06Id6Gi5+bjq72nYSs2S/5iCFpMvTTIlP5dXFO7GV6htsA0LAkhdvYsXepymNWHjG7SajotPz0BpumHwTd5zzWS4dP29AKpvy0qxvXseDdd9hQ8sLFNkQkRJvkGYt+9canfnr5ThibVy08YZQRux5rnzLwwUMCyqv8sHscYMVx9MekwqnsuqKtSx770ourZgHwuAaF894aOP7OWNM+L/vF12iKsLimsXULtrII5c+RqEaR4ersYR6O9IYkbciMQwW3muV46Rgvn+6rOJyxkZsXOOGclhCcSztMb9iPr+/+mUWVV8dAgYCS1gooUKLCc4rhEAJhRJWGGQ0mtvO+gTrFr3ItKLpnHC8QYEoh46BQTPEKCb6Tzmk8CPptOKzmFk8i6QHUggsITnheFxafgnPXFlLRawS17goocLoHmiaQPhROfMSCDzj+nMu+GBKJK52mDl2Fmuu+j1njzmbDtdDDTBTGFYibYwfnU9VdpX20rlmbDykkLyvajFdnu+XuzRUFoxnxfz/IW7F8YyHJawexyihcLTH/o797Dqxk4aOBlztoYSFFDIn8lrS1/Cqwmp+seA3xK0xOJpg7uDt08BTnZhuPrTZ96vdNPK6mg8SU6DRJFzNty/6IWfEa0LNywZPCcWe9rf4wl8+x9zV53FJ7QwuW3Muc5+bydzV5/GlV77AnvY9YWM8O2i6xmF6yQy+fdEPaHc0Uoi3EUDjz9P05dMGniz7rmDjwQ00JZrCG6SEwmCYU/Zu5pReyNGkx/smzOfDU27Kq3lKKFbt+wXzai/igR0PsKujjpROoHFJmwQ7O+r4/vbvc2nthayofyIPiDae8fj4tCVcMWEebU7vc4EjigubjC9t6KznpUN/8v1rBtQAmI9M/jiOY/jMjK/0CDg685k1Tau5+U8fJaVbqSiwiCmJzzv8sbWYklQUWDj6BLe9tITlux/rAWKgDXfPugdt+teOEQJgoEUOqxqezAkmCl8Drp90I++pPI/LKxeGzAN8sxZCcjB5kDs3305UCSJS4Wg/WPhAm/CmONrFkpKxUcnnX/k0da11OcNCQYReOOEqzi05i4Sn+6Sew47Cp7KbXGQXsb55A63pE6H5BqnIGfEaHp77BHErnuMf/UAm+O6b99GQOEKhpfqlZtpoIkLS4aX51talCHKHCjzjEVE2V1d/gIQbpFSnGECNzuRmp8AJZlZUxjjWmeI3Db8KLyR7zSmfk8OGAj95OHmYp/b+NyW2wNUD47Wu8Si2Bc+3/JamRJPPpbuxkEvKL0P2k/MOMwqf2ma8RiMULH/rp3hG98jFul9gAPDvGp/hQLJtUMNRBoMlJEdTSV498uccXxxo3LTic4hbok+aOiwfeKodqDYa24LNh//MC80bEOTma919UXChtU3PooQ/bjHYWqFnBLvbdubYUXCW8mg5casQz5heix9Dx2CQdbqBULlAeCHg+3Xf7MFOumuQFJL2dAdbW1+jQJmcHHIwwhx3jnYTQmRKaTFiVrxPO5P9XWNKd+WvgwkbS0QDljlg3LIpV3dmZ4zBM1Bs26xv3siGA+t7sIbsPBRgZ9t2mpIHiaihT5dFZbQXi/ALD2KoVigFtLsdOZcZaERMFVAaKccz4Q0bgIlCkT0GW1lAtln4721Oa+ZcEingG1u+GpaXuoMT8PAdbdtIuiZMd4ZCy2sKp+S9OW3OCTqd9j73xMi+nKwS0Jho6OF/vEwZa2rR2ThaDIgzCiSOFkyJT+0REIJzNyX2YQlwjUOxrXjx8Gss2/1I3ggZrK3H/zqg788ftDwKFJw/7oLc1Chzsxo6G2h3HZToPTj1DqDRRBXs7djFifSJnFwpeL+sYkHGwQ7sTnvG8O7ySzPCnzyXQNCebqchsYeoDExZU2xLlr7xbzR2NvYAMbjYmsLJOHpgvLV7gTfhwrklszi/dHaYEp28PsObx98grYeYBxoMESk42HWUba1v5tCr4IQfmPghKguKSGvdT4le4BpNaSTKB2tuyDmHybCFHW11tCQOY2cmZf15ZEFz8jj3vH53DzMOAP30jM9x+7SbOJB0iEh7gK2CTDXbNdw1/cvY0s6N9pla5PqW2szo3xDzQIki6cFzTc/maGDg2KsKq/jMjC9zLKX7FD4qbY6kNLee+QmmjJkSlpwCTRQI1hz4HR2eySHvftARpLyuvKFKCAECfjrvZ3z8zI9wIOmE4PQmi0AQkREOJB1umHQtt0y7DW10WJgI9sTtbd/Li4deoMgeRh7ooYlbsKrhSRJuIscXBCB+6dyvceOUD9CUSPvJqbSwxMmXEpKmZJrLyi/k3gvuCzf1hH4WScpLs6phJXFFTpE2aGzNKb04x+y7m7EtFcvnP803Zt9LSvvVap0xyWxZLKFwjeFAMs37q6/gkXkrEYIcduPTU8Ejux7geDqFnaGUQwLQGE2hUuxoa2TFW0/kJLZBtdeWip/P/xVfedcXgUIOd7kcSfmvwymXTkdzy5SP8OyVz1MSKc7URkQYjISQ/Hrf02w5vpu4levngkB2TvHMXnNC3zL8z94zeykbr97MhyfdiC2KOJbyOJwly7GUR4ldwb/PvpffXLmWsZGSnPPqTImsvq2eR3f9hJKI7JdX99qVy4meBsbZ5Wy+bivjY+PD7bDZQQCgvu0tft+yjvq2HbjG4YzCySyovII55Rf1+KxGg4EOp5N5teezP7GPAil6aGBawx+veZ3zS2fnaG9gbt2zg8AFNHQ0sPnwJna0vUmH00bcGsO7xl3A5ZULKS8o6yFP0COxhMU/bbiSDS0bKbHV8AHMbuJ8sGYxv1z4u5x+Q1iZMbrX4mP3vbbZwv7rptt4fPdyyqIKt1s1Om0MFdEKXl28m+LImJwLzq0liiwt0nlpX75WQfYxBo0SFl997Yvcv+17lHeTZ1h01jUepRGLZ/av5u6/fDZkE9nmHERF17g5r0BLss3WJ/IW/7llKY/vXk5p1OohrBCStAdT4mflBc/THi8ffClTKhW4xg3pXVDf87rJEny3ygQZg98C9XsoFve+/jXu3/Y9yvLIM+x6gGtcyqIWP9zxIJ96+fZMUFFhBywAKtdp+w0cP6/zTpqYga++djdL3/g646KqR8PcF0zg6pP+L7hZgUN3jMutL17PJ1+6jaNdR7GEFQIZaLwS3QOaCjXONa6/lVVYHO06ypIXb+G//vZNyqJWXnlOSUHFMy5lUcWy+mUsXDuXtU1rwg7YyZaiF4LlX7TJ6scqNh3axNXrFnL/tu9SFlV9FgA0cHbxjLw0qyXRTEp3suyt5bx3zUU8vutRkl4qvGnBAFG2LEGEDW50ykuzfPcy5q95Nyv2Pkl5Lzdz2D4wn0/scD08AwsqF3Lzmbcxv2Ihk4um5OXFLYkWNh3exFN7l7HmwLM4Gkrsvn2MEpLWtOa3V65hUfU1ofYG739seYFrN1zB2IhNp+uQ8OC8sTO4cfKtLKp+PzNLZlFoxXqcN+Em2X6ijg3Nz/PLvT/jr63b/EEjpQZstsMG8KSTNrQ7BldDWbSAqUVnMzF+JiV2iV9qcjo4kGygvn0HLV1tCKDYDnJI3WedTmOwRIRN19Zx5pipoYtwjYslLB7d+RPu+PMdjI9aYVBIuB4JD+IWTCqczNSisymNlhFVUZJuF8fTR9nTUc/+xF46XH9CK25JDEMf1RvygGXwhcW2yvikLt5o3cqrx7bmFCYtCVEJ4yIq4wZ0vwM8QggczzAxXkN1Yc1J1pG1tp3YcrIMlonqMUsStySecWlI7GN3xz48c1IWKSCSkWd81MqY+PCq6sOeUA2cu0QQt4J0IvvS/IR8MDN4Qf43uWgqURXJyfcCDv1W+04s2b29qcM8MqokMdV9E6VBYzAmu5/DPxbAnB6JOTXNJYHAyYrAGh1OnUohcbTL/sQ+bNk70TcmmAF7e9eIHTIXwLljZ+eNwAeTLbQkm/wN4uYfu1VtRALoZQqd04tn5S107umopzWdwBoBjyiQI0/zBK42lEbGMKXozNC/ZgO4q20HqX4KnacvgML3fxNiNVTEKkJal73qM23IkbCskaiBae33WwyatHaQWRTMw2NX+/Z+K8WnNYCugbnj56OEhcoaYQsykj2d9X1G4NMaQG00RRZsaK6lMbEvJP0BuF1eF42de4gqRsRzHsT4p5Qxf5eMaXApTKcLKU04Qhy8S6A4MjKeMSJQWHGrhDbnWKYtODK2/xugyJYU54lxJlMV+se7GcNYuwSrsmACR9PHKBhhT+7IpmUjMc13jaGyoAp53tg5uFoMagPg6b6kEDhacP64i5BXVC3KGMbo0zsG42QEhoUTFiGvqV7MxMIKUtoMuKt/Oi8/EzBMLKzkmjOuQ5YVlPGhSbdwIm0GvU/sdFxKKNodww2Tb6U0Wuo/gPFAZzMXr55Blx59AGN/2ucZQYEq4pXFdVQVViG10ZwRr2bpBd/iWFpjSWsUqd5Yh7Q4ltYsnX0f1YXVfqE3aNR86pw7WTLtYzRnppxGV+6KSJvmpMMnpt3Mp865M2xujT4GeQBm2+9jkIMHS0RVhJULVvEvU2+mJeniGX/a6nSMzj5wFq4xtCRdlky7hZULVhFVkZwxFZl9gDGGqIryxHtX8NDFD1CgSjmUdElrEzbQRTimId5hcAlE1pBAWhsOJV0KVRk/uuRBHrvs5/5TzLtteejzxwj2d+7nx9sfYNX+p9nX2XBa/RjBpMKJ/POkm7hrxmepiU8c2I8RZK/sUbGjXcdYd2Atfzi4nq2tr3Okq4VOt/Md+nMYF3J55ftYVH11OAbX189h/B/COSEywP5C4QAAAABJRU5ErkJggg==" />
    </a>
    <a class="social-badge" href="https://www.guru.com/freelancers/jitendrap" target="_blank" rel="noopener noreferrer" title="Guru">
      <img class="logo-native" src="data:image/png;base64,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" />
    </a>
    <a class="social-badge" href="https://www.peopleperhour.com/freelancer/business/jitendra-patel-web-scrapper-data-entry-assistant-yzaymjv" target="_blank" rel="noopener noreferrer" title="PeoplePerHour">
      <img class="logo-native" src="data:image/png;base64,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" />
    </a>
  </div>
  <p class="copyright-line">© 2026 HumanAI Labs — crafted with care, one calendar at a time.</p>
</div>
""", unsafe_allow_html=True)

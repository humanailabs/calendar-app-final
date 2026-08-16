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

# ---------- THEME SELECTOR (TOP-RIGHT) ----------
col1, col2 = st.columns([6, 1])
with col2:
    theme = st.selectbox(
        "Theme",
        ["Light", "Dark", "Navy Blue"],
        index=2,
        label_visibility="collapsed"
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
        .stTitle {{ margin-top: -2.5rem !important; margin-bottom: 0rem !important; font-size: 0.95rem !important; padding-top: 0 !important; }}
        .stMarkdown {{ margin-top: -1.4rem !important; margin-bottom: 0rem !important; font-size: 0.65rem !important; }}
        section[data-testid="stSidebar"] {{ padding: 0rem 0.05rem !important; }}
        section[data-testid="stSidebar"] .stHeader {{ font-size: 0.65rem !important; margin-top: -0.1rem !important; padding-top: 0 !important; }}
        section[data-testid="stSidebar"] .stMarkdown {{ margin-top: -0.1rem !important; font-size: 0.6rem !important; }}
        section[data-testid="stSidebar"] .stSubheader {{ font-size: 0.65rem !important; margin-top: -0.1rem !important; }}
        .stDivider {{ margin: 0.05rem 0 !important; padding: 0 !important; }}
        hr {{ margin: 0.05rem 0 !important; }}
        .stButton button {{ font-size: 13px !important; padding: 2px 0px !important; margin: 0.05rem 0 !important; min-height: 28px !important; }}
        .stButton button[kind="primary"] {{ font-size: 15px !important; padding: 3px 0px !important; min-height: 28px !important; }}
        .stFileUploader {{ min-height: 70px !important; padding: 4px 6px !important; margin-top: -0.3rem !important; margin-bottom: 0rem !important; }}
        .stFileUploader * {{ font-size: 11px !important; line-height: 1.1 !important; }}
        .stFileUploader button {{ padding: 2px 10px !important; font-size: 11px !important; margin: 2px 0 !important; }}
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

    /* ---------- YEAR BOX (ONLY BACKGROUND FIX) ---------- */
    /* Outer wrapper */
    .stNumberInput > div {{
        background-color: {card_bg} !important;
        border: 1px solid {border} !important;
        border-radius: 8px !important;
        padding: 0px 4px !important;
        min-height: 34px !important;
        display: flex !important;
        align-items: center !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
        transition: 0.2s !important;
        width: 100% !important;
    }}
    .stNumberInput > div:hover {{
        border-color: {heading} !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
    }}
    /* Input field */
    .stNumberInput input {{
        background: {card_bg} !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0px 8px !important;
        margin: 0px !important;
        height: auto !important;
        color: {input_text} !important;
        text-align: center !important;
        flex: 1 !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        min-height: 34px !important;
        width: 100% !important;
        order: 1 !important;
    }}
    /* Buttons */
    .stNumberInput button {{
        background: {card_bg} !important;
        border: none !important;
        border-left: 1px solid {border} !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        padding: 0px 12px !important;
        color: {text} !important;
        min-width: 32px !important;
        height: 34px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 18px !important;
        transition: 0.2s !important;
        margin: 0 !important;
        order: 0 !important;
        line-height: 1 !important;
        cursor: pointer !important;
    }}
    .stNumberInput button:first-of-type {{
        border-left: none !important;
        border-radius: 8px 0 0 8px !important;
    }}
    .stNumberInput button:last-of-type {{
        border-radius: 0 8px 8px 0 !important;
        border-left: 1px solid {border} !important;
    }}
    .stNumberInput button:hover {{
        background-color: {heading} !important;
        color: {bg} !important;
        border-left-color: {heading} !important;
    }}
    .stNumberInput button:first-of-type:hover {{
        border-left-color: transparent !important;
        border-right-color: {heading} !important;
    }}
    .stNumberInput button:last-of-type:hover {{
        border-left-color: {heading} !important;
        border-right-color: transparent !important;
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
</style>
"""
st.markdown(css, unsafe_allow_html=True)

st.title("📄 Professional Calendar Generator")
st.markdown("Upload 13 photos, select year, and get a print-ready PDF instantly!")

# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("⚙️ Settings")
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

if generate_btn:
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

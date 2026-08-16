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

st.set_page_config(page_title="Pro Calendar Generator", page_icon="📅", layout="centered")
st.title("📅 Professional Calendar Generator")
st.markdown("Upload 13 photos, select year, and get a print-ready PDF instantly!")

with st.sidebar:
    st.header("⚙️ Settings")
    year = st.number_input("Year", min_value=2024, max_value=2040, value=2027, step=1)
    country = st.selectbox("Country (Holidays)", ["India", "Switzerland", "USA"])
    st.divider()
    st.subheader("🖼️ Upload Images")
    st.markdown("**Upload 13 images:** 1 Cover + 12 Months")
    uploaded_files = st.file_uploader("Select Images", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)
    generate_btn = st.button("🚀 Generate Calendar PDF", type="primary", use_container_width=True)

def get_holidays(year, country):
    h = {}
    if country == "Switzerland":
        h = {(1,1):"New Year", (1,2):"Berchtold", (3,26):"Good Fri", (3,29):"Easter Mon", (5,6):"Ascension", (5,17):"Whit Mon", (8,1):"National", (12,25):"Christmas", (12,26):"St. Stephen"}
    elif country == "USA":
        h = {(1,1):"New Year", (1,18):"MLK", (2,15):"Presidents", (5,31):"Memorial", (7,4):"Independence", (9,6):"Labor", (10,11):"Columbus", (11,11):"Veterans", (11,25):"Thanksgiving", (12,25):"Christmas"}
    elif country == "India":
        h = {(1,26):"Republic", (3,17):"Holi", (4,2):"Good Fri", (8,15):"Independence", (10,2):"Gandhi", (11,4):"Diwali", (12,25):"Christmas"}
    return h

def generate_pdf(year, country, uploaded_files):
    temp_dir = tempfile.mkdtemp()
    img_dir = os.path.join(temp_dir, "images")
    os.makedirs(img_dir)
    
    cover_found = False
    month_counter = 1
    for f in uploaded_files:
        if "cover" in f.name.lower():
            with open(os.path.join(img_dir, "cover.jpg"), "wb") as out:
                out.write(f.getbuffer())
            cover_found = True
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

    # Cover
    c.setPageSize(A4); c.setFillColor(colors.red); c.rect(0,0,210*mm,297*mm,fill=1)
    c.setStrokeColor(colors.white); c.setLineWidth(2); c.rect(10*mm,10*mm,190*mm,277*mm, fill=0, stroke=1)
    img = find_image(0)
    if img:
        try: c.drawImage(img, 30*mm, 60*mm, 150*mm, 150*mm, preserveAspectRatio=True)
        except: pass
    else:
        c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 60); c.drawCentredString(105*mm, 180*mm, str(year))
    c.setFillColor(colors.white); c.setFont("Helvetica", 10); c.drawCentredString(105*mm, 25*mm, f"{country} Calendar")
    c.showPage()

    for m in range(1, 13):
        # Photo Page
        c.setPageSize(A4); c.setFillColor(colors.white); c.rect(0,0,210*mm,297*mm,fill=1)
        c.setFillColor(colors.lightgrey); c.rect(23*mm,23*mm,170*mm,240*mm,fill=1)
        c.setStrokeColor(colors.black); c.setLineWidth(2); c.rect(20*mm,20*mm,170*mm,240*mm, fill=0, stroke=1)
        img = find_image(m)
        if img:
            try: c.drawImage(img, 25*mm, 25*mm, 160*mm, 220*mm, preserveAspectRatio=True)
            except: pass
        else:
            c.setFillColor(colors.black); c.setFont("Helvetica-Bold",24)
            c.drawCentredString(105*mm, 140*mm, f"PHOTO {m:02d}")
        c.setFillColor(colors.red); c.setFont("Helvetica-Bold",14)
        c.drawCentredString(105*mm, 14*mm, calendar.month_name[m].upper())
        c.showPage()

        # Calendar Page
        c.setPageSize(A4); c.setFillColor(colors.white); c.rect(0,0,210*mm,297*mm,fill=1)
        c.setFillColor(colors.red); c.rect(15*mm,270*mm,180*mm,18*mm,fill=1)
        c.setFillColor(colors.white); c.setFont("Helvetica-Bold",16)
        c.drawCentredString(105*mm, 276*mm, f"{calendar.month_name[m].upper()} {year}")
        left, top, cw, ch = 20*mm, 250*mm, 24*mm, 13*mm
        for i, day in enumerate(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]):
            c.setFillColor(colors.red if i in (5,6) else colors.black)
            c.setFont("Helvetica-Bold",10); c.drawCentredString(left+i*cw+cw/2, top-5, day)
        cal = calendar.monthcalendar(year, m)
        for r, week in enumerate(cal):
            y_pos = top - (r+1)*ch - 8*mm
            for col, day in enumerate(week):
                if day:
                    x = left + col*cw
                    if col in (5,6): c.setFillColor(colors.lightgrey); c.rect(x, y_pos-2*mm, cw, ch+1*mm, fill=1)
                    c.setFillColor(colors.red if ((m,day) in holidays or col==6) else colors.black)
                    c.setFont("Helvetica",11); c.drawCentredString(x+cw/2, y_pos+3*mm, str(day))
                    if (m,day) in holidays: c.setFillColor(colors.red); c.circle(x+cw/2, y_pos-2*mm, 1.2*mm, fill=1)
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
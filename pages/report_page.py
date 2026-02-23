import os
import streamlit as st
import model
from datetime import date
import io
import pandas as pd
import plotly.express as px
from fpdf import FPDF # เพิ่มการ import

def create_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    
    # ดึง Path ของโฟลเดอร์ pages ที่ไฟล์นี้อยู่
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # รวม Path เข้ากับชื่อไฟล์ฟอนต์
    font_path = os.path.join(current_dir, 'THSarabunNew.ttf')
    
    try:
        # ลงทะเบียนฟอนต์โดยใช้ Full Path
        pdf.add_font('THSarabun', '', font_path)
        pdf.set_font('THSarabun', '', 16)
    except Exception as e:
        st.error(f"ไม่สามารถโหลดฟอนต์ได้: {e}")
        # กรณีฉุกเฉินให้ใช้ฟอนต์มาตรฐาน (แต่อาจจะอ่านไทยไม่ได้)
        pdf.set_font('Arial', '', 16)

    # --- ส่วนที่เหลือของโค้ด ---
    pdf.cell(0, 10, 'รายงานข้อมูลการยืม-คืนหนังสือ', ln=True, align='C')
    # ... (โค้ดสร้างตารางเดิม) ...
    # 5. ตรวจสอบว่า df มีข้อมูลไหม ถ้าไม่มีให้เขียนบอกใน PDF
    if df.empty:
        pdf.cell(0, 10, '--- ไม่มีข้อมูลในระบบ ---', ln=True, align='C')
    else:
        # ส่วนการสร้างตาราง
        pdf.set_font('THSarabun', '', 12)
        col_width = pdf.epw / len(df.columns)
        line_height = pdf.font_size * 2
        
        # เขียน Header
        for col in df.columns:
            pdf.multi_cell(col_width, line_height, str(col), border=1, align='C', ln=3)
        pdf.ln(line_height)
        
        # เขียน Data
        for row in df.itertuples(index=False):
            for datum in row:
                pdf.multi_cell(col_width, line_height, str(datum), border=1, align='L', ln=3)
            pdf.ln(line_height)
    
    return bytes(pdf.output())

def render_report():
    st.subheader("📊 รายงานสรุประบบยืม-คืนหนังสือ")

    # =========================
    # 1) กราฟวงกลม : สถานะหนังสือ
    # =========================
    st.markdown("### 1) สัดส่วนหนังสือตามสถานะ")

    status_df = model.get_book_status_summary()

    if status_df.empty:
        st.info("ไม่มีข้อมูลหนังสือ")
    else:
        fig = px.pie(
            status_df,
            names="สถานะหนังสือ",
            values="จำนวน",
            hole=0.4,  # ทำเป็น Donut Chart (ดูเป็น Dashboard มากขึ้น)
            title="สัดส่วนหนังสือตามสถานะ"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(status_df, use_container_width=True)

    st.divider()

    # =========================
    # 2) กราฟแท่ง : จำนวนการยืมรายเดือน
    # =========================
    st.markdown("### 2) จำนวนการยืมรายเดือน")

    col1, col2 = st.columns(2)

    with col1:
        month_start = st.date_input(
            "วันที่เริ่มต้น (กราฟรายเดือน)",
            value=date(2025, 6, 1),
            key="month_start"
        )

    with col2:
        month_end = st.date_input(
            "วันที่สิ้นสุด (กราฟรายเดือน)",
            value=date.today(),
            key="month_end"
        )

    if month_start > month_end:
        st.warning("วันที่เริ่มต้นต้องไม่มากกว่าวันที่สิ้นสุด")
        return

    monthly_df = model.get_borrow_summary_by_month(
        month_start.isoformat(),
        month_end.isoformat()
    )

    if monthly_df.empty:
        st.info("ไม่พบข้อมูลการยืมในช่วงเวลาที่เลือก")
    else:
        st.bar_chart(
            monthly_df.set_index("เดือน")["จำนวนการยืม"]
        )

        st.dataframe(monthly_df, use_container_width=True)

    # ===============================
    # 3) รายการผู้ยืม–คืนทั้งหมด
    # ===============================
    st.markdown("### 3) รายการผู้ยืม–คืนทั้งหมด")

    col1, col2, col3 = st.columns(3)

    with col1:
        report_start = st.date_input(
            "วันที่เริ่มต้น (รายงาน)",
            value=date(2025, 6, 1),
            key="report_start"
        )

    with col2:
        report_end = st.date_input(
            "วันที่สิ้นสุด (รายงาน)",
            value=date.today(),
            key="report_end"
        )

    with col3:
        status_label = st.selectbox(
            "สถานะการยืม–คืน",
            ["ทั้งหมด", "ยังไม่คืน", "คืนแล้ว"],
            key="report_status"
        )

    if report_start > report_end:
        st.warning("วันที่เริ่มต้นต้องไม่มากกว่าวันที่สิ้นสุด")
        return

    status_map = {
        "ทั้งหมด": "all",
        "ยังไม่คืน": "borrowed",
        "คืนแล้ว": "returned"
    }

    selected_status = status_map[status_label]

    report_df = model.get_borrow_report(
        report_start.isoformat(),
        report_end.isoformat(),
        selected_status
    )

    if report_df.empty:
        st.info("ไม่พบข้อมูลตามเงื่อนไขที่เลือก")
        return

    st.dataframe(report_df, use_container_width=True)

    # ===============================
    # 4) ส่งออกรายงาน
    # ===============================
    st.markdown("### 4) ส่งออกรายงาน")

    # --- CSV ---
    csv_buffer = io.StringIO()
    report_df.to_csv(csv_buffer, index=False)

    st.download_button(
        label="⬇️ ดาวน์โหลดรายงานผู้ยืม–คืน (CSV)",
        data=csv_buffer.getvalue(),
        file_name="borrow_return_report.csv",
        mime="text/csv"
    )

    # --- Excel ---
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer) as writer:
        report_df.to_excel(writer, index=False, sheet_name="BorrowReport")

    st.download_button(
        label="⬇️ ดาวน์โหลดรายงานผู้ยืม–คืน (Excel)",
        data=excel_buffer.getvalue(),
        file_name="borrow_return_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # --- PDF ---
    if st.button("🚀 สร้างไฟล์ PDF"):
        try:
            pdf_data = create_pdf(report_df)
            
            st.download_button(
                label="⬇️ Click เพื่อดาวน์โหลด PDF",
                data=pdf_data, # ตอนนี้ข้อมูลจะเป็น bytes แล้ว
                file_name="library_report.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
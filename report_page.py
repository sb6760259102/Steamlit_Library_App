import os
import streamlit as st
import model
from datetime import date
import io
import pandas as pd
import plotly.express as px
from fpdf import FPDF


def _find_font_path() -> str:
    """หา path ของ THSarabunNew.ttf โดยลองหลาย location"""
    candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'THSarabunNew.ttf'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'THSarabunNew.ttf'),
        os.path.join(os.getcwd(), 'THSarabunNew.ttf'),
        os.path.join(os.getcwd(), 'pages', 'THSarabunNew.ttf'),
    ]
    for p in candidates:
        if os.path.exists(p):
            return os.path.abspath(p)
    return None


def create_pdf(df):
    pdf = FPDF()
    pdf.add_page()

    font_path = _find_font_path()
    font_loaded = False

    if font_path:
        try:
            pdf.add_font('THSarabun', '', font_path, uni=True)
            pdf.set_font('THSarabun', '', 16)
            font_loaded = True
        except TypeError:
            try:
                pdf.add_font('THSarabun', '', font_path)
                pdf.set_font('THSarabun', '', 16)
                font_loaded = True
            except Exception as e:
                st.warning(f"โหลดฟอนต์ไม่สำเร็จ: {e}")
        except Exception as e:
            st.warning(f"โหลดฟอนต์ไม่สำเร็จ: {e}")
    else:
        st.warning("ไม่พบไฟล์ THSarabunNew.ttf — วางไฟล์ไว้ที่ root หรือ pages/ ของ project")

    if not font_loaded:
        pdf.set_font('Arial', '', 16)

    # Header — ใช้ ln=1 (int) ไม่ใช้ ln=True
    pdf.cell(0, 10, 'รายงานข้อมูลการยืม-คืนหนังสือ', ln=1, align='C')

    if df.empty:
        pdf.cell(0, 10, '--- ไม่มีข้อมูลในระบบ ---', ln=1, align='C')
    else:
        if font_loaded:
            pdf.set_font('THSarabun', '', 10)
        else:
            pdf.set_font('Arial', '', 8)

        col_width = (pdf.w - pdf.l_margin - pdf.r_margin) / len(df.columns)
        line_height = 6  # ใช้ตัวเลขตายตัว ไม่ใช้ pdf.font_size

        # Header row — ใช้ cell + set_xy แทน multi_cell ln=3
        y_row = pdf.get_y()
        x = pdf.l_margin
        for col in df.columns:
            pdf.set_xy(x, y_row)
            pdf.cell(col_width, line_height, str(col)[:25], border=1, align='C')
            x += col_width
        pdf.ln(line_height)

        # Data rows
        for row in df.itertuples(index=False):
            if pdf.get_y() + line_height > (pdf.h - pdf.b_margin):
                pdf.add_page()
                if font_loaded:
                    pdf.set_font('THSarabun', '', 10)
                else:
                    pdf.set_font('Arial', '', 8)

            y_row = pdf.get_y()
            x = pdf.l_margin
            for datum in row:
                text = str(datum) if datum is not None else ''
                pdf.set_xy(x, y_row)
                pdf.cell(col_width, line_height, text[:25], border=1, align='L')
                x += col_width
            pdf.ln(line_height)

    return pdf.output(dest="S").encode("latin-1")


def render_report():
    st.subheader("📊 รายงานสรุประบบยืม-คืนหนังสือ")

    st.markdown("### 1) สัดส่วนหนังสือตามสถานะ")
    status_df = model.get_book_status_summary()
    if status_df.empty:
        st.info("ไม่มีข้อมูลหนังสือ")
    else:
        fig = px.pie(
            status_df,
            names="สถานะหนังสือ",
            values="จำนวน",
            hole=0.4,
            title="สัดส่วนหนังสือตามสถานะ"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(status_df, use_container_width=True)

    st.divider()

    st.markdown("### 2) จำนวนการยืมรายเดือน")
    col1, col2 = st.columns(2)
    with col1:
        month_start = st.date_input("วันที่เริ่มต้น (กราฟรายเดือน)", value=date(2025, 6, 1), key="month_start")
    with col2:
        month_end = st.date_input("วันที่สิ้นสุด (กราฟรายเดือน)", value=date.today(), key="month_end")

    if month_start > month_end:
        st.warning("วันที่เริ่มต้นต้องไม่มากกว่าวันที่สิ้นสุด")
        return

    monthly_df = model.get_borrow_summary_by_month(month_start.isoformat(), month_end.isoformat())
    if monthly_df.empty:
        st.info("ไม่พบข้อมูลการยืมในช่วงเวลาที่เลือก")
    else:
        st.bar_chart(monthly_df.set_index("เดือน")["จำนวนการยืม"])
        st.dataframe(monthly_df, use_container_width=True)

    st.markdown("### 3) รายการผู้ยืม–คืนทั้งหมด")
    col1, col2, col3 = st.columns(3)
    with col1:
        report_start = st.date_input("วันที่เริ่มต้น (รายงาน)", value=date(2025, 6, 1), key="report_start")
    with col2:
        report_end = st.date_input("วันที่สิ้นสุด (รายงาน)", value=date.today(), key="report_end")
    with col3:
        status_label = st.selectbox("สถานะการยืม–คืน", ["ทั้งหมด", "ยังไม่คืน", "คืนแล้ว"], key="report_status")

    if report_start > report_end:
        st.warning("วันที่เริ่มต้นต้องไม่มากกว่าวันที่สิ้นสุด")
        return

    status_map = {"ทั้งหมด": "all", "ยังไม่คืน": "borrowed", "คืนแล้ว": "returned"}
    report_df = model.get_borrow_report(report_start.isoformat(), report_end.isoformat(), status_map[status_label])

    if report_df.empty:
        st.info("ไม่พบข้อมูลตามเงื่อนไขที่เลือก")
        return

    st.dataframe(report_df, use_container_width=True)

    st.markdown("### 4) ส่งออกรายงาน")

    csv_buffer = io.StringIO()
    report_df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="⬇️ ดาวน์โหลดรายงานผู้ยืม–คืน (CSV)",
        data=csv_buffer.getvalue(),
        file_name="borrow_return_report.csv",
        mime="text/csv"
    )

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer) as writer:
        report_df.to_excel(writer, index=False, sheet_name="BorrowReport")
    st.download_button(
        label="⬇️ ดาวน์โหลดรายงานผู้ยืม–คืน (Excel)",
        data=excel_buffer.getvalue(),
        file_name="borrow_return_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    if st.button("🚀 สร้างไฟล์ PDF"):
        try:
            pdf_data = create_pdf(report_df)
            st.download_button(
                label="⬇️ Click เพื่อดาวน์โหลด PDF",
                data=pdf_data,
                file_name="library_report.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {e}")
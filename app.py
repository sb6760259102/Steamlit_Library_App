# app.py
import streamlit as st

from pages import book_page
from pages import borrow_page
from pages import member_page
from pages import admin_page
from pages import login_page
from pages import report_page

#init session สำหรับ login/logout
if "is_logged_in" not in st.session_state:
    st.session_state["is_logged_in"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None

# --- แก้ไขจุดที่ 1: ต้องเรียก set_page_config เป็นอันดับแรก ---
st.set_page_config(page_title="ระบบยืม-คืนหนังสือ", page_icon="📚", layout="wide")

# Login Gate
if not st.session_state["is_logged_in"]:
    login_page.render_login()
    st.stop()

# --- CSS สำหรับซ่อน Sidebar เดิม ---
st.markdown("""
<style>
section[data-testid="stSidebarNav"] {display: none !important;}
div[data-testid="stSidebarNav"] {display: none !important;}
</style>
""", unsafe_allow_html=True)

st.title("📚 ระบบยืม-คืนหนังสือ (Streamlit + SQLite)")
st.write("ตัวอย่าง Web App เชื่อมฐานข้อมูล (ปรับโครงสร้างแบบ MVC เชิงแนวคิด)")

#แสดงผู้ใช้ + ปุ่ม Logout
user = st.session_state.get("user") or {}
st.sidebar.markdown(f"👤 ผู้ใช้: **{user.get('username','-')}**")
st.sidebar.markdown(f"🔑 บทบาท: **{user.get('role','-')}**")

if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state["is_logged_in"] = False
    st.session_state["user"] = None
    st.session_state["page"] = "books"
    st.rerun()

# --- ตรวจสอบ Session State ---
if "page" not in st.session_state:
    st.session_state.page = "books"

# --- ส่วนของเมนู Sidebar ---
st.sidebar.markdown("<h2 style='text-align: center;'>เมนู</h2>", unsafe_allow_html=True)

def nav_button(label, key, icon=""):
    if st.sidebar.button(f"{icon} {label}", use_container_width=True, key=f"btn_{key}"):
        st.session_state.page = key
        st.rerun()

#Role-based menu (มี 2 role คือ admin, staff)
role = user.get("role", "admin")

nav_button("หนังสือ", "books", "📚")
nav_button("สมาชิก", "members", "👤")
nav_button("ยืม-คืน", "borrows", "🔄")

if role == "admin":
    nav_button("จัดการผู้ใช้", "admin", "🛠️")
    nav_button("รายงาน", "reports", "📊")

# --- Routing ---
if st.session_state.page == "books":
    book_page.render_book()
elif st.session_state.page == "members":
    member_page.render_member()
elif st.session_state.page == "admin":
    # ✅ เพิ่มเติม: guard กัน staff เข้าหน้า admin แม้พยายามเปลี่ยน state เอง
    if role != "admin":
        st.warning("⚠ หน้านี้อนุญาตเฉพาะผู้ดูแลระบบ (admin) เท่านั้น")
    else:
        admin_page.render_admin()
elif st.session_state.page == "reports":
    report_page.render_report()
else:
    borrow_page.render_borrow()
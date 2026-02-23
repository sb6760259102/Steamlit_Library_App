import streamlit as st
import model
import controller

# =========================
# View helpers (reset form)
# =========================
def reset_member_form():
    st.session_state["member_code"] = ""
    st.session_state["member_name"] = ""
    st.session_state["gender"] = "ไม่ระบุ"
    st.session_state["member_email"] = ""
    st.session_state["member_phone"] = ""
    # st.session_state["is_active"] = True

# =========================
# UI
# =========================

def render_member():
    if st.session_state.get("_reset_member_next_run", False):
        reset_member_form()
        st.session_state["_reset_member_next_run"] = False


    st.subheader("👤 สมัครสมาชิกใหม่")
    with st.form("member_form"):
        col_a, col_b = st.columns(2)

        with col_a:
            member_code = st.text_input("รหัสสมาชิก (เช่น M001)", max_chars=10, key="member_code")
            member_name = st.text_input("ชื่อ - สกุล", key="member_name")
            gender = st.selectbox("เพศ", ["ไม่ระบุ", "หญิง", "ชาย", "อื่น ๆ"], key="gender")

        with col_b:
            email = st.text_input("อีเมล", key="member_email")
            phone = st.text_input("เบอร์โทรศัพท์", key="member_phone")
            is_active = st.checkbox("ยังใช้งานอยู่", value=True, key="is_active")
            # is_active = st.checkbox("ยังใช้งานอยู่", key="is_active") #เพิ่มการแก้ไขให้ใช้การกำหนดค่าจาก session state ทีเดียว

        btn_col1, btn_col2 = st.columns([1, 3])
        with btn_col1:
            submitted = st.form_submit_button("บันทึกข้อมูลสมาชิก")
        with btn_col2:
            st.form_submit_button("ล้างฟอร์ม", on_click=reset_member_form)

    if "submitted_guard" not in st.session_state:
        st.session_state["submitted_guard"] = False

    if submitted:
        ok, msgs = controller.create_member(member_code, member_name, gender, email, phone, is_active)
        if not ok:
            for m in msgs:
                st.error("⚠ " + m)
        else:
            for m in msgs:
                st.success(m)
            # reset_member_form() #เพิ่มการแก้ไข คอมเมนท์ส่วนนี้
            # ====== set flag+ rerun ======
            st.session_state["_reset_member_next_run"] = True
            st.rerun()
        
        # -------- Members: Read + Delete --------
    st.subheader("📋 รายชื่อสมาชิกทั้งหมด")
    members_df = model.get_all_members()
    if members_df.empty:
        st.info("ยังไม่มีข้อมูลสมาชิกในระบบ")
    else:
        for _, row in members_df.iterrows():
            c1, c2, c3, c4 = st.columns([3, 3, 2, 1])
            with c1:
                st.write(f"**{row['รหัสสมาชิก']}** : {row['ชื่อสกุล']}")
            with c2:
                st.write(row["อีเมล"] if row["อีเมล"] else "-")
            with c3:
                st.write(row["สถานะ"])
            with c4:
                if st.button("ลบ", key=f"delete_member_{row['id']}"):
                    controller.remove_member(int(row["id"]))
                    st.success(f"ลบสมาชิก {row['ชื่อสกุล']} เรียบร้อยแล้ว")
                    st.rerun()

    # -------- Members: Update --------
    st.subheader("✏️ แก้ไขข้อมูลสมาชิก")
    members_df = model.get_all_members()
    if members_df.empty:
        st.info("ยังไม่มีข้อมูลให้แก้ไข")
    else:
        member_options = [
            f"{row['id']} - {row['รหัสสมาชิก']} : {row['ชื่อสกุล']}"
            for _, row in members_df.iterrows()
        ]
        selected = st.selectbox("เลือกสมาชิกที่จะแก้ไข", member_options, key="selected_member")
        selected_id = int(selected.split(" - ")[0])
        selected_row = members_df[members_df["id"] == selected_id].iloc[0]

        with st.form("edit_member_form"):
            col1, col2 = st.columns(2)

            with col1:
                edit_member_code = st.text_input("รหัสสมาชิก", value=selected_row["รหัสสมาชิก"])
                edit_name = st.text_input("ชื่อ - สกุล", value=selected_row["ชื่อสกุล"])
                edit_gender = st.selectbox(
                    "เพศ",
                    ["ไม่ระบุ", "หญิง", "ชาย", "อื่น ๆ"],
                    index=["ไม่ระบุ", "หญิง", "ชาย", "อื่น ๆ"].index(selected_row["เพศ"] if selected_row["เพศ"] else "ไม่ระบุ")
                )

            with col2:
                edit_email = st.text_input("อีเมล", value=selected_row["อีเมล"] if selected_row["อีเมล"] else "")
                edit_phone = st.text_input("เบอร์โทรศัพท์", value=selected_row["เบอร์โทร"] if selected_row["เบอร์โทร"] else "")
                edit_is_active = st.checkbox("ยังใช้งานอยู่", value=(selected_row["สถานะ"] == "ใช้งาน"))

            update_submitted = st.form_submit_button("บันทึกการแก้ไข")

        if update_submitted:
            ok, msgs = controller.edit_member(
                member_id=selected_id,
                new_code=edit_member_code,
                new_name=edit_name,
                gender=edit_gender,
                email=edit_email,
                phone=edit_phone,
                is_active=edit_is_active,
                old_code=selected_row["รหัสสมาชิก"],
                old_email=selected_row["อีเมล"] or ""
            )
            if not ok:
                for m in msgs:
                    st.error("⚠ " + m)
            else:
                for m in msgs:
                    st.success(m)
                st.rerun()
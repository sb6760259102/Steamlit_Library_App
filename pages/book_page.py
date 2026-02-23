import streamlit as st
import model
import controller

# =========================
# View helpers (reset form)
# =========================
def reset_book_form():
    st.session_state["new_title"] = ""
    st.session_state["new_author"] = ""

def on_save_book():
    title = st.session_state.get("new_title", "")
    author = st.session_state.get("new_author", "")
    ok, msgs = controller.create_book(title, author)
    if not ok:
        for m in msgs:
            st.error(m)
    else:
        for m in msgs:
            st.success(m)
        reset_book_form()

# =========================
# UI
# =========================

def render_book():
    # -------- Books: Create --------
    st.subheader("เพิ่มข้อมูลหนังสือใหม่") 
    st.text_input("ชื่อหนังสือ", key="new_title")
    st.text_input("ผู้แต่ง", key="new_author")

    col1, col2 = st.columns([1, 3])
    with col1:
        st.button("บันทึกข้อมูลหนังสือ", on_click=on_save_book)
    with col2:
        st.button("ล้างฟอร์ม", on_click=reset_book_form)

    # -------- Books: Read --------
    st.subheader("รายการหนังสือทั้งหมดในระบบ")
    books_df = model.get_all_books()
    if books_df.empty:
        st.info("ยังไม่มีข้อมูลหนังสือในระบบ")
    else:
        st.dataframe(books_df, use_container_width=True)

    # -------- Books: Delete --------
    st.subheader("ลบข้อมูลหนังสือ")
    books_df = model.get_all_books()
    if books_df.empty:
        st.info("ยังไม่มีข้อมูลหนังสือในระบบ")
    else:
        for _, row in books_df.iterrows():
            c1, c2, c3 = st.columns([4, 3, 1])
            with c1:
                st.write(f"หนังสือ :  **{row['title']}** — {row['author']}")
            with c2:
                st.write(f"รหัสหนังสือ: {row['id']}")
            with c3:
                if st.button("ลบ",key=f"delete_book_{row['id']}"):
                    controller.remove_book(int(row["id"]))
                    st.success("ลบข้อมูลหนังสือเรียบร้อยแล้ว")
                    st.rerun()

    # -------- Books: Update --------
    st.subheader("✏️ แก้ไขข้อมูลหนังสือ")
    if books_df.empty:
        st.info("ยังไม่มีข้อมูลให้แก้ไข")
    else:
        search_title = st.text_input("ค้นหาชื่อหนังสือที่ต้องการแก้ไข", key="search_title")
    if search_title.strip():
        filtered_df = books_df[books_df["title"].str.contains(search_title.strip(),case=False)]
    else:
        filtered_df = books_df
    if filtered_df.empty:
        st.warning("ไม่พบหนังสือตามคำค้นหา")
    else:
        book_options = [f"{row['id']} - {row['title']}"for _, row in filtered_df.iterrows()]
        selected_book = st.selectbox("เลือกหนังสือที่จะแก้ไข", book_options, key="selected_book")
        book_id = int(selected_book.split(" - ")[0])
        selected_row = books_df[books_df["id"] == book_id].iloc[0]

        with st.form("edit_book_form"):
            new_title = st.text_input("ชื่อหนังสือ",value=selected_row["title"])
            new_author = st.text_input("ผู้แต่ง",value=selected_row["author"])
            save_update = st.form_submit_button("บันทึกการแก้ไข")

        if save_update:
            ok, msgs = controller.edit_book(book_id,new_title, new_author)
            if not ok:
                for m in msgs:
                    st.error(m)
            else:
                for m in msgs:
                    st.success(m)
                st.rerun()
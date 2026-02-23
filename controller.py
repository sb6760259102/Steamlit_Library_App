# controller.py
import re
import model

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

# =========================
# Books: validation + actions
# =========================
def validate_book_input(title: str) -> list[str]:
    errors = []
    if title.strip() == "":
        errors.append("⚠ กรุณากรอกชื่อหนังสือ")
    return errors

def create_book(title: str, author: str):
    """คืนค่า (ok:bool, messages:list[str])"""
    errors = validate_book_input(title)
    if errors:
        return False, errors
    model.add_book(title.strip(), author.strip())
    return True, [f"✅ บันทึก '{title.strip()}' สำเร็จแล้ว"]

def edit_book(book_id: int, title: str, author: str):
    errors = validate_book_input(title)
    if errors:
        return False, errors
    model.update_book(book_id, title.strip(), author.strip())
    return True, ["✅ แก้ไขข้อมูลหนังสือเรียบร้อยแล้ว"]

def remove_book(book_id: int):
    model.delete_book(book_id)

# =========================
# Members: validation + actions
# =========================
def validate_member_input(member_code: str, member_name: str, email: str) -> list[str]:
    errors = []
    if member_code.strip() == "":
        errors.append("กรุณากรอก **รหัสสมาชิก**")
    if member_name.strip() == "":
        errors.append("กรุณากรอก **ชื่อ - สกุล**")
    if email.strip() and not re.match(EMAIL_PATTERN, email.strip()):
        errors.append("รูปแบบ **อีเมลไม่ถูกต้อง**")
    return errors

def create_member(member_code: str, member_name: str, gender: str, email: str, phone: str, is_active: bool):
    errors = validate_member_input(member_code, member_name, email)

    # ตรวจซ้ำ
    if member_code.strip() and model.is_member_code_exists(member_code.strip()):
        errors.append(f"รหัสสมาชิก **{member_code.strip()}** มีอยู่แล้วในระบบ")
    if email.strip() and model.is_email_exists(email.strip()):
        errors.append(f"อีเมล **{email.strip()}** ถูกใช้สมัครแล้ว")

    if errors:
        return False, errors

    model.add_member(
        member_code.strip(),
        member_name.strip(),
        gender,
        email.strip(),
        phone.strip(),
        is_active
    )
    return True, [f"✅ บันทึกข้อมูลสมาชิก '{member_name.strip()}' สำเร็จแล้ว"]

def edit_member(
    member_id: int,
    new_code: str,
    new_name: str,
    gender: str,
    email: str,
    phone: str,
    is_active: bool,
    old_code: str,
    old_email: str
):
    errors = validate_member_input(new_code, new_name, email)

    # ตรวจซ้ำ (ยกเว้นแถวเดิม)
    if new_code.strip() and new_code.strip() != (old_code or "") and model.is_member_code_exists(new_code.strip()):
        errors.append(f"รหัสสมาชิก **{new_code.strip()}** มีอยู่แล้วในระบบ")

    if email.strip():
        old_email = old_email or ""
        if email.strip() != old_email and model.is_email_exists(email.strip()):
            errors.append(f"อีเมล **{email.strip()}** ถูกใช้สมัครแล้ว")

    if errors:
        return False, errors

    model.update_member(
        member_id,
        new_code.strip(),
        new_name.strip(),
        gender,
        email.strip(),
        phone.strip(),
        is_active
    )
    return True, ["✅ แก้ไขข้อมูลสมาชิกเรียบร้อยแล้ว"]

def remove_member(member_id: int):
    model.delete_member(member_id)

#################################################
#  user login
################################################
# --- เพิ่มท้ายไฟล์ controller.py ---
import hashlib

def _hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def login(username: str, password: str):
    """
    Controller-level login
    return: (ok:bool, messages:list[str], user_info:dict|None)
    user_info: {"id":.., "username":.., "role":..}
    """
    errors = []
    if not username.strip():
        errors.append("กรุณากรอก **ชื่อผู้ใช้**")
    if not password.strip():
        errors.append("กรุณากรอก **รหัสผ่าน**")
    if errors:
        return False, errors, None
    
    u = model.get_user_auth_row(username)
    if not u:
        return False, ["⚠ ไม่พบบัญชีผู้ใช้นี้ในระบบ"], None
    if u["is_active"] != 1:
        return False, ["⚠ บัญชีนี้ถูกปิดใช้งาน กรุณาติดต่อผู้ดูแลระบบ"], None
    if _hash_password(password) != u["password_hash"]:
        return False, ["⚠ รหัสผ่านไม่ถูกต้อง"], None
    
    user_info = {"id": u["id"], "username": u["username"], "role": u["role"]}
    return True, ["✅ เข้าสู่ระบบสำเร็จ"], user_info

# -------- Admin actions --------
def create_user(username: str, password: str, role: str, is_active: bool = True):
    errors = []
    if not username.strip():
        errors.append("กรุณากรอก **ชื่อผู้ใช้**")
    if len(username.strip()) < 3:
        errors.append("ชื่อผู้ใช้ต้องมีอย่างน้อย 3 ตัวอักษร")
    if not password.strip():
        errors.append("กรุณากรอก **รหัสผ่าน**")
    if len(password.strip()) < 4:
        errors.append("รหัสผ่านต้องมีอย่างน้อย 4 ตัวอักษร")
    if role not in ("admin", "staff"):
        errors.append("role ต้องเป็น admin หรือ staff")
    if username.strip() and model.is_username_exists(username.strip()):
        errors.append(f"ชื่อผู้ใช้ **{username.strip()}** มีอยู่แล้ว")
    if errors:
        return False, errors
    
    model.add_user(
        username=username.strip(),
        password_hash=_hash_password(password),
        role=role,
        is_active=1 if is_active else 0
    )
    return True, [f"✅ เพิ่มผู้ใช้ '{username.strip()}' เรียบร้อยแล้ว"]

def set_user_role(user_id: int, new_role: str, current_username: str):
    # กันลดสิทธิ์ตัวเองแบบง่าย ๆ
    if new_role not in ("admin", "staff"):
        return False, ["role ต้องเป็น admin หรือ staff"]

    users_df = model.get_all_users()
    me = users_df[users_df["username"] == current_username]
    if not me.empty and int(me.iloc[0]["id"]) == int(user_id) and new_role != "admin":
        return False, ["ไม่อนุญาตให้ลดสิทธิ์ของผู้ดูแลระบบที่กำลังล็อกอินอยู่"]

    model.update_user_role(int(user_id), new_role)
    return True, ["✅ เปลี่ยน role เรียบร้อยแล้ว"]

def set_user_active(user_id: int, is_active: bool, current_username: str):
    # กันปิดตัวเอง
    users_df = model.get_all_users()
    me = users_df[users_df["username"] == current_username]
    if not me.empty and int(me.iloc[0]["id"]) == int(user_id) and (not is_active):
        return False, ["ไม่อนุญาตให้ปิดใช้งานบัญชีที่กำลังล็อกอินอยู่"]

    model.update_user_active(int(user_id), 1 if is_active else 0)
    return True, ["✅ เปลี่ยนสถานะผู้ใช้เรียบร้อยแล้ว"]

# ============================================================
# Borrow: multi-book per transaction
# ============================================================
def borrow_books(member_id: int, staff_user_id: int, due_date_iso: str | None, book_ids: list[int], note: str | None = None):
    """
    สร้างรายการยืม 1 ครั้ง (หลายเล่ม)
    - ต้องระบุ staff_user_id เพื่อบันทึกว่าใครเป็นผู้ทำรายการ
    """
    errors = []
    if not member_id:
        errors.append("กรุณาเลือกสมาชิก")
    if not staff_user_id:
        errors.append("ไม่พบข้อมูลผู้ทำรายการ (กรุณาเข้าสู่ระบบใหม่)")
    if not book_ids:
        errors.append("กรุณาเลือกหนังสืออย่างน้อย 1 เล่ม")
    if errors:
        return False, errors, None

    try:
        tx_id = model.create_borrow_transaction(
            member_id=int(member_id),
            staff_user_id=int(staff_user_id),
            default_due_date=due_date_iso,
            book_ids=[int(x) for x in book_ids],
            note=note
        )
        return True, [f"บันทึกการยืมเรียบร้อยแล้ว (TX: {tx_id})"], tx_id
    except Exception as e:
        return False, [f"ไม่สามารถบันทึกการยืมได้: {e}"], None

def return_book_item(item_id: int, return_staff_user_id: int):
    """คืนหนังสือทีละเล่ม พร้อมบันทึกผู้ทำรายการคืน"""
    if not item_id:
        return False, ["กรุณาเลือกรายการที่จะคืน"]
    if not return_staff_user_id:
        return False, ["ไม่พบข้อมูลผู้ทำรายการ (กรุณาเข้าสู่ระบบใหม่)"]

    ok = model.return_borrow_item(int(item_id), int(return_staff_user_id))
    if not ok:
        return False, ["ไม่พบรายการที่ยังไม่คืน หรือรายการถูกคืนแล้ว"]
    return True, ["บันทึกการคืนเรียบร้อยแล้ว"]

def return_book_items(item_ids: list[int], return_staff_user_id: int):
    """
    คืนหนังสือหลายรายการ (ติ๊กได้หลายเล่ม) พร้อมบันทึกผู้ทำรายการคืน
    return: (ok:bool, messages:list[str])
    """
    if not item_ids:
        return False, ["กรุณาเลือกรายการที่จะคืนอย่างน้อย 1 รายการ"]
    if not return_staff_user_id:
        return False, ["ไม่พบข้อมูลผู้ทำรายการ (กรุณาเข้าสู่ระบบใหม่)"]

    success = 0
    failed = []

    for item_id in item_ids:
        try:
            ok = model.return_borrow_item(int(item_id), int(return_staff_user_id))
            if ok:
                success += 1
            else:
                failed.append(int(item_id))
        except Exception:
            failed.append(int(item_id))

    msgs = [f"บันทึกการคืนสำเร็จ {success} รายการ"]
    if failed:
        msgs.append(f"รายการที่คืนไม่สำเร็จ/ถูกคืนแล้ว: {failed}")

    return True, msgs
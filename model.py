# model.py
import sqlite3
import pandas as pd

DB_PATH = "library.db"

def get_connection():
    """สร้างการเชื่อมต่อฐานข้อมูล SQLite"""
    return sqlite3.connect(DB_PATH)

# =========================
# Books (CRUD)
# =========================
def add_book(title: str, author: str):
    """เพิ่มหนังสือใหม่"""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO books (title, author) VALUES (?, ?)",
        (title, author)
    )
    conn.commit()
    conn.close()

def get_all_books() -> pd.DataFrame:
    """อ่านรายการหนังสือทั้งหมด"""
    conn = get_connection()
    df = pd.read_sql_query("SELECT id, title, author FROM books", conn)
    conn.close()
    return df

def delete_book(book_id: int):
    """ลบหนังสือตาม id"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()

def update_book(book_id: int, title: str, author: str):
    """แก้ไขหนังสือตาม id"""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """
        UPDATE books
        SET title = ?, author = ?
        WHERE id = ?
        """,
        (title, author, book_id)
    )
    conn.commit()
    conn.close()

# =========================
# Members (CRUD + Checks)
# =========================
def add_member(member_code: str, name: str, gender: str, email: str, phone: str, is_active: bool = True):
    """เพิ่มสมาชิกใหม่"""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO members (member_code, name, gender, email, phone, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (member_code, name, gender, email, phone, 1 if is_active else 0)
    )
    conn.commit()
    conn.close()

def get_all_members() -> pd.DataFrame:
    """อ่านข้อมูลสมาชิกทั้งหมด (จัดชื่อคอลัมน์สำหรับแสดงผล)"""
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT
            id,
            member_code AS รหัสสมาชิก,
            name        AS ชื่อสกุล,
            gender      AS เพศ,
            email       AS อีเมล,
            phone       AS เบอร์โทร,
            CASE is_active WHEN 1 THEN 'ใช้งาน' ELSE 'ยกเลิก' END AS สถานะ
        FROM members
        ORDER BY id DESC
        """,
        conn
    )
    conn.close()
    return df

def delete_member(member_id: int):
    """ลบสมาชิกตาม id"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM members WHERE id = ?", (member_id,))
    conn.commit()
    conn.close()

def update_member(member_id: int, member_code: str, name: str, gender: str, email: str, phone: str, is_active: bool):
    """แก้ไขข้อมูลสมาชิกตาม id"""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        """
        UPDATE members
        SET member_code = ?,
            name        = ?,
            gender      = ?,
            email       = ?,
            phone       = ?,
            is_active   = ?
        WHERE id = ?
        """,
        (member_code, name, gender, email, phone, 1 if is_active else 0, member_id)
    )
    conn.commit()
    conn.close()

def is_member_code_exists(member_code: str) -> bool:
    """ตรวจรหัสสมาชิกซ้ำ"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM members WHERE member_code = ?", (member_code,))
    (count,) = c.fetchone()
    conn.close()
    return count > 0

def is_email_exists(email: str) -> bool:
    """ตรวจอีเมลซ้ำ (ถ้า email ว่างให้ถือว่าไม่ซ้ำ)"""
    if not email:
        return False
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM members WHERE email = ?", (email,))
    (count,) = c.fetchone()
    conn.close()
    return count > 0

#################################################
#user login
################################################
def get_user_auth_row(username: str):
    """
    ดึงข้อมูลสำหรับตรวจสอบ login (DB only)
    return: dict หรือ None
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute(
    "SELECT id, username, password_hash, role FROM users WHERE username = ?",
    (username.strip(),)
    )
    row = c.fetchone()
    conn.close()

    if not row:
        return None
    user_id, uname, pw_hash, role = row
    return {"id": user_id, "username": uname, "password_hash": pw_hash, "role": role}

###########################################
# manage user role
###########################################
def get_user_auth_row(username: str):
    """ดึงข้อมูล user สำหรับ login (DB-only)"""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT id, username, password_hash, role, is_active FROM users WHERE username = ?",
        (username.strip(),)
    )
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    user_id, uname, pw_hash, role, is_active = row
    return {
        "id": user_id,
        "username": uname,
        "password_hash": pw_hash,
        "role": role,
        "is_active": int(is_active)
    }


def get_all_users():
    """ดึง users ทั้งหมดเพื่อแสดงในหน้า admin"""
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT id, username, role,
        CASE is_active WHEN 1 THEN 'ใช้งาน' ELSE 'ปิดใช้งาน' END AS สถานะ
        FROM users
        ORDER BY id DESC
        """, conn
        )
    conn.close()
    return df

##### 20260202 เพิ่มกาารตรวจ members
def get_active_members() -> pd.DataFrame:
    """ดึงสมาชิกที่ยังใช้งานอยู่ (is_active = 1)"""
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT id, member_code, name
        FROM members
        WHERE is_active = 1
        ORDER BY id DESC
        """,
        conn
    )
    conn.close()
    return df
#################################

def is_username_exists(username: str) -> bool:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username.strip(),))
    (count,) = c.fetchone()
    conn.close()
    return count > 0

def add_user(username: str, password_hash: str, role: str, is_active: int = 1):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (username, password_hash, role, is_active) VALUES (?, ?, ?, ?)",
        (username.strip(), password_hash, role, int(is_active))
    )
    conn.commit()
    conn.close()

def update_user_role(user_id: int, new_role: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
    conn.commit()
    conn.close()

def update_user_active(user_id: int, is_active: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET is_active = ? WHERE id = ?", (int(is_active), user_id))
    conn.commit()
    conn.close()

# ============================================================
# สร้างตารางยืม คืน Schema: Borrow (Header-Detail)
# ============================================================
def ensure_borrow_schema():
    """
    สร้างตารางสำหรับงานยืม-คืน (รองรับยืม 1 ครั้งหลายเล่ม) หากยังไม่มี
    - borrow_tx: หัวรายการ (ใครยืม / ใครทำรายการ / เมื่อไหร่ / กำหนดส่ง)
    - borrow_items: รายการย่อย (หนังสือแต่ละเล่ม + สถานะคืนรายเล่ม + ผู้ทำรายการคืน)
    """
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS borrow_tx (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER NOT NULL,
    staff_user_id INTEGER NOT NULL,
    borrow_date TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    default_due_date TEXT,
    status TEXT NOT NULL DEFAULT 'open',
    note TEXT,
    FOREIGN KEY (member_id) REFERENCES members(id),
    FOREIGN KEY (staff_user_id) REFERENCES users(id)
    )
    """)


    c.execute("""
    CREATE TABLE IF NOT EXISTS borrow_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tx_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    due_date TEXT,
    return_date TEXT,
    status TEXT NOT NULL DEFAULT 'borrowed',
    return_staff_user_id INTEGER,
    FOREIGN KEY (tx_id) REFERENCES borrow_tx(id),
    FOREIGN KEY (book_id) REFERENCES books(id),
    FOREIGN KEY (return_staff_user_id) REFERENCES users(id)
    )
    """)

    c.execute("CREATE INDEX IF NOT EXISTS idx_borrow_items_tx ON borrow_items(tx_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_borrow_items_book ON borrow_items(book_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_borrow_items_status ON borrow_items(status)")

    conn.commit()
    conn.close()

# ============================================================
# จัดการยืมคืน หนังสือ
# ============================================================
def set_book_status(book_id: int, status: str):
    """อัปเดตสถานะหนังสือ: available / borrowed"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE books SET status = ? WHERE id = ?", (status, int(book_id)))
    conn.commit()
    conn.close()

def get_available_books() -> pd.DataFrame:
    """ดึงเฉพาะหนังสือที่พร้อมให้ยืม (status='available')"""
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT id, title, author FROM books WHERE status = 'available' ORDER BY id DESC",
        conn
    )
    conn.close()
    return df

# ============================================================
# Borrow operations (Multi-book per transaction)
# ============================================================
def create_borrow_transaction(member_id: int, staff_user_id: int, default_due_date: str | None, book_ids: list[int], note: str | None = None):
    """
    สร้างธุรกรรมการยืม 1 ครั้ง (ยืมได้หลายเล่ม)
    เงื่อนไข:
    - หนังสือทุกเล่มต้องมีสถานะ available
    - หลังบันทึก ต้องอัปเดต books.status = borrowed
    """
    ensure_borrow_schema()


    if not book_ids:
        raise ValueError("ต้องระบุรายการหนังสืออย่างน้อย 1 เล่ม")


    conn = get_connection()
    c = conn.cursor()


    try:
        # ตรวจสอบสถานะหนังสือทั้งหมดก่อน
        q_marks = ",".join(["?"] * len(book_ids))
        c.execute(f"SELECT id, status FROM books WHERE id IN ({q_marks})", tuple(map(int, book_ids)))
        rows = c.fetchall()


        found_ids = {int(r[0]) for r in rows}
        missing = [bid for bid in book_ids if int(bid) not in found_ids]
        if missing:
            raise ValueError(f"ไม่พบหนังสือ id: {missing}")


        not_available = [int(r[0]) for r in rows if (r[1] or "").lower() != "available"]
        if not_available:
            raise ValueError(f"หนังสือบางเล่มไม่พร้อมให้ยืม (status ไม่ใช่ available): {not_available}")


        # เริ่ม transaction
        conn.execute("BEGIN")


        # 1) insert header
        c.execute(
            """
            INSERT INTO borrow_tx (member_id, staff_user_id, default_due_date, status, note)
            VALUES (?, ?, ?, 'open', ?)
            """,
            (int(member_id), int(staff_user_id), default_due_date, note)
        )
        tx_id = c.lastrowid


        # 2) insert items + update book status
        for bid in book_ids:
            c.execute(
                """
                INSERT INTO borrow_items (tx_id, book_id, due_date, status)
                VALUES (?, ?, ?, 'borrowed')
                """,
                (int(tx_id), int(bid), default_due_date)
            )
            c.execute("UPDATE books SET status = 'borrowed' WHERE id = ?", (int(bid),))


        conn.commit()
        return int(tx_id)


    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_active_borrow_items() -> pd.DataFrame:
    """ดึงรายการหนังสือที่กำลังถูกยืมอยู่ (ยังไม่คืน) เพื่อแสดงในหน้า UI"""
    ensure_borrow_schema()
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT
            bi.id AS item_id,
            tx.id AS tx_id,
            m.member_code AS รหัสสมาชิก,
            m.name AS ชื่อสมาชิก,
            bk.id AS รหัสหนังสือ,
            bk.title AS ชื่อหนังสือ,
            tx.borrow_date AS วันที่ยืม,
            bi.due_date AS กำหนดส่ง,
            u.username AS ผู้ทำรายการยืม,
            u.role AS บทบาทผู้ทำรายการ
        FROM borrow_items bi
        JOIN borrow_tx tx ON tx.id = bi.tx_id
        JOIN members m ON m.id = tx.member_id
        JOIN books bk ON bk.id = bi.book_id
        JOIN users u ON u.id = tx.staff_user_id
        WHERE bi.status = 'borrowed'
        ORDER BY bi.id DESC
        """,
        conn
    )
    conn.close()
    return df


def get_active_borrow_items_by_member(member_id: int) -> pd.DataFrame:
    """
    ดึงรายการหนังสือที่กำลังถูกยืมอยู่ (ยังไม่คืน) เฉพาะสมาชิก 1 คน
    ใช้ในหน้า 'คืน' เพื่อดูรายการค้างส่งแบบกรองตามสมาชิก
    """
    ensure_borrow_schema()
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT
            bi.id AS item_id,
            tx.id AS tx_id,
            m.member_code AS รหัสสมาชิก,
            m.name AS ชื่อสมาชิก,
            bk.id AS รหัสหนังสือ,
            bk.title AS ชื่อหนังสือ,
            tx.borrow_date AS วันที่ยืม,
            bi.due_date AS กำหนดส่ง,
            u.username AS ผู้ทำรายการยืม,
            u.role AS บทบาทผู้ทำรายการ
        FROM borrow_items bi
        JOIN borrow_tx tx ON tx.id = bi.tx_id
        JOIN members m ON m.id = tx.member_id
        JOIN books bk ON bk.id = bi.book_id
        JOIN users u ON u.id = tx.staff_user_id
        WHERE bi.status = 'borrowed'
        AND m.id = ?
        ORDER BY bi.id DESC
        """,
        conn,
        params=(int(member_id),)
    )
    conn.close()
    return df

def return_borrow_item(item_id: int, return_staff_user_id: int) -> bool:
    """
    คืนหนังสือรายเล่ม:
    - อัปเดต borrow_items.return_date + status + return_staff_user_id
    - อัปเดต books.status = available
    - หากใน tx เดียวกันไม่มี item ค้างแล้ว ให้ปิด tx (status=closed)
    """
    ensure_borrow_schema()
    conn = get_connection()
    c = conn.cursor()

    try:
        conn.execute("BEGIN")

        # หา book_id + tx_id ที่ยังค้าง
        c.execute(
            "SELECT tx_id, book_id FROM borrow_items WHERE id = ? AND status = 'borrowed'",
            (int(item_id),)
        )
        row = c.fetchone()
        if not row:
            conn.rollback()
            return False

        tx_id, book_id = int(row[0]), int(row[1])

        c.execute(
            """
            UPDATE borrow_items
            SET status = 'returned',
                return_date = CURRENT_TIMESTAMP,
                return_staff_user_id = ?
            WHERE id = ?
            """,
            (int(return_staff_user_id), int(item_id))
        )

        c.execute("UPDATE books SET status = 'available' WHERE id = ?", (int(book_id),))

        # ถ้าไม่มีรายการค้างใน tx นี้แล้ว -> ปิดหัวรายการ
        c.execute("SELECT COUNT(*) FROM borrow_items WHERE tx_id = ? AND status = 'borrowed'", (int(tx_id),))
        (remain,) = c.fetchone()
        if int(remain) == 0:
            c.execute("UPDATE borrow_tx SET status = 'closed' WHERE id = ?", (int(tx_id),))

        conn.commit()
        return True

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def get_borrow_history(limit: int = 200) -> pd.DataFrame:
    """ประวัติการยืม-คืน (รวมข้อมูลผู้ทำรายการยืมและผู้ทำรายการคืน)"""
    # ensure_borrow_schema()
    conn = get_connection()
    df = pd.read_sql_query(
        f"""
        SELECT
            bi.id AS item_id,
            tx.id AS tx_id,
            m.member_code AS รหัสสมาชิก,
            m.name AS ชื่อสมาชิก,
            bk.id AS รหัสหนังสือ,
            bk.title AS ชื่อหนังสือ,
            tx.borrow_date AS วันที่ยืม,
            bi.due_date AS กำหนดส่ง,
            bi.return_date AS วันที่คืน,
            bi.status AS สถานะ,
            u1.username AS ผู้ทำรายการยืม,
            u1.role AS บทบาทผู้ทำรายการยืม,
            u2.username AS ผู้ทำรายการคืน
        FROM borrow_items bi
        JOIN borrow_tx tx ON tx.id = bi.tx_id
        JOIN members m ON m.id = tx.member_id
        JOIN books bk ON bk.id = bi.book_id
        JOIN users u1 ON u1.id = tx.staff_user_id
        LEFT JOIN users u2 ON u2.id = bi.return_staff_user_id
        ORDER BY bi.id DESC
        LIMIT {int(limit)}
        """,
        conn
    )
    conn.close()
    return df

############ ดึงข้อมูลสถานะหนังสือทั้งหมด ##############
def get_book_status_summary():
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT
            status AS สถานะหนังสือ,
            COUNT(*) AS จำนวน
        FROM books
        GROUP BY status
        """,
        conn
    )
    conn.close()
    return df

############## ดึงข้อมูล จำนวนการยืมรายเดือน ######
def get_borrow_summary_by_month(start_date: str, end_date: str):
    """
    สรุปจำนวนการยืมรายเดือน
    """
    conn = get_connection()
    sql = """
        SELECT
            strftime('%Y-%m', borrow_date) AS เดือน,
            COUNT(*) AS จำนวนการยืม
        FROM borrow_tx
        WHERE DATE(borrow_date) BETWEEN ? AND ?
        GROUP BY strftime('%Y-%m', borrow_date)
        ORDER BY เดือน
    """
    df = pd.read_sql_query(sql, conn, params=[start_date, end_date])
    conn.close()
    return df

######### ดึงข้อมูลรายงานการยืม-คืน ทั้งหมด กรองตามช่วงเวลา ###
def get_borrow_report(start_date: str, end_date: str, status: str):
    """
    รายงานการยืม-คืนทั้งหมด
    - กรองตามช่วงเวลา
    - กรองตามสถานะ borrowed / returned / all
    """
    conn = get_connection()

    base_sql = """
        SELECT
            m.member_code AS รหัสสมาชิก,
            m.name AS ชื่อสมาชิก,
            bk.title AS ชื่อหนังสือ,
            tx.borrow_date AS วันที่ยืม,
            bi.due_date AS กำหนดส่ง,
            bi.return_date AS วันที่คืน,
            bi.status AS สถานะ,
            u1.username AS ผู้ทำรายการยืม,
            u2.username AS ผู้ทำรายการคืน
        FROM borrow_items bi
        JOIN borrow_tx tx ON tx.id = bi.tx_id
        JOIN members m ON m.id = tx.member_id
        JOIN books bk ON bk.id = bi.book_id
        JOIN users u1 ON u1.id = tx.staff_user_id
        LEFT JOIN users u2 ON u2.id = bi.return_staff_user_id
        WHERE DATE(tx.borrow_date) BETWEEN ? AND ?
    """

    params = [start_date, end_date]

    if status != "all":
        base_sql += " AND bi.status = ?"
        params.append(status)

    base_sql += " ORDER BY tx.borrow_date DESC"

    df = pd.read_sql_query(base_sql, conn, params=params)
    conn.close()
    return df


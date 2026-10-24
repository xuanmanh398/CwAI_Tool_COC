import customtkinter as ctk
import mysql.connector
import random
import string
from datetime import datetime, timedelta

# ===== KẾT NỐI DATABASE =====
try:
    db = mysql.connector.connect(
        host="157.66.224.95",
        user="root",
        password="",
        database="tool_keys"
    )
    cursor = db.cursor()

except:
    print("Không kết nối được database")
    exit()

# ===== TẠO KEY NGẪU NHIÊN =====
def generate_key():

    chars = string.ascii_uppercase + string.digits

    return "-".join(
        "".join(random.choice(chars) for _ in range(5))
        for _ in range(4)
    )


# ===== LOAD KEY =====
def load_keys():

    listbox.delete("1.0", "end")

    cursor.execute("""
        SELECT id, license_key, created_at, expire_at, status
        FROM license_keys
        ORDER BY id ASC
    """)

    rows = cursor.fetchall()

    for row in rows:

        id = row[0]
        key = row[1]
        created = row[2]
        expire = row[3]
        status = row[4]

        text = f"{id} | {key} | CREATED:{created} | EXPIRE:{expire} | STATUS:{status}"

        listbox.insert("end", text + "\n")


# ===== THÊM KEY =====
def add_key():

    try:

        key = generate_key()

        days = int(days_entry.get())
        devices = int(device_entry.get())

        if permanent_var.get() == 1:
            expire = None
            permanent = 1
        else:
            expire = datetime.now() + timedelta(days=days)
            permanent = 0

        sql = """
        INSERT INTO license_keys
        (license_key,expire_at,is_permanent,max_devices)
        VALUES (%s,%s,%s,%s)
        """

        cursor.execute(sql, (key, expire, permanent, devices))
        db.commit()

        load_keys()

    except:
        print("Lỗi tạo key")


# ===== LẤY ID TỪ DÒNG =====
def get_selected_id():

    try:

        line = listbox.get("insert linestart", "insert lineend")

        id = line.split("|")[0].strip()

        return id

    except:
        return None


# ===== DELETE =====
def delete_key():

    id = get_selected_id()

    if id:

        cursor.execute("DELETE FROM license_keys WHERE id=%s", (id,))
        db.commit()

        load_keys()


# ===== LOCK =====
def lock_key():

    id = get_selected_id()

    if id:

        cursor.execute("UPDATE license_keys SET status='locked' WHERE id=%s", (id,))
        db.commit()

        load_keys()


# ===== UNLOCK =====
def unlock_key():

    id = get_selected_id()

    if id:

        cursor.execute("UPDATE license_keys SET status='active' WHERE id=%s", (id,))
        db.commit()

        load_keys()


# ===== UI =====

ctk.set_appearance_mode("dark")

app = ctk.CTk()
app.geometry("800x600")
app.title("KEY MANAGER")


title = ctk.CTkLabel(app, text="KEY MANAGER", font=("Arial", 30))
title.pack(pady=20)


frame = ctk.CTkFrame(app)
frame.pack(pady=10)


ctk.CTkLabel(frame, text="Days").grid(row=0, column=0, padx=5)

days_entry = ctk.CTkEntry(frame, width=80)
days_entry.insert(0, "30")
days_entry.grid(row=0, column=1)


ctk.CTkLabel(frame, text="Devices").grid(row=0, column=2, padx=5)

device_entry = ctk.CTkEntry(frame, width=80)
device_entry.insert(0, "1")
device_entry.grid(row=0, column=3)


permanent_var = ctk.IntVar()

permanent_box = ctk.CTkCheckBox(
    frame,
    text="Permanent",
    variable=permanent_var
)

permanent_box.grid(row=0, column=4, padx=10)


add_btn = ctk.CTkButton(
    frame,
    text="Generate Key",
    command=add_key
)

add_btn.grid(row=0, column=5, padx=10)


listbox = ctk.CTkTextbox(
    app,
    width=700,
    height=300
)

listbox.pack(pady=20)


btn_frame = ctk.CTkFrame(app)
btn_frame.pack()


delete_btn = ctk.CTkButton(
    btn_frame,
    text="Delete",
    command=delete_key
)

delete_btn.grid(row=0, column=0, padx=10)


lock_btn = ctk.CTkButton(
    btn_frame,
    text="Lock",
    command=lock_key
)

lock_btn.grid(row=0, column=1, padx=10)


unlock_btn = ctk.CTkButton(
    btn_frame,
    text="Unlock",
    command=unlock_key
)

unlock_btn.grid(row=0, column=2, padx=10)


refresh_btn = ctk.CTkButton(
    btn_frame,
    text="Refresh",
    command=load_keys
)

refresh_btn.grid(row=0, column=3, padx=10)


load_keys()

app.mainloop()
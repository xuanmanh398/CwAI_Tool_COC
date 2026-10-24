import customtkinter as ctk
import requests
import panel   # import file panel.py

ctk.set_appearance_mode("dark")

API_URL = "http://157.66.224.95/checkkey.php?key="


def login():

    key = key_entry.get().strip()

    if key == "":
        status.configure(text="Vui lòng nhập key", text_color="orange")
        return

    try:

        r = requests.get(API_URL + key, timeout=5)

        result = r.text.strip()

        if result == "valid":

            status.configure(text="Key hợp lệ", text_color="green")
            app.after(500, open_panel)

        elif result == "invalid":

            status.configure(text="Key không tồn tại", text_color="red")

        elif result == "locked":

            status.configure(text="Key đã bị khóa", text_color="red")

        elif result == "expired":

            status.configure(text="Key đã hết hạn", text_color="red")

        elif result == "device_full":

            status.configure(text="Key đã hết lượt thiết bị", text_color="red")

        elif result == "spam":

            status.configure(text="Bạn thao tác quá nhanh", text_color="orange")

        else:

            status.configure(text="Server lỗi", text_color="red")

    except:

        status.configure(text="Không kết nối được server", text_color="red")


def open_panel():

    app.destroy()

    # gọi panel
    panel.start_panel()


app = ctk.CTk()
app.geometry("420x340")
app.title("Login Key")

title = ctk.CTkLabel(app, text="NHẬP KEY", font=("Arial", 26))
title.pack(pady=25)

key_entry = ctk.CTkEntry(app, width=260, placeholder_text="Nhập KEY")
key_entry.pack(pady=10)

login_btn = ctk.CTkButton(app, text="Đăng nhập", command=login, width=200)
login_btn.pack(pady=10)

status = ctk.CTkLabel(app, text="")
status.pack(pady=10)

contact = ctk.CTkLabel(
    app,
    text="Mua key liên hệ Zalo: 0963913615",
    font=("Arial", 13),
    text_color="#AAAAAA"
)
contact.pack(pady=25)

app.mainloop()
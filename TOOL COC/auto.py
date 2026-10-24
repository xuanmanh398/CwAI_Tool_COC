import customtkinter as ctk
import pyautogui
import threading
import time
import os
import webbrowser
from tkinter import filedialog
from PIL import Image

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

image_folder = "images"
special_image = None

running = False
paused = False

if not os.path.exists(image_folder):
    os.makedirs(image_folder)


# ================= AUTO CLICK =================

def auto_click():

    global running, paused

    while running:

        if paused:
            time.sleep(0.5)
            continue

        images = os.listdir(image_folder)

        for img in images:

            path = os.path.join(image_folder, img)

            try:

                location = pyautogui.locateOnScreen(
                    path,
                    confidence=0.9
                )

                if location:

                    if img == special_image:

                        pyautogui.hotkey("ctrl", "z")
                        status_label.configure(
                            text=f"Special detected: {img} → CTRL+Z"
                        )

                    else:

                        pyautogui.click(pyautogui.center(location))
                        status_label.configure(
                            text=f"Click: {img}"
                        )

                    time.sleep(0.5)

            except:
                pass

        time.sleep(0.3)


# ================= CONTROL =================

def start():

    global running

    if not running:

        running = True

        threading.Thread(
            target=auto_click,
            daemon=True
        ).start()

        status_label.configure(text="Running...")


def pause():

    global paused

    paused = not paused

    if paused:
        status_label.configure(text="Paused")
    else:
        status_label.configure(text="Running...")


def stop():

    global running

    running = False
    status_label.configure(text="Stopped")


# ================= IMAGE FUNCTIONS =================

def add_image():

    file = filedialog.askopenfilename(
        filetypes=[("PNG Image", "*.png")]
    )

    if file:

        name = os.path.basename(file)

        new_path = os.path.join(image_folder, name)

        with open(file, "rb") as src:
            with open(new_path, "wb") as dst:
                dst.write(src.read())

        refresh_images()

        status_label.configure(text=f"Added: {name}")


def delete_image(path):

    os.remove(path)

    refresh_images()

    status_label.configure(text="Image deleted")


def view_images():

    win = ctk.CTkToplevel(app)
    win.title("Image Manager")
    win.geometry("450x450")

    images = os.listdir(image_folder)

    for img in images:

        frame = ctk.CTkFrame(win)
        frame.pack(pady=5, padx=10, fill="x")

        path = os.path.join(image_folder, img)

        image = Image.open(path)
        image = image.resize((60, 60))

        photo = ctk.CTkImage(light_image=image, size=(60,60))

        label = ctk.CTkLabel(
            frame,
            text=img,
            image=photo,
            compound="left"
        )
        label.pack(side="left", padx=10)

        delete_btn = ctk.CTkButton(
            frame,
            text="Delete",
            width=70,
            command=lambda p=path: delete_image(p)
        )
        delete_btn.pack(side="right", padx=10)


# ================= SPECIAL IMAGE =================

def set_special():

    global special_image

    special_image = image_option.get()

    status_label.configure(
        text=f"Special image: {special_image}"
    )


def refresh_images():

    imgs = os.listdir(image_folder)

    if imgs:

        image_option.configure(values=imgs)
        image_option.set(imgs[0])


# ================= GUIDE =================

def open_guide():

    webbrowser.open("https://your-website.com/huongdan")


# ================= GUI =================

app = ctk.CTk()

app.title("AUTO CLICK TOOL")

app.geometry("600x650")

title = ctk.CTkLabel(
    app,
    text="AUTO CLICK TOOL",
    font=("Arial", 28)
)
title.pack(pady=20)


status_label = ctk.CTkLabel(
    app,
    text="Ready",
    font=("Arial", 14)
)
status_label.pack(pady=10)


# ===== CONTROL BUTTONS =====

start_btn = ctk.CTkButton(
    app,
    text="Start",
    width=200,
    command=start
)
start_btn.pack(pady=8)

pause_btn = ctk.CTkButton(
    app,
    text="Pause",
    width=200,
    command=pause
)
pause_btn.pack(pady=8)

stop_btn = ctk.CTkButton(
    app,
    text="Stop",
    width=200,
    command=stop
)
stop_btn.pack(pady=8)


# ===== IMAGE MANAGER =====

ctk.CTkLabel(
    app,
    text="Image Manager",
    font=("Arial", 18)
).pack(pady=15)

add_btn = ctk.CTkButton(
    app,
    text="Add Image",
    width=200,
    command=add_image
)
add_btn.pack(pady=6)

view_btn = ctk.CTkButton(
    app,
    text="View / Delete Images",
    width=200,
    command=view_images
)
view_btn.pack(pady=6)


# ===== SPECIAL IMAGE =====

ctk.CTkLabel(
    app,
    text="Special Image (CTRL + Z)",
    font=("Arial", 16)
).pack(pady=15)

image_option = ctk.CTkOptionMenu(
    app,
    values=[]
)
image_option.pack(pady=6)

special_btn = ctk.CTkButton(
    app,
    text="Set Special Image",
    width=200,
    command=set_special
)
special_btn.pack(pady=6)


# ===== GUIDE =====

ctk.CTkLabel(
    app,
    text="Help",
    font=("Arial", 18)
).pack(pady=20)

guide_btn = ctk.CTkButton(
    app,
    text="Hướng dẫn sử dụng",
    width=200,
    command=open_guide
)
guide_btn.pack(pady=8)


refresh_images()

app.mainloop()
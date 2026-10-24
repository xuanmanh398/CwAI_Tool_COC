import customtkinter as ctk
import pyautogui
import threading
import time
import os
import webbrowser
import sys
from tkinter import filedialog
from PIL import Image

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

expire_time = "Free Version"

# ================= IMAGE FOLDER =================

if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

image_folder = os.path.join(base_path, "images")

if not os.path.exists(image_folder):
    os.makedirs(image_folder)

# ================= VARIABLES =================

special_image = None
running = False
paused = False

# ================= AUTO CLICK =================

def auto_click():

    global running, paused

    while running:

        if paused:
            time.sleep(0.2)
            continue

        try:

            screenshot = pyautogui.screenshot()

            images = os.listdir(image_folder)

            for img in images:

                path = os.path.join(image_folder, img)

                location = pyautogui.locate(
                    path,
                    screenshot,
                    confidence=0.85,
                    grayscale=True
                )

                if location:

                    center = pyautogui.center(location)

                    if img == special_image:

                        pyautogui.hotkey("ctrl", "z")
                        status_label.configure(text=f"Special detected: {img}")

                    else:

                        pyautogui.click(center)
                        status_label.configure(text=f"Click: {img}")

        except:
            pass

        time.sleep(0.05)

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

    win = ctk.CTkToplevel(panel_app)
    win.title("Image Manager")
    win.geometry("450x450")

    images = os.listdir(image_folder)

    for img in images:

        frame = ctk.CTkFrame(win)
        frame.pack(pady=5, padx=10, fill="x")

        path = os.path.join(image_folder, img)

        image = Image.open(path)
        image = image.resize((60,60))

        photo = ctk.CTkImage(light_image=image,size=(60,60))

        label = ctk.CTkLabel(
            frame,
            text=img,
            image=photo,
            compound="left"
        )
        label.pack(side="left",padx=10)

        delete_btn = ctk.CTkButton(
            frame,
            text="Delete",
            width=70,
            command=lambda p=path: delete_image(p)
        )
        delete_btn.pack(side="right",padx=10)

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
    webbrowser.open("https://youtu.be/17rX8rvKVG8")

# ================= PANEL =================

def start_panel():

    global panel_app
    global status_label
    global image_option

    panel_app = ctk.CTk()

    panel_app.title("AUTO CLICK TOOL")
    panel_app.geometry("600x650")

    title = ctk.CTkLabel(
        panel_app,
        text="AUTO CLICK TOOL",
        font=("Arial",28)
    )
    title.pack(pady=20)

    expire_label = ctk.CTkLabel(
        panel_app,
        text=f"Version: {expire_time}",
        font=("Arial",14),
        text_color="orange"
    )
    expire_label.pack(pady=5)

    status_label = ctk.CTkLabel(
        panel_app,
        text="Ready",
        font=("Arial",14)
    )
    status_label.pack(pady=10)

    ctk.CTkButton(panel_app,text="Start",width=200,command=start).pack(pady=8)
    ctk.CTkButton(panel_app,text="Pause",width=200,command=pause).pack(pady=8)
    ctk.CTkButton(panel_app,text="Stop",width=200,command=stop).pack(pady=8)

    ctk.CTkLabel(panel_app,text="Image Manager",font=("Arial",18)).pack(pady=15)

    ctk.CTkButton(panel_app,text="Add Image",width=200,command=add_image).pack(pady=6)
    ctk.CTkButton(panel_app,text="View / Delete Images",width=200,command=view_images).pack(pady=6)

    ctk.CTkLabel(panel_app,text="Special Image (CTRL + Z)",font=("Arial",16)).pack(pady=15)

    image_option = ctk.CTkOptionMenu(panel_app,values=[])
    image_option.pack(pady=6)

    ctk.CTkButton(panel_app,text="Set Special Image",width=200,command=set_special).pack(pady=6)

    ctk.CTkLabel(panel_app,text="Help",font=("Arial",18)).pack(pady=20)

    ctk.CTkButton(panel_app,text="Hướng dẫn sử dụng",width=200,command=open_guide).pack(pady=8)

    refresh_images()

    panel_app.mainloop()

# ================= RUN TOOL =================

start_panel()
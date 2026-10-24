import customtkinter as ctk
import pyautogui
import threading
import time
import os
import webbrowser
import sys
import json
from tkinter import filedialog
from PIL import Image

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

expire_time = "Không giới hạn"

# ================= IMAGE FOLDER =================

if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

image_folder = os.path.join(base_path, "images")
settings_file = os.path.join(base_path, "settings.json")

if not os.path.exists(image_folder):
    os.makedirs(image_folder)

# ================= VARIABLES =================

running = False
paused = False
image_actions = {}  # key: img, value: "click" or list of keys for hotkey
slot_option_menus = []
slot_selected_images = []
slot_action_labels = []
saved_slot_images = ["", "", "", ""]

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

                    action = image_actions.get(img, "click")

                    if action == "click":
                        pyautogui.click(pyautogui.center(location))
                        status_label.configure(text=f"Click: {img}")
                    else:
                        pyautogui.hotkey(*action)
                        status_label.configure(text=f"Hotkey: {img} - {action}")

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

    files = filedialog.askopenfilenames(
        filetypes=[("PNG Images", "*.png")]
    )

    if files:
        added = []

        for file in files:
            name = os.path.basename(file)
            new_path = os.path.join(image_folder, name)

            try:
                with open(file, "rb") as src:
                    with open(new_path, "wb") as dst:
                        dst.write(src.read())
                added.append(name)
            except Exception:
                pass

        refresh_images()
        save_settings()

        if added:
            status_label.configure(text=f"Added: {', '.join(added)}")
        else:
            status_label.configure(text="Không thêm được ảnh")


def delete_image(path):

    if os.path.exists(path):
        os.remove(path)
    refresh_images()
    save_settings()
    status_label.configure(text="Image deleted")


def delete_all_images():

    images = os.listdir(image_folder)

    for img in images:
        try:
            os.remove(os.path.join(image_folder, img))
        except Exception:
            pass

    image_actions.clear()
    refresh_images()
    save_settings()
    status_label.configure(text="Deleted all images")

# ================= SET IMAGE ACTION =================

def set_image_action(img):

    dialog = ctk.CTkInputDialog(text="Enter action: 'click' or hotkey like 'ctrl+c'", title="Set Action")

    action_str = dialog.get_input()

    if action_str:

        if action_str.lower() == "click":
            image_actions[img] = "click"
        else:
            keys = [k.strip() for k in action_str.split("+") if k.strip()]
            image_actions[img] = keys

        save_settings()
        status_label.configure(text=f"Set action for {img}: {action_str}")


def save_settings():

    data = {
        "slots": [
            {
                "image": slot.get(),
                "action": image_actions.get(slot.get(), "click")
            }
            for slot in slot_selected_images
        ],
        "image_actions": image_actions
    }

    try:
        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def load_settings():

    global saved_slot_images
    global image_actions

    if not os.path.exists(settings_file):
        return

    try:
        with open(settings_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        slots = data.get("slots", [])
        saved_slot_images = [slot.get("image", "") for slot in slots][:4]
        if len(saved_slot_images) < 4:
            saved_slot_images += [""] * (4 - len(saved_slot_images))

        image_actions = data.get("image_actions", {}) or {}
    except Exception:
        saved_slot_images = ["", "", "", ""]
        image_actions = {}


def apply_saved_slots():

    images = os.listdir(image_folder)

    for i, var in enumerate(slot_selected_images):
        saved = saved_slot_images[i] if i < len(saved_slot_images) else ""

        if saved and saved in images:
            var.set(saved)
        elif images:
            var.set(images[0])
        else:
            var.set("")

        on_slot_image_change(i, var.get())


def on_slot_image_change(slot_index, selection):

    if slot_index < 0 or slot_index >= len(slot_action_labels):
        return

    action = image_actions.get(selection, "click")
    label = slot_action_labels[slot_index]

    if selection:
        if action == "click":
            label.configure(text="Action: click")
        else:
            label.configure(text=f"Action: {'+'.join(action)}")
    else:
        label.configure(text="Action: click")

    if slot_index < len(saved_slot_images):
        saved_slot_images[slot_index] = selection
    save_settings()


def capture_hotkey_dialog(slot_index):

    if slot_index < 0 or slot_index >= len(slot_selected_images):
        return

    img = slot_selected_images[slot_index].get()
    if not img:
        status_label.configure(text="Chưa chọn ảnh cho ô này", text_color="orange")
        return

    dialog = ctk.CTkToplevel(app)
    dialog.title("Nhấn tổ hợp phím")
    dialog.geometry("420x220")
    dialog.grab_set()
    dialog.focus_force()

    info = ctk.CTkLabel(dialog, text="Nhấn tổ hợp phím, sau đó nhấn Enter để xác nhận.")
    info.pack(pady=15, padx=20)

    combo_var = ctk.StringVar(value="")
    combo_label = ctk.CTkLabel(dialog, textvariable=combo_var, font=("Arial", 16))
    combo_label.pack(pady=10)

    pressed_mods = set()
    last_key = [None]

    def update_display():
        parts = []
        for mod in ["ctrl", "shift", "alt"]:
            if mod in pressed_mods:
                parts.append(mod)
        if last_key[0]:
            parts.append(last_key[0])
        combo_var.set("+".join(parts))

    def press_key(event):
        key = event.keysym.lower()

        if key in ["control_l", "control_r"]:
            pressed_mods.add("ctrl")
            update_display()
            return
        if key in ["shift_l", "shift_r"]:
            pressed_mods.add("shift")
            update_display()
            return
        if key in ["alt_l", "alt_r", "meta_l", "meta_r"]:
            pressed_mods.add("alt")
            update_display()
            return
        if key == "return":
            accept_action()
            return
        if key == "escape":
            cancel_action()
            return

        last_key[0] = key
        update_display()

    def release_key(event):
        key = event.keysym.lower()
        if key in ["control_l", "control_r"]:
            pressed_mods.discard("ctrl")
            update_display()
        elif key in ["shift_l", "shift_r"]:
            pressed_mods.discard("shift")
            update_display()
        elif key in ["alt_l", "alt_r", "meta_l", "meta_r"]:
            pressed_mods.discard("alt")
            update_display()

    def accept_action(_=None):
        if not last_key[0] and not pressed_mods:
            return
        action = []
        for mod in ["ctrl", "shift", "alt"]:
            if mod in pressed_mods:
                action.append(mod)
        if last_key[0] and last_key[0] not in action:
            action.append(last_key[0])
        if not action:
            action = ["click"]
        image_actions[img] = action
        slot_action_labels[slot_index].configure(text=f"Action: {'+'.join(action)}")
        save_settings()
        status_label.configure(text=f"Set action for {img}: {'+'.join(action)}")
        dialog.destroy()

    def cancel_action(_=None):
        dialog.destroy()

    dialog.bind_all("<KeyPress>", press_key)
    dialog.bind_all("<KeyRelease>", release_key)
    dialog.bind_all("<Return>", accept_action)
    dialog.bind_all("<Escape>", cancel_action)

    button_frame = ctk.CTkFrame(dialog)
    button_frame.pack(pady=10)

    ok_btn = ctk.CTkButton(button_frame, text="OK", command=accept_action)
    ok_btn.pack(side="left", padx=10)
    cancel_btn = ctk.CTkButton(button_frame, text="Cancel", command=cancel_action)
    cancel_btn.pack(side="left", padx=10)


def refresh_images():

    images = os.listdir(image_folder)

    for menu in slot_option_menus:
        menu.configure(values=images)

    for var in slot_selected_images:
        if images:
            if not var.get() or var.get() not in images:
                var.set(images[0])
        else:
            var.set("")


def view_images(parent):

    win = ctk.CTkToplevel(parent)
    win.title("Image Manager")
    win.geometry("500x550")

    top_frame = ctk.CTkFrame(win)
    top_frame.pack(fill="x", padx=10, pady=(10, 5))

    ctk.CTkButton(top_frame, text="Delete All Images", width=160, command=delete_all_images).pack(side="left", padx=5)
    ctk.CTkButton(top_frame, text="Refresh", width=120, command=refresh_images).pack(side="left", padx=5)

    scroll = ctk.CTkScrollableFrame(win)
    scroll.pack(fill="both", expand=True, padx=10, pady=5)

    images = os.listdir(image_folder)

    if not images:
        empty = ctk.CTkLabel(scroll, text="No images available")
        empty.pack(pady=20)
        return

    for img in images:

        frame = ctk.CTkFrame(scroll)
        frame.pack(pady=5, padx=5, fill="x")

        path = os.path.join(image_folder, img)

        image = Image.open(path)
        image = image.resize((60, 60))

        photo = ctk.CTkImage(light_image=image, size=(60, 60))

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

        set_action_btn = ctk.CTkButton(
            frame,
            text="Set Action",
            width=90,
            command=lambda i=img: set_image_action(i)
        )
        set_action_btn.pack(side="right", padx=10)

# ================= PANEL =================

def set_slot_action(slot_index):

    capture_hotkey_dialog(slot_index)


def start_panel():

    global status_label
    global slot_option_menus
    global slot_selected_images
    global slot_action_labels

    slot_option_menus = []
    slot_selected_images = []
    slot_action_labels = []

    app.title("AUTO CLICK TOOL")
    app.geometry("700x700")

    title = ctk.CTkLabel(
        app,
        text="AUTO CLICK TOOL",
        font=("Arial",28)
    )
    title.pack(pady=20)

    expire_label = ctk.CTkLabel(
        app,
        text=f"Hạn key: {expire_time}",
        font=("Arial",14),
        text_color="orange"
    )
    expire_label.pack(pady=5)

    status_label = ctk.CTkLabel(
        app,
        text="Ready",
        font=("Arial",14)
    )
    status_label.pack(pady=10)

    ctk.CTkButton(app,text="Start",width=200,command=start).pack(pady=8)
    ctk.CTkButton(app,text="Pause",width=200,command=pause).pack(pady=8)
    ctk.CTkButton(app,text="Stop",width=200,command=stop).pack(pady=8)

    ctk.CTkLabel(app,text="Image Slots",font=("Arial",18)).pack(pady=15)

    for i in range(4):
        frame = ctk.CTkFrame(app)
        frame.pack(pady=6, padx=20, fill="x")

        slot_label = ctk.CTkLabel(frame, text=f"Slot {i + 1}", width=80)
        slot_label.pack(side="left", padx=(10, 5))

        slot_var = ctk.StringVar(value="")
        slot_selected_images.append(slot_var)

        slot_menu = ctk.CTkOptionMenu(
            frame,
            values=[],
            variable=slot_var,
            width=220,
            command=lambda choice, idx=i: on_slot_image_change(idx, choice)
        )
        slot_menu.pack(side="left", padx=5)
        slot_option_menus.append(slot_menu)

        action_label = ctk.CTkLabel(frame, text="Action: click", width=140)
        action_label.pack(side="left", padx=5)
        slot_action_labels.append(action_label)

        ctk.CTkButton(frame, text="Set Action", width=100, command=lambda idx=i: set_slot_action(idx)).pack(side="right", padx=10)

    ctk.CTkButton(app,text="Add Image",width=200,command=add_image).pack(pady=10)
    ctk.CTkButton(app,text="View / Delete Images",width=200,command=lambda: view_images(app)).pack(pady=6)

    refresh_images()
    load_settings()
    apply_saved_slots()

# ================= MAIN GUI =================

app = ctk.CTk()

start_panel()

app.mainloop()
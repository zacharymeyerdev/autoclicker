import tkinter as tk
from tkinter import ttk, messagebox
from pynput.mouse import Controller, Button
import time
import threading
import keyboard
import json
import logging

# Constants for mouse buttons
MOUSE_BUTTONS = {
    'left': Button.left,
    'right': Button.right,
    'middle': Button.middle
}

# Setting up logging
logging.basicConfig(filename='autoclicker.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AutoClicker:
    def __init__(self, button='left', click_type='click', cps=1):
        self.button = MOUSE_BUTTONS[button]
        self.click_type = click_type
        self.cps = cps
        self.running = False
        self.mouse_controller = Controller()
        self.click_thread = None

    def start_clicking(self):
        if not self.running:
            self.running = True
            self.click_thread = threading.Thread(target=self.click_process)
            self.click_thread.start()
            logging.info("Auto-clicker started.")

    def stop_clicking(self):
        self.running = False
        if self.click_thread is not None:
            self.click_thread.join()
            logging.info("Auto-clicker stopped.")

    def click_process(self):
        try:
            if self.click_type == 'click':
                while self.running:
                    self.mouse_controller.click(self.button)
                    time.sleep(1 / self.cps)
            elif self.click_type == 'hold':
                self.mouse_controller.press(self.button)
                while self.running:
                    time.sleep(1 / self.cps)
                self.mouse_controller.release(self.button)
        except Exception as e:
            logging.error(f"Error during clicking process: {e}")

class AutoClickerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoClicker Settings")
        self.auto_clicker = AutoClicker()
        self.hotkey = 'ctrl+shift+a'
        self.setup_widgets()
        self.load_settings()

    def setup_widgets(self):
        self.button_label = ttk.Label(self.root, text="Select Button:")
        self.button_label.grid(row=0, column=0, padx=10, pady=10)

        self.button_var = tk.StringVar()
        self.button_dropdown = ttk.Combobox(self.root, textvariable=self.button_var, state='readonly')
        self.button_dropdown['values'] = list(MOUSE_BUTTONS.keys())
        self.button_dropdown.current(0)
        self.button_dropdown.grid(row=0, column=1, padx=10, pady=10)
        self.button_dropdown.bind("<<ComboboxSelected>>", self.update_settings)

        self.type_label = ttk.Label(self.root, text="Select Click Type:")
        self.type_label.grid(row=1, column=0, padx=10, pady=10)

        self.type_var = tk.StringVar()
        self.type_dropdown = ttk.Combobox(self.root, textvariable=self.type_var, state='readonly')
        self.type_dropdown['values'] = ['click', 'hold']
        self.type_dropdown.current(0)
        self.type_dropdown.grid(row=1, column=1, padx=10, pady=10)
        self.type_dropdown.bind("<<ComboboxSelected>>", self.update_settings)

        self.cps_label = ttk.Label(self.root, text="Clicks Per Second:")
        self.cps_label.grid(row=2, column=0, padx=10, pady=10)

        self.cps_var = tk.StringVar(value="1")
        self.cps_entry = ttk.Entry(self.root, textvariable=self.cps_var)
        self.cps_entry.grid(row=2, column=1, padx=10, pady=10)
        self.cps_entry.bind("<FocusOut>", self.validate_cps)

        self.start_button = ttk.Button(self.root, text="Start Clicking", command=self.start_clicking)
        self.start_button.grid(row=3, column=0, padx=10, pady=10)

        self.stop_button = ttk.Button(self.root, text="Stop Clicking", command=self.stop_clicking)
        self.stop_button.grid(row=3, column=1, padx=10, pady=10)

        self.status_label = ttk.Label(self.root, text="Status: Stopped", foreground="red")
        self.status_label.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        self.hotkey_label = ttk.Label(self.root, text="Set Hotkey:")
        self.hotkey_label.grid(row=5, column=0, padx=10, pady=10)

        self.hotkey_var = tk.StringVar(value=self.hotkey)
        self.hotkey_entry = ttk.Entry(self.root, textvariable=self.hotkey_var)
        self.hotkey_entry.grid(row=5, column=1, padx=10, pady=10)
        self.hotkey_entry.bind("<FocusOut>", self.update_hotkey)

        self.save_button = ttk.Button(self.root, text="Save Settings", command=self.save_settings)
        self.save_button.grid(row=6, column=0, padx=10, pady=10)

        self.load_button = ttk.Button(self.root, text="Load Settings", command=self.load_settings)
        self.load_button.grid(row=6, column=1, padx=10, pady=10)

    def validate_cps(self, event=None):
        try:
            cps = int(self.cps_var.get())
            if cps <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a positive integer for CPS.")
            self.cps_var.set("1")

    def update_settings(self, event=None):
        button = self.button_var.get()
        click_type = self.type_var.get()
        cps = int(self.cps_var.get())
        self.auto_clicker = AutoClicker(button=button, click_type=click_type, cps=cps)

    def start_clicking(self):
        self.update_settings()
        self.auto_clicker.start_clicking()
        self.status_label.config(text="Status: Running", foreground="green")

    def stop_clicking(self):
        self.auto_clicker.stop_clicking()
        self.status_label.config(text="Status: Stopped", foreground="red")

    def update_hotkey(self, event=None):
        new_hotkey = self.hotkey_var.get()
        try:
            keyboard.remove_hotkey(self.hotkey)
            self.hotkey = new_hotkey
            keyboard.add_hotkey(self.hotkey, self.toggle_clicking)
            logging.info(f"Hotkey updated to {self.hotkey}")
        except Exception as e:
            messagebox.showerror("Invalid Hotkey", f"Failed to set hotkey: {e}")
            self.hotkey_var.set(self.hotkey)

    def toggle_clicking(self):
        if self.auto_clicker.running:
            self.stop_clicking()
        else:
            self.start_clicking()

    def save_settings(self):
        settings = {
            "button": self.button_var.get(),
            "click_type": self.type_var.get(),
            "cps": self.cps_var.get(),
            "hotkey": self.hotkey_var.get()
        }
        with open("settings.json", "w") as f:
            json.dump(settings, f)
        logging.info("Settings saved.")

    def load_settings(self):
        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)
            self.button_var.set(settings["button"])
            self.type_var.set(settings["click_type"])
            self.cps_var.set(settings["cps"])
            self.hotkey_var.set(settings["hotkey"])
            self.update_hotkey()
            self.update_settings()
            logging.info("Settings loaded.")
        except FileNotFoundError:
            logging.warning("Settings file not found. Using default settings.")
        except Exception as e:
            logging.error(f"Failed to load settings: {e}")

class AutoClickerApp:
    def __init__(self, root):
        self.gui = AutoClickerGUI(root)

# Running the app
root = tk.Tk()
app = AutoClickerApp(root)
root.mainloop()

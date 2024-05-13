import tkinter as tk
from tkinter import ttk
from pynput.mouse import Controller, Button
import time
import threading
import keyboard

# Constants for mouse buttons
MOUSE_BUTTONS = {
    'left': Button.left,
    'right': Button.right,
    'middle': Button.middle
}

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

    def stop_clicking(self):
        self.running = False
        if self.click_thread is not None:
            self.click_thread.join()

    def click_process(self):
        if self.click_type == 'click':
            while self.running:
                self.mouse_controller.click(self.button)
                time.sleep(1 / self.cps)
        elif self.click_type == 'hold':
            self.mouse_controller.press(self.button)
            while self.running:
                time.sleep(1 / self.cps)
            self.mouse_controller.release(self.button)

class AutoClickerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoClicker Settings")
        self.auto_clicker = AutoClicker()
        self.setup_widgets()

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

        self.start_button = ttk.Button(self.root, text="Start Clicking", command=self.start_clicking)
        self.start_button.grid(row=3, column=0, padx=10, pady=10)

        self.stop_button = ttk.Button(self.root, text="Stop Clicking", command=self.stop_clicking)
        self.stop_button.grid(row=3, column=1, padx=10, pady=10)

    def update_settings(self, event=None):
        button = self.button_var.get()
        click_type = self.type_var.get()
        cps = int(self.cps_var.get())
        self.auto_clicker = AutoClicker(button=button, click_type=click_type, cps=cps)

    def start_clicking(self):
        self.update_settings()
        self.auto_clicker.start_clicking()

    def stop_clicking(self):
        self.auto_clicker.stop_clicking()

class AutoClickerApp:
    def __init__(self, root):
        self.gui = AutoClickerGUI(root)
        self.hotkey = 'ctrl+shift+a'
        keyboard.add_hotkey(self.hotkey, self.toggle_clicking)

    def toggle_clicking(self):
        if self.gui.auto_clicker.running:
            self.gui.stop_clicking()
        else:
            self.gui.start_clicking()

    def update_hotkey(self, new_hotkey):
        keyboard.remove_hotkey(self.hotkey)
        self.hotkey = new_hotkey
        keyboard.add_hotkey(self.hotkey, self.toggle_clicking)

# Running the app
root = tk.Tk()
app = AutoClickerApp(root)
root.mainloop()

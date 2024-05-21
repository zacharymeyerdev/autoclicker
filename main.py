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


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event):
        if self.tip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self, event):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()


class AutoClicker:
    def __init__(self, button='left', click_type='single', cps=1, pattern=None):
        self.button = MOUSE_BUTTONS[button]
        self.click_type = click_type
        self.cps = cps
        self.pattern = pattern if pattern else [1]
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
            while self.running:
                if self.click_type == 'single':
                    self.mouse_controller.click(self.button)
                    time.sleep(1 / self.cps)
                elif self.click_type == 'double':
                    self.mouse_controller.click(self.button)
                    time.sleep(0.1)  # Short delay between double clicks
                    self.mouse_controller.click(self.button)
                    time.sleep(1 / self.cps)
                elif self.click_type == 'pattern':
                    for interval in self.pattern:
                        if not self.running:
                            break
                        self.mouse_controller.click(self.button)
                        time.sleep(interval)
        except Exception as e:
            logging.error(f"Error during clicking process: {e}")


class AutoClickerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoClicker Settings")
        self.auto_clicker = AutoClicker()
        self.hotkey = 'f5'
        self.setup_widgets()
        self.setup_color_customization()  # Add this line
        self.load_settings()
        self.load_color_settings()  # Add this line

    def setup_widgets(self):
        self.setup_dark_mode_checkbutton()
        self.setup_button_dropdown()
        self.setup_type_dropdown()
        self.setup_pattern_entry()
        self.setup_cps_entry()
        self.setup_control_buttons()
        self.setup_status_label()
        self.setup_hotkey_entry()
        self.setup_save_load_buttons()

        self.setup_tooltips()

    def setup_dark_mode_checkbutton(self):
        self.dark_mode = tk.BooleanVar(value=False)
        self.dark_mode_check = ttk.Checkbutton(self.root, text="Dark Mode", variable=self.dark_mode, command=self.toggle_dark_mode)
        self.dark_mode_check.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

    def setup_button_dropdown(self):
        self.button_label = ttk.Label(self.root, text="Select Button:")
        self.button_label.grid(row=0, column=0, padx=10, pady=10)
        self.button_var = tk.StringVar()
        self.button_dropdown = ttk.Combobox(self.root, textvariable=self.button_var, state='readonly')
        self.button_dropdown['values'] = list(MOUSE_BUTTONS.keys())
        self.button_dropdown.current(0)
        self.button_dropdown.grid(row=0, column=1, padx=10, pady=10)
        self.button_dropdown.bind("<<ComboboxSelected>>", self.update_settings)

    def setup_type_dropdown(self):
        self.type_label = ttk.Label(self.root, text="Select Click Type:")
        self.type_label.grid(row=1, column=0, padx=10, pady=10)
        self.type_var = tk.StringVar()
        self.type_dropdown = ttk.Combobox(self.root, textvariable=self.type_var, state='readonly')
        self.type_dropdown['values'] = ['single', 'double', 'pattern']
        self.type_dropdown.current(0)
        self.type_dropdown.grid(row=1, column=1, padx=10, pady=10)
        self.type_dropdown.bind("<<ComboboxSelected>>", self.update_click_type)

    def setup_pattern_entry(self):
        self.pattern_label = ttk.Label(self.root, text="Pattern Intervals (sec):")
        self.pattern_label.grid(row=2, column=0, padx=10, pady=10)
        self.pattern_var = tk.StringVar(value="1")
        self.pattern_entry = ttk.Entry(self.root, textvariable=self.pattern_var)
        self.pattern_entry.grid(row=2, column=1, padx=10, pady=10)
        self.pattern_entry.bind("<FocusOut>", self.update_settings)

    def setup_cps_entry(self):
        self.cps_label = ttk.Label(self.root, text="Clicks Per Second:")
        self.cps_label.grid(row=3, column=0, padx=10, pady=10)
        self.cps_var = tk.StringVar(value="1")
        self.cps_entry = ttk.Entry(self.root, textvariable=self.cps_var)
        self.cps_entry.grid(row=3, column=1, padx=10, pady=10)
        self.cps_entry.bind("<FocusOut>", self.validate_cps)

    def setup_control_buttons(self):
        self.start_button = ttk.Button(self.root, text="Start Clicking", command=self.start_clicking)
        self.start_button.grid(row=4, column=0, padx=10, pady=10)
        self.stop_button = ttk.Button(self.root, text="Stop Clicking", command=self.stop_clicking)
        self.stop_button.grid(row=4, column=1, padx=10, pady=10)

    def setup_status_label(self):
        self.status_label = ttk.Label(self.root, text="Status: Stopped", foreground="red")
        self.status_label.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    def setup_hotkey_entry(self):
        self.hotkey_label = ttk.Label(self.root, text="Set Hotkey:")
        self.hotkey_label.grid(row=6, column=0, padx=10, pady=10)
        self.hotkey_var = tk.StringVar(value=self.hotkey)
        self.hotkey_entry = ttk.Entry(self.root, textvariable=self.hotkey_var)
        self.hotkey_entry.grid(row=6, column=1, padx=10, pady=10)
        self.hotkey_entry.bind("<FocusOut>", self.update_hotkey)

    def setup_save_load_buttons(self):
        self.save_button = ttk.Button(self.root, text="Save Settings", command=self.save_settings)
        self.save_button.grid(row=7, column=0, padx=10, pady=10)
        self.load_button = ttk.Button(self.root, text="Load Settings", command=self.load_settings)
        self.load_button.grid(row=7, column=1, padx=10, pady=10)

    def setup_tooltips(self):
        ToolTip(self.button_dropdown, "Select the mouse button to click")
        ToolTip(self.type_dropdown, "Select the type of click (single, double, or pattern)")
        ToolTip(self.pattern_entry, "Enter the pattern intervals in seconds, separated by commas (e.g., 1,0.5,1.5)")
        ToolTip(self.cps_entry, "Enter the number of clicks per second")
        ToolTip(self.start_button, "Start the auto-clicker")
        ToolTip(self.stop_button, "Stop the auto-clicker")
        ToolTip(self.hotkey_entry, "Set the hotkey to toggle the auto-clicker")
        ToolTip(self.save_button, "Save the current settings")
        ToolTip(self.load_button, "Load the saved settings")

    def setup_color_customization(self):
        self.bg_color_label = ttk.Label(self.root, text="Window Color:")
        self.bg_color_label.grid(row=9, column=0, padx=10, pady=10)
        self.bg_color_button = ttk.Button(self.root, text="Choose Color", command=self.choose_bg_color)
        self.bg_color_button.grid(row=9, column=1, padx=10, pady=10)
        
        self.text_color_label = ttk.Label(self.root, text="Text Color:")
        self.text_color_label.grid(row=10, column=0, padx=10, pady=10)
        self.text_color_button = ttk.Button(self.root, text="Choose Color", command=self.choose_text_color)
        self.text_color_button.grid(row=10, column=1, padx=10, pady=10)

    def choose_bg_color(self):
        color_code = colorchooser.askcolor(title="Choose window color")[1]
        if color_code:
            self.root.configure(bg=color_code)
            self.save_color_settings(bg_color=color_code)

    def choose_text_color(self):
        color_code = colorchooser.askcolor(title="Choose text color")[1]
        if color_code:
            self.apply_text_color(color_code)
            self.save_color_settings(text_color=color_code)

    def apply_text_color(self, color):
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Label) or isinstance(widget, ttk.Button) or isinstance(widget, ttk.Checkbutton):
                widget.configure(foreground=color)

    def save_color_settings(self, bg_color=None, text_color=None):
        try:
            with open("color_settings.json", "r") as f:
                color_settings = json.load(f)
        except FileNotFoundError:
            color_settings = {}

        if bg_color:
            color_settings["bg_color"] = bg_color
        if text_color:
            color_settings["text_color"] = text_color

        with open("color_settings.json", "w") as f:
            json.dump(color_settings, f)

    def load_color_settings(self):
        try:
            with open("color_settings.json", "r") as f:
                color_settings = json.load(f)
            if "bg_color" in color_settings:
                self.root.configure(bg=color_settings["bg_color"])
            if "text_color" in color_settings:
                self.apply_text_color(color_settings["text_color"])
        except FileNotFoundError:
            pass

    def toggle_dark_mode(self):
        self.apply_theme()

    def apply_theme(self):
        if self.dark_mode.get():
            self.root.style.theme_use('alt')
        else:
            self.root.style.theme_use('default')

    def validate_cps(self, event=None):
        try:
            cps = int(self.cps_var.get())
            if cps <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a positive integer for CPS.")
            self.cps_var.set("1")

    def update_click_type(self, event=None):
        click_type = self.type_var.get()
        if click_type == 'pattern':
            self.pattern_entry.config(state='normal')
        else:
            self.pattern_entry.config(state='disabled')
        self.update_settings()

    def update_settings(self, event=None):
        button = self.button_var.get()
        click_type = self.type_var.get()
        cps = int(self.cps_var.get())
        pattern = [float(x) for x in self.pattern_var.get().split(',')] if click_type == 'pattern' else None
        self.auto_clicker = AutoClicker(button=button, click_type=click_type, cps=cps, pattern=pattern)

    def start_clicking(self):
        self.update_settings()
        self.status_label.config(text=“Status: Running”, foreground=“green”)

	def stop_clicking(self):
    self.auto_clicker.stop_clicking()
    self.status_label.config(text="Status: Stopped", foreground="red")

def update_hotkey(self, event=None):
    new_hotkey = self.hotkey_var.get()
    try:
        keyboard.remove_hotkey(self.hotkey)
    except KeyError:
        pass  # Ignore if the hotkey was not set before
    self.hotkey = new_hotkey
    try:
        keyboard.add_hotkey(self.hotkey, self.toggle_clicking)
        logging.info(f"Hotkey updated to {self.hotkey}")
    except Exception as e:
        messagebox.showerror("Invalid Hotkey", f"Failed to set hotkey: {e}")
        logging.error(f"Failed to set hotkey: {e}")
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
        "pattern": self.pattern_var.get(),
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
        self.pattern_var.set(settings["pattern"])
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
    	self.root = root
    	self.root.title("AutoClicker Settings")
    	self.auto_clicker = AutoClicker()
    	self.hotkey = 'f5'
    	self.setup_widgets()
    	self.setup_color_customization()  # Add this line
        self.load_settings()
    	self.load_color_settings()  # Add this line

    def apply_styles(self):
        dark_theme = {
            'TLabel': {'configure': {'background': '#333333', 'foreground': '#ffffff'}},
            'TButton': {'configure': {'background': '#444444', 'foreground': '#ffffff'}},
            'TCombobox': {'configure': {'background': '#333333', 'foreground': '#ffffff'}},
            'TEntry': {'configure': {'background': '#333333', 'foreground': '#ffffff'}}
        }

        light_theme = {
            'TLabel': {'configure': {'background': '#f0f0f0', 'foreground': '#000000'}},
            'TButton': {'configure': {'background': '#f0f0f0', 'foreground': '#000000'}},
            'TCombobox': {'configure': {'background': '#ffffff', 'foreground': '#000000'}},
            'TEntry': {'configure': {'background': '#ffffff', 'foreground': '#000000'}}
        }

        if 'alt' not in self.style.theme_names():
            self.style.theme_create('alt', parent='default', settings=dark_theme)
        if 'default' not in self.style.theme_names():
            self.style.theme_create('default', parent='alt', settings=light_theme)

# Running the app
if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from pynput.mouse import Controller, Button
import time
import threading
import keyboard
import json
import logging
from pynput import mouse

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
    def __init__(self, button='left', click_type='single', interval=100, pattern=None):
        self.button = MOUSE_BUTTONS[button]
        self.click_type = click_type
        self.interval = interval / 1000.0  # Convert to seconds
        self.pattern = pattern if pattern else [self.interval]
        self.running = False
        self.mouse_controller = Controller()
        self.click_thread = None
        self.repeat_mode = 'repeat_until_stopped'
        self.repeat_count = 1

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
            count = 0
            while self.running:
                if self.click_type == 'single':
                    self.mouse_controller.click(self.button)
                    count += 1
                    time.sleep(self.interval)
                elif self.click_type == 'double':
                    self.mouse_controller.click(self.button)
                    time.sleep(0.1)  # Short delay between double clicks
                    self.mouse_controller.click(self.button)
                    count += 2
                    time.sleep(self.interval)
                elif self.click_type == 'pattern':
                    for interval in self.pattern:
                        if not self.running:
                            break
                        self.mouse_controller.click(self.button)
                        count += 1
                        time.sleep(interval)
                
                if self.repeat_mode == 'repeat' and count >= self.repeat_count:
                    self.stop_clicking()
                    break
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
        self.register_hotkey()

    def setup_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Click interval
        interval_frame = ttk.LabelFrame(main_frame, text="Click interval", padding="10")
        interval_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))

        self.hours_var = tk.IntVar(value=0)
        self.minutes_var = tk.IntVar(value=0)
        self.seconds_var = tk.IntVar(value=0)
        self.milliseconds_var = tk.IntVar(value=100)

        ttk.Label(interval_frame, text="hours").grid(row=0, column=1)
        ttk.Label(interval_frame, text="mins").grid(row=0, column=3)
        ttk.Label(interval_frame, text="secs").grid(row=0, column=5)
        ttk.Label(interval_frame, text="milliseconds").grid(row=0, column=7)

        ttk.Spinbox(interval_frame, from_=0, to=23, textvariable=self.hours_var, width=5).grid(row=0, column=0)
        ttk.Spinbox(interval_frame, from_=0, to=59, textvariable=self.minutes_var, width=5).grid(row=0, column=2)
        ttk.Spinbox(interval_frame, from_=0, to=59, textvariable=self.seconds_var, width=5).grid(row=0, column=4)
        ttk.Spinbox(interval_frame, from_=0, to=999, textvariable=self.milliseconds_var, width=7).grid(row=0, column=6)

        # Click options
        options_frame = ttk.LabelFrame(main_frame, text="Click options", padding="10")
        options_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))

        self.button_var = tk.StringVar(value='left')
        self.type_var = tk.StringVar(value='single')

        ttk.Label(options_frame, text="Mouse button:").grid(row=0, column=0, padx=5, pady=5)
        self.button_dropdown = ttk.Combobox(options_frame, textvariable=self.button_var, state='readonly')
        self.button_dropdown['values'] = list(MOUSE_BUTTONS.keys())
        self.button_dropdown.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(options_frame, text="Click type:").grid(row=1, column=0, padx=5, pady=5)
        self.type_dropdown = ttk.Combobox(options_frame, textvariable=self.type_var, state='readonly')
        self.type_dropdown['values'] = ['single', 'double', 'pattern']
        self.type_dropdown.grid(row=1, column=1, padx=5, pady=5)
        self.type_dropdown.bind("<<ComboboxSelected>>", self.update_click_type)

        # Add the pattern entry for click type pattern
        self.pattern_var = tk.StringVar(value="0.1,0.2,0.3")  # Example default pattern
        self.pattern_entry = ttk.Entry(options_frame, textvariable=self.pattern_var, state='disabled', width=20)
        self.pattern_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Label(options_frame, text="Pattern (sec):").grid(row=2, column=0, padx=5, pady=5)

        # Click repeat
        repeat_frame = ttk.LabelFrame(main_frame, text="Click repeat", padding="10")
        repeat_frame.grid(row=1, column=1, sticky=(tk.W, tk.E))

        self.repeat_var = tk.IntVar(value=1)
        self.repeat_mode_var = tk.StringVar(value='repeat_until_stopped')

        self.repeat_times_entry = ttk.Entry(repeat_frame, textvariable=self.repeat_var, width=5)
        self.repeat_times_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Radiobutton(repeat_frame, text="Repeat", variable=self.repeat_mode_var, value='repeat', command=self.update_repeat_mode).grid(row=0, column=0, padx=5, pady=5)
        ttk.Radiobutton(repeat_frame, text="Repeat until stopped", variable=self.repeat_mode_var, value='repeat_until_stopped', command=self.update_repeat_mode).grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        self.repeat_times_entry.config(state='disabled')  # Start with disabled

        # Cursor position
        position_frame = ttk.LabelFrame(main_frame, text="Cursor position", padding="10")
        position_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))

        self.position_var = tk.StringVar(value='current')
        self.x_pos_var = tk.IntVar(value=0)
        self.y_pos_var = tk.IntVar(value=0)

        ttk.Radiobutton(position_frame, text="Current location", variable=self.position_var, value='current').grid(row=0, column=0, padx=5, pady=5)
        ttk.Radiobutton(position_frame, text="Pick location", variable=self.position_var, value='pick').grid(row=0, column=1, padx=5, pady=5)

        self.pick_location_button = ttk.Button(position_frame, text="Pick location", command=self.pick_location)
        self.pick_location_button.grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(position_frame, text="X:").grid(row=1, column=0, padx=5, pady=5)
        self.x_pos_entry = ttk.Entry(position_frame, textvariable=self.x_pos_var, width=5)
        self.x_pos_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(position_frame, text="Y:").grid(row=1, column=2, padx=5, pady=5)
        self.y_pos_entry = ttk.Entry(position_frame, textvariable=self.y_pos_var, width=5)
        self.y_pos_entry.grid(row=1, column=3, padx=5, pady=5)

        # Control buttons
        self.start_button = ttk.Button(main_frame, text="Start (F6)", command=self.start_clicking)
        self.start_button.grid(row=3, column=0, padx=5, pady=10, sticky=(tk.W, tk.E))

        self.stop_button = ttk.Button(main_frame, text="Stop (F6)", command=self.stop_clicking)
        self.stop_button.grid(row=3, column=1, padx=5, pady=10, sticky=(tk.W, tk.E))

        self.hotkey_var = tk.StringVar(value=self.hotkey)
        self.hotkey_button = ttk.Button(main_frame, text="Hotkey setting", command=self.set_hotkey)
        self.hotkey_button.grid(row=4, column=0, padx=5, pady=10, sticky=(tk.W, tk.E))

        self.record_button = ttk.Button(main_frame, text="Record & Playback", command=self.record_playback)
        self.record_button.grid(row=4, column=1, padx=5, pady=10, sticky=(tk.W, tk.E))

        self.status_label = ttk.Label(main_frame, text="Status: Stopped", foreground="red")
        self.status_label.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

    def set_hotkey(self):
        new_hotkey = simpledialog.askstring("Set Hotkey", "Enter new hotkey:", initialvalue=self.hotkey)
        if new_hotkey:
            try:
                keyboard.remove_hotkey(self.hotkey)
            except KeyError:
                pass  # Ignore if the hotkey was not set before
            self.hotkey = new_hotkey
            self.register_hotkey()
            self.hotkey_var.set(self.hotkey)
            logging.info(f"Hotkey updated to {self.hotkey}")

    def register_hotkey(self):
        try:
            keyboard.add_hotkey(self.hotkey, self.toggle_clicking)
            logging.info(f"Hotkey {self.hotkey} registered.")
        except Exception as e:
            messagebox.showerror("Invalid Hotkey", f"Failed to set hotkey: {e}")
            logging.error(f"Failed to set hotkey: {e}")

    def pick_location(self):
        messagebox.showinfo("Pick Location", "Move the mouse to the desired position and press 'Enter' to select the location.")

        def on_key_press(key):
            if key == keyboard.Key.enter:
                x, y = self.mouse_controller.position
                self.x_pos_var.set(x)
                self.y_pos_var.set(y)
                messagebox.showinfo("Location Picked", f"Location set to X: {x}, Y: {y}")
                # Stop listener
                return False

        # Create a mouse controller instance
        self.mouse_controller = Controller()

        # Set up listener for keyboard events
        with keyboard.Listener(on_press=on_key_press) as listener:
            listener.join()


    def record_playback(self):
        self.recording = []
        messagebox.showinfo("Record", "Press 'R' to start recording, 'S' to stop recording, and 'P' to playback the recording.")

        def on_click(x, y, button, pressed):
            if pressed:
                event = ('click', x, y, button)
                self.recording.append(event)
                logging.info(f"Recorded click at ({x}, {y}) with {button}")

        def on_move(x, y):
            event = ('move', x, y)
            self.recording.append(event)
            logging.info(f"Recorded move to ({x}, {y})")

        def on_key_press(key):
            try:
                if key.char == 'r':
                    self.recording = []
                    messagebox.showinfo("Recording", "Recording started. Press 'S' to stop.")
                    return True
                elif key.char == 's':
                    messagebox.showinfo("Recording Stopped", "Recording stopped. Press 'P' to playback.")
                    return False
                elif key.char == 'p':
                    play_recording()
                    return False
            except AttributeError:
                pass

        def play_recording():
            for event in self.recording:
                if event[0] == 'move':
                    self.mouse_controller.position = (event[1], event[2])
                    time.sleep(0.01)  # Small delay to mimic human-like movement
                elif event[0] == 'click':
                    x, y, button = event[1], event[2], event[3]
                    self.mouse_controller.position = (x, y)
                    self.mouse_controller.click(button)
                    time.sleep(0.1)  # Small delay to mimic human-like clicking

        # Set up listeners for mouse and keyboard events
        with keyboard.Listener(on_press=on_key_press) as key_listener:
            with mouse.Listener(on_click=on_click, on_move=on_move) as mouse_listener:
                key_listener.join()
                mouse_listener.stop()


    def update_repeat_mode(self):
        if self.repeat_mode_var.get() == 'repeat':
            self.repeat_times_entry.config(state='normal')
        else:
            self.repeat_times_entry.config(state='disabled')

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
        hours = self.hours_var.get()
        minutes = self.minutes_var.get()
        seconds = self.seconds_var.get()
        milliseconds = self.milliseconds_var.get()
        interval = (hours * 3600000) + (minutes * 60000) + (seconds * 1000) + milliseconds
        pattern = [float(x) for x in self.pattern_var.get().split(',')] if click_type == 'pattern' else None
        self.auto_clicker = AutoClicker(button=button, click_type=click_type, interval=interval, pattern=pattern)
        self.auto_clicker.repeat_mode = self.repeat_mode_var.get()
        self.auto_clicker.repeat_count = self.repeat_var.get()

    def start_clicking(self):
        self.update_settings()
        self.auto_clicker.start_clicking()
        self.status_label.config(text="Status: Running", foreground="green")

    def stop_clicking(self):
        self.auto_clicker.stop_clicking()
        self.status_label.config(text="Status: Stopped", foreground="red")

    def toggle_clicking(self):
        if self.auto_clicker.running:
            self.stop_clicking()
        else:
            self.start_clicking()

    def save_settings(self):
        settings = {
            "button": self.button_var.get(),
            "click_type": self.type_var.get(),
            "interval": self.milliseconds_var.get(),
            "pattern": self.pattern_var.get(),
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
            self.milliseconds_var.set(settings["interval"])
            self.hotkey_var.set(settings["hotkey"])
            self.register_hotkey()
            self.update_settings()
            logging.info("Settings loaded.")
        except FileNotFoundError:
            logging.warning("Settings file not found. Using default settings.")
        except Exception as e:
            logging.error(f"Failed to load settings: {e}")

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.style = ttk.Style()
        self.root.style = self.style
        self.apply_styles()
        self.gui = AutoClickerGUI(root)

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
root = tk.Tk()
app = AutoClickerApp(root)
root.mainloop()

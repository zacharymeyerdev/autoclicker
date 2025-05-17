#!/usr/bin/env python3
"""
AutoClicker – simple cross-platform auto-click utility.

Author : Zachary Meyer
License: MIT
"""
import json
import logging
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, colorchooser

from pynput import mouse, keyboard as kb
from pynput.mouse import Button, Controller

# --------------------- logging ---------------------
logging.basicConfig(filename="autoclicker.log",
                    level=logging.INFO,
                    format="%(asctime)s %(levelname)s: %(message)s")

# ------------------- core engine -------------------
MOUSE_BUTTONS = {"left": Button.left, "right": Button.right, "middle": Button.middle}


class AutoClicker:
    def __init__(self,
                 button: str = "left",
                 click_type: str = "single",
                 interval_ms: int = 100,
                 pattern: list[float] | None = None):
        self.button = MOUSE_BUTTONS[button]
        self.click_type = click_type
        self.interval = interval_ms / 1000.0          # ms → s
        self.pattern = pattern or [self.interval]
        self.running = False
        self.mouse = Controller()
        self.thread: threading.Thread | None = None
        self.repeat_mode = "until_stopped"            # or "fixed"
        self.repeat_count = 1

    # ---------- public control ----------
    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logging.info("Auto-clicker started")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        logging.info("Auto-clicker stopped")

    # ---------- worker ----------
    def _click_once(self):
        if self.click_type == "single":
            self.mouse.click(self.button)
        elif self.click_type == "double":
            self.mouse.click(self.button)
            time.sleep(0.1)
            self.mouse.click(self.button)
        elif self.click_type == "pattern":
            for gap in self.pattern:
                if not self.running:
                    break
                self.mouse.click(self.button)
                time.sleep(gap)

    def _run(self):
        done = 0
        try:
            while self.running:
                self._click_once()
                done += 1
                if self.repeat_mode == "fixed" and done >= self.repeat_count:
                    break
                time.sleep(self.interval)
        except Exception as exc:
            logging.exception("Click loop error: %s", exc)
        finally:
            self.running = False
# --------------------- GUI ------------------------


class AutoClickerGUI(tk.Tk):
    SETTINGS_FILE = "settings.json"

    def __init__(self):
        super().__init__()
        self.title("AutoClicker")
        self.style = ttk.Style(self)
        self.clicker = AutoClicker()
        # ui-state vars
        self.var_button = tk.StringVar(value="left")
        self.var_type = tk.StringVar(value="single")
        self.var_pattern = tk.StringVar(value="1")
        self.var_cps = tk.DoubleVar(value=10.0)
        self.var_hotkey = tk.StringVar(value="f5")
        self.var_dark = tk.BooleanVar(value=False)

        self._build_ui()
        self._load_settings()
        self._bind_hotkey()      # register initial hotkey

    # --------------- ui helpers ---------------
    def _row(self, r: int, label: str, widget: ttk.Widget):
        ttk.Label(self, text=label).grid(row=r, column=0, sticky="e", padx=4, pady=4)
        widget.grid(row=r, column=1, sticky="we", padx=4, pady=4)

    def _build_ui(self):
        self.columnconfigure(1, weight=1)

        # button
        cb_btn = ttk.Combobox(self, textvariable=self.var_button,
                              values=list(MOUSE_BUTTONS.keys()), state="readonly")
        self._row(0, "Mouse button:", cb_btn)

        # click type
        cb_type = ttk.Combobox(self, textvariable=self.var_type,
                               values=["single", "double", "pattern"],
                               state="readonly")
        cb_type.bind("<<ComboboxSelected>>", self._type_changed)
        self._row(1, "Click type:", cb_type)

        # pattern
        self.ent_pattern = ttk.Entry(self, textvariable=self.var_pattern)
        self._row(2, "Pattern (s):", self.ent_pattern)

        # cps
        self.ent_cps = ttk.Entry(self, textvariable=self.var_cps, width=8)
        self._row(3, "Clicks / sec:", self.ent_cps)


        # hotkey
        ent_hot = ttk.Entry(self, textvariable=self.var_hotkey, width=10)
        self._row(4, "Hotkey:", ent_hot)

        # buttons
        frame_btn = ttk.Frame(self)
        ttk.Button(frame_btn, text="Start", command=self.start_clicking).pack(side="left", padx=2)
        ttk.Button(frame_btn, text="Stop", command=self.stop_clicking).pack(side="left", padx=2)
        ttk.Button(frame_btn, text="Save", command=self._save_settings).pack(side="left", padx=2)
        ttk.Button(frame_btn, text="Quit", command=self.destroy).pack(side="left", padx=2)
        frame_btn.grid(row=5, column=0, columnspan=2, pady=6)

        # dark-mode & colors
        ttk.Checkbutton(self, text="Dark mode", variable=self.var_dark,
                        command=self._apply_theme).grid(row=6, column=0, sticky="w", padx=4, pady=4)
        ttk.Button(self, text="BG color", command=self._pick_bg).grid(row=6, column=1, sticky="e", padx=4)

        # status
        self.lbl_status = ttk.Label(self, text="Status: Stopped", foreground="red")
        self.lbl_status.grid(row=7, column=0, columnspan=2, pady=4)

        self._type_changed()  # set pattern field state
        self._apply_theme()

    def _type_changed(self, *_):
        click_type = self.var_type.get()

        # Enable both by default
        self.ent_pattern.configure(state="normal")
        self.ent_cps.configure(state="normal")

        # Adjust based on click type
        if click_type == "pattern":
            self.ent_cps.configure(state="disabled")
        else:
            self.ent_pattern.configure(state="disabled")

    # --------------- start / stop ---------------
    def start_clicking(self):
        if self.clicker.running:
            return

        # Try parsing pattern
        pattern = None
        if self.var_type.get() == "pattern":
            try:
                pattern = [float(x.strip()) for x in self.var_pattern.get().split(",") if x.strip()]
            except ValueError:
                messagebox.showerror("Invalid pattern", "Could not parse pattern values.")
                return

        try:
            cps = max(self.var_cps.get(), 0.1)
            interval_ms = int(1000 / cps)
        except tk.TclError:
            messagebox.showerror("Invalid CPS", "Enter a valid number for clicks/sec.")
            return

        self.clicker = AutoClicker(
            button=self.var_button.get(),
            click_type=self.var_type.get(),
            interval_ms=interval_ms,
            pattern=pattern
        )
        self.clicker.start()
        self.lbl_status.config(text="Status: Running", foreground="green")

    def stop_clicking(self):
        self.clicker.stop()
        self.lbl_status.config(text="Status: Stopped", foreground="red")

    # --------------- hotkey handling ---------------
    def _bind_hotkey(self):
        try:
            kb.GlobalHotKeys({f'<{self.var_hotkey.get()}>': self._toggle_clicking}).start()
            logging.info("Registered hotkey %s", self.var_hotkey.get())
        except ValueError as exc:
            messagebox.showerror("Hotkey error", str(exc))

    def _toggle_clicking(self):
        self.stop_clicking() if self.clicker.running else self.start_clicking()

    # --------------- theme / colors ---------------
    def _apply_theme(self):
        if self.var_dark.get():
            self.style.theme_use("clam")
            self.style.configure(".", background="#2b2b2b", foreground="#e6e6e6")
            self.configure(background="#2b2b2b")
        else:
            self.style.theme_use("default")
            self.configure(background=self.style.lookup(".", "background"))

    def _pick_bg(self):
        col = colorchooser.askcolor(title="Pick background")[1]
        if col:
            self.configure(bg=col)

    # --------------- settings I/O ---------------
    def _save_settings(self):
        data = {
            "button": self.var_button.get(),
            "click_type": self.var_type.get(),
            "pattern": self.var_pattern.get(),
            "cps": self.var_cps.get(),
            "hotkey": self.var_hotkey.get(),
            "dark": self.var_dark.get()
        }
        with open(self.SETTINGS_FILE, "w") as fp:
            json.dump(data, fp, indent=2)
        logging.info("Settings saved")

    def _load_settings(self):
        try:
            with open(self.SETTINGS_FILE) as fp:
                data = json.load(fp)
            self.var_button.set(data["button"])
            self.var_type.set(data["click_type"])
            self.var_pattern.set(data["pattern"])
            self.var_cps.set(float(data["cps"]))
            self.var_hotkey.set(data["hotkey"])
            self.var_dark.set(data.get("dark", False))
        except FileNotFoundError:
            logging.info("No settings file – using defaults")

# -------------------- main ------------------------
if __name__ == "__main__":
    AutoClickerGUI().mainloop()

# AutoClicker

A lightweight, cross-platform Python utility for **automating mouse clicks**.  
It ships with an intuitive Tkinter GUI, dark-mode support, configurable click
patterns, and a global hotkey so you can toggle it from any application.

---

## ✨ Features

| Category | Details |
| :-- | :-- |
| **Click Options** | Left / right / middle button · Single, double, or custom-pattern clicks |
| **Speed Control** | Adjustable CPS (clicks-per-second) or millisecond interval |
| **Pattern Mode** | Comma-separated timing list (e.g. `0.2,1,0.2` repeats in order) |
| **Hotkey** | Global start/stop hotkey (default **F5** – configurable) |
| **Dark Mode** | One-click theme toggle or custom background / text colours |
| **Profiles** | Settings auto-saved to `settings.json` and re-loaded on launch |
| **Logging** | Creates `autoclicker.log` with timestamps for troubleshooting |

---

## 🛠 Requirements

| Package | Purpose |
| :-- | :-- |
| **Python ≥ 3.9** | Core runtime |
| **tkinter** | GUI framework (bundled with Python on Windows/macOS) |
| **pynput ≥ 1.7** | Mouse control & global hotkeys |

Install dependencies with:

```bash
python -m pip install -r requirements.txt
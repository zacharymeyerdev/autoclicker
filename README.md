# autoclicker
This is a work in progress and is very annoying to iron out.
Formatting, commenting, and bug fixing helped out by ChatGPT/Copilot.

### README.md
```markdown
# AutoClicker

## Overview
AutoClicker is a simple application that allows you to automate mouse clicks. You can customize the button to click, the click type (single, double, pattern), and the clicks per second (CPS). The application also supports hotkeys to start and stop clicking.

## Features
- Select mouse button (left, right, middle)
- Choose click type (single, double, pattern)
- Set clicks per second (CPS)
- Define custom click patterns
- Dark mode support
- Hotkey to toggle auto-clicker
- Save and load settings

## Requirements
- Python 3.x
- Tkinter
- Pynput
- Keyboard

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/autoclicker.git
   ```
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Run the application:
   ```bash
   python main.py
   ```
2. Configure the settings in the GUI.
3. Start and stop the auto-clicker using the GUI or the assigned hotkey.

## Settings
- **Button:** Select the mouse button to click.
- **Click Type:** Choose between single, double, or pattern clicks.
- **Pattern Intervals:** Define intervals for pattern clicks (e.g., `1,0.5,1.5`).
- **Clicks Per Second:** Set the number of clicks per second.
- **Hotkey:** Set a hotkey to toggle the auto-clicker.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License.
```

### settings.json
```json
{
    "button": "left",
    "click_type": "single",
    "pattern": "1",
    "cps": "1",
    "hotkey": "f5"
}
```

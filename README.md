# Auto Key Presser - README

## Download

Executable users: You can download the ready-to-run .exe from the repository's `dist` folder: <repository-url>/dist

## Features

- **Automatic Key Pressing:** Configure any number of keys to be pressed automatically at custom intervals (in milliseconds).
- **Per-Key Enable/Disable:** Each key can be toggled active/inactive individually using a real checkbox in the table.
- **Window Picker:** Select the exact window that should receive the key presses from a live dropdown list of open windows. Key presses are only sent to the selected window, ensuring safe and targeted automation.
- **Add/Remove Keys Easily:** Add new key+interval pairs with a simple form. Remove any key by selecting its row and clicking "Remove".
- **Edit Intervals On-the-Fly:** Double-click the interval cell to change the timing for any key.
- **Multi-language Support:** Instantly switch between English, Portuguese, and Spanish (or add your own language file).
- **Global Hotkeys:** Start/Stop automation from anywhere using F7 (Start) and F8 (Stop).
- **Persistent Configuration:** All your settings and key lists are saved and restored automatically.
- **Modern, Intuitive UI:** Clean, resizable interface with a PayPal donate button and clear status indicators.

## How to Use

### 1. Window Picker

- At the top, use the dropdown to select the window that should receive the key presses. Only the selected window will be targeted.
- The list updates automatically to show all open windows.

### 2. Adding Keys

- Enter the key you want to automate (e.g., `z`, `space`, `f1`) in the "Key" field.
- Enter the interval in milliseconds (e.g., `1000` for 1 second) in the "Interval (ms)" field.
- Click "Add" to insert the new key into the table. It will be enabled by default.

### 3. Removing Keys

- Click on a row in the table to select it.
- Click "Remove" to delete that key from the list.

### 4. Enabling/Disabling Keys

- Use the checkbox in the "Active" column to enable or disable each key individually.
- Only checked (active) keys will be pressed when automation is running.

### 5. Editing Intervals

- Double-click the interval cell for any key to edit its timing.
- Enter a new value in milliseconds and press Enter.

### 6. Starting and Stopping

- Click "Start" to begin pressing all active keys at their configured intervals, targeted to the selected window.
- Click "Stop" to halt all automation.
- You can also use the global hotkeys: F7 (Start) and F8 (Stop).

### 7. Language Selection

- Click the "Language" button to instantly switch the app's language.

### 8. Donate

- Click the PayPal button at the bottom to support the developer if you find the app useful!

---

For advanced usage, adding new languages, or building your own executable, see the rest of this README and the repository documentation.

## Advanced Usage

### Building a Standalone Executable (Windows)

You can package this app as a single .exe file (with icon and all resources) using PyInstaller and the provided `autokeypresser.spec` file.

#### Steps:

1. **Install PyInstaller** (if not already installed):

   ```powershell
   pip install pyinstaller
   ```

2. **Build the Executable**
   From the project directory, run:

   ```powershell
   python -m PyInstaller autokeypresser.spec
   ```

   This will use all the settings and data files defined in the `.spec` file, including the application icon (`autokeypresser.ico`).

3. **Find Your Executable**
   The resulting `.exe` will be in the `dist` folder as `autokeypresser.exe`.

4. **Distribute**
   You can now send the `.exe` to others. They do **not** need Python or pip installed.

## Multi-language Support

To add a new language:

1. Create a new text file (e.g., "fr.txt" for French)
2. Add all required key-value pairs (copy structure from existing language files)
3. Edit the values with your translations
4. Add the language to `locales.json`:

```json
{
  "languages": [
    ...,
    {
      "code": "fr",
      "name": "Français",
      "file": "fr.txt"
    }
  ]
}
```

## Troubleshooting

- **Keys Not Pressing:** Ensure the correct window is selected in the Window Picker. Check that the keys are active (checked) in the list.
- **Interval Changes Not Saving:** Make sure to press Enter after typing a new interval. The row should update to show the new value.
- **Language Not Changing:** If the language doesn't change, ensure the language file is correctly formatted and added to `locales.json`.

For further issues, consult the repository's issue tracker or documentation.

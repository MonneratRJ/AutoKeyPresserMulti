import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import keyboard
import queue
import json
from i18n import I18nManager
import style
import window_utils

class KeyPresserApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("500x500")

        # Set application icon
        icon_path = 'autokeypresser.png'  # or .ico
        try:
            img = tk.PhotoImage(file=icon_path)
            self.root.tk.call('wm', 'iconphoto', self.root._w, img)
        except:
            try:
                self.root.iconbitmap('autokeypresser.ico')
            except:
                pass  # Silently fail if no icon is found
        
        # Configuration files
        self.config_file = "config.json"
        self.locales_file = "locales.json"
        
        # Language and localization
        self.i18n = I18nManager()
        self.current_language = self.i18n.get_current_language()
        self.texts = self.i18n.texts
        self.available_languages = self.i18n.get_available_languages()
        
        # Data storage
        self.key_configs = []
        self.timers = {}
        self.is_running = False
        
        # Key press queue and lock for synchronization
        self.key_queue = queue.Queue()
        self.key_lock = threading.Lock()
        self.key_press_thread = None
        
        # Editing state
        self.edit_entry = None
        self.edit_item = None
        self.edit_column = None
        
        # Window selection
        self.selected_window = None
        
        # Load configuration and language
        self.load_config()
        style.setup_ui(self)
        self.setup_hotkeys()
        self.update_ui_texts()
        self.update_tree()
        self.update_window_list()
        
        # After UI setup, update window list
        self.update_window_list()
        
        # Store references to checkbuttons and their variables
        self.checkbuttons = {}
        self.checkbox_vars = {}
        
    def on_single_click(self, event):
        """Handle single click to cancel editing if clicking elsewhere"""
        if self.edit_entry:
            # Check if click is not on the edit entry
            try:
                widget = event.widget.winfo_containing(event.x_root, event.y_root)
                if widget != self.edit_entry:
                    self.cancel_edit()
            except:
                self.cancel_edit()
    
    def on_double_click(self, event):
        """Handle double click for toggling active state or editing interval"""
        if self.is_running:
            return  # Don't allow editing while running
            
        # Cancel any existing edit
        if self.edit_entry:
            self.cancel_edit()
            
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return
            
        item = self.tree.identify_row(event.y)
        if not item:
            return
            
        column = self.tree.identify_column(event.x)
        
        if column == '#2':  # Interval column
            self.start_edit(item, 'interval', event.x, event.y)
    
    def toggle_active_by_item(self, item):
        """Toggle active state for a specific tree item"""
        index = self.tree.index(item)
        if 0 <= index < len(self.key_configs):
            self.key_configs[index]['active'] = not self.key_configs[index]['active']
            self.update_tree()
            self.save_config()
    
    def start_edit(self, item, column, x, y):
        """Start editing a cell"""
        if self.is_running:
            return
            
        # Get the bounding box of the cell
        bbox = self.tree.bbox(item, column)
        if not bbox:
            return
            
        self.edit_item = item
        self.edit_column = column
        
        # Get current value
        index = self.tree.index(item)
        if column == 'interval' and 0 <= index < len(self.key_configs):
            current_value = str(self.key_configs[index]['interval'])
        else:
            return
            
        # Create entry widget
        self.edit_entry = tk.Entry(self.tree, borderwidth=1, highlightthickness=1)
        self.edit_entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        
        # Set current value and select all
        self.edit_entry.insert(0, current_value)
        self.edit_entry.select_range(0, tk.END)
        self.edit_entry.focus()
        
        # Bind events
        self.edit_entry.bind('<Return>', self.save_edit)
        self.edit_entry.bind('<Escape>', self.cancel_edit)
        self.edit_entry.bind('<FocusOut>', self.save_edit)
        self.edit_entry.bind('<KeyPress>', self.on_edit_keypress)
    
    def on_edit_keypress(self, event):
        """Handle keypress in edit entry - only allow digits"""
        if event.keysym in ('BackSpace', 'Delete', 'Left', 'Right', 'Home', 'End', 'Tab'):
            return True
        if not event.char.isdigit():
            return "break"
    
    def save_edit(self, event=None):
        """Save the edited value"""
        if not self.edit_entry or not self.edit_item:
            return
            
        new_value = self.edit_entry.get().strip()
        
        # Validate the new value
        try:
            interval = int(new_value)
            if interval <= 0:
                raise ValueError("Interval must be positive")
        except ValueError:
            messagebox.showerror(self.get_text("error_title"), 
                               self.get_text("error_valid_interval"))
            self.edit_entry.focus()
            return
        
        # Update the configuration
        index = self.tree.index(self.edit_item)
        if 0 <= index < len(self.key_configs):
            self.key_configs[index]['interval'] = interval
            self.update_tree()
            self.save_config()
        
        self.cleanup_edit()
    
    def cancel_edit(self, event=None):
        """Cancel editing without saving"""
        self.cleanup_edit()
    
    def cleanup_edit(self):
        """Clean up editing widgets and state"""
        if self.edit_entry:
            self.edit_entry.destroy()
            self.edit_entry = None
        self.edit_item = None
        self.edit_column = None
        self.tree.focus()
        
    def show_language_menu(self):
        """Show language selection menu"""
        menu = tk.Menu(self.root, tearoff=0)
        for lang in self.available_languages:
            menu.add_command(
                label=lang['name'], 
                command=lambda l=lang['code']: self.change_language(l)
            )
        
        # Show menu at button position
        try:
            x = self.language_button.winfo_rootx()
            y = self.language_button.winfo_rooty() + self.language_button.winfo_height()
            menu.post(x, y)
        except:
            menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())
    
    def change_language(self, language_code):
        """Change application language"""
        if language_code != self.current_language:
            self.i18n.change_language(language_code)
            self.current_language = self.i18n.get_current_language()
            self.texts = self.i18n.texts
            self.available_languages = self.i18n.get_available_languages()
            self.update_ui_texts()
            self.save_config()

    def update_ui_texts(self):
        """Update all UI texts with current language"""
        self.root.title(self.get_text("app_title"))
        self.title_label.config(text=self.get_text("app_title"))
        self.language_button.config(text=self.get_text("language_button"))
        self.key_label.config(text=self.get_text("key_label"))
        self.interval_label.config(text=self.get_text("interval_label"))
        self.add_button.config(text=self.get_text("add_button"))
        self.remove_button.config(text=self.get_text("remove_button"))
        self.start_button.config(text=self.get_text("start_button"))
        self.stop_button.config(text=self.get_text("stop_button"))
        
        # Update treeview headers
        self.tree.heading('#0', text=self.get_text("header_active"))
        self.tree.heading('key', text=self.get_text("header_key"))
        self.tree.heading('interval', text=self.get_text("header_interval"))
        
        # Update status and hotkey labels
        if self.is_running:
            self.status_label.config(text=self.get_text("status_running"))
        else:
            self.status_label.config(text=self.get_text("status_stopped"))
        
        self.hotkey_label.config(text=self.get_text("hotkeys_info"))
        
    def load_config(self):
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.key_configs = config.get('key_configs', [])
                self.current_language = config.get('language', 'en')
                self.i18n.change_language(self.current_language)
                self.texts = self.i18n.texts
        except FileNotFoundError:
            # Create default config with sample data
            self.key_configs = [
                {'key': 'z', 'interval': 1000, 'active': True},
                {'key': 'x', 'interval': 2000, 'active': False},
                {'key': 'y', 'interval': 3000, 'active': True}
            ]
            self.save_config()
        except Exception as e:
            messagebox.showerror("Error", f"Error loading config: {e}")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            config = {
                'key_configs': self.key_configs,
                'language': self.current_language
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"Error saving config: {e}")
    
    def add_key_config(self):
        key = self.key_entry.get().strip().lower()
        interval_text = self.interval_entry.get().strip()
        
        if not key:
            messagebox.showerror(self.get_text("error_title"), self.get_text("error_enter_key"))
            return
            
        try:
            interval = int(interval_text)
            if interval <= 0:
                raise ValueError("Interval must be positive")
        except ValueError:
            messagebox.showerror(self.get_text("error_title"), self.get_text("error_valid_interval"))
            return
            
        # Check if key already exists
        for config in self.key_configs:
            if config['key'] == key:
                messagebox.showerror(self.get_text("error_title"), 
                                   self.get_text("error_key_exists").replace('{key}', key))
                return
                
        self.key_configs.append({
            'key': key,
            'interval': interval,
            'active': True
        })
        
        self.update_tree()
        self.key_entry.delete(0, tk.END)
        self.interval_entry.delete(0, tk.END)
        self.save_config()  # Save after adding
        
    def remove_key_config(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(self.get_text("warning_title"), self.get_text("warning_select_row"))
            return
            
        item = selection[0]
        index = self.tree.index(item)
        
        if 0 <= index < len(self.key_configs):
            self.key_configs.pop(index)
            self.update_tree()
            self.save_config()  # Save after removing
            
    def toggle_active(self, event):
        """Legacy method - now handled by on_double_click"""
        pass
            
    def update_tree(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Remove old checkbuttons
        for cb in getattr(self, 'checkbuttons', {}).values():
            cb.destroy()
        self.checkbuttons = {}
        self.checkbox_vars = {}
        # Add current configurations and overlay checkboxes
        for idx, config in enumerate(self.key_configs):
            item_id = self.tree.insert('', 'end', values=(config['key'], config['interval']))
            self.place_checkbox(item_id, idx)

    def place_checkbox(self, item_id, idx):
        bbox = self.tree.bbox(item_id, '#0')
        if not bbox:
            self.root.after(10, lambda: self.place_checkbox(item_id, idx))
            return
        # Store BooleanVar to keep it alive
        var = self.checkbox_vars[idx] = tk.BooleanVar(value=self.key_configs[idx]['active'])
        cb = ttk.Checkbutton(self.tree, variable=var, command=lambda i=idx, v=var: self.on_checkbox_toggle(i, v), takefocus=0)
        cb_width = 18
        cb_height = 18
        x = bbox[0] + (bbox[2] - cb_width) // 2
        y = bbox[1] + (bbox[3] - cb_height) // 2
        cb.place(x=x, y=y, width=cb_width, height=cb_height)
        self.checkbuttons[item_id] = cb

    def on_checkbox_toggle(self, idx, var):
        self.key_configs[idx]['active'] = var.get()
        self.save_config()

    def update_tree_checkboxes(self):
        # Reposition checkboxes after scroll/resize
        for idx, item_id in enumerate(self.tree.get_children()):
            self.place_checkbox(item_id, idx)

    def setup_hotkeys(self):
        """Setup global hotkeys for start/stop functionality"""
        try:
            keyboard.add_hotkey('f7', self.start_pressing)
            keyboard.add_hotkey('f8', self.stop_pressing)
        except Exception as e:
            # If hotkey setup fails, continue without hotkeys
            pass
            
    def key_press_manager(self):
        """Manager thread that processes key presses with minimum delay"""
        while self.is_running:
            try:
                # Get next key from queue with timeout
                key_to_press = self.key_queue.get(timeout=0.25)
                
                win_info = self.get_selected_window_info()
                if win_info:
                    window_utils.send_key_to_window(win_info, key_to_press)
                
                # Minimum delay of 250ms between key presses
                time.sleep(0.25) # 250ms delay
                
                self.key_queue.task_done()
                
            except queue.Empty:
                # No keys in queue, continue
                continue
            except Exception as e:
                # Log errors silently
                pass
                
    def key_press_worker(self, key, interval):
        """Worker function for scheduling key presses at intervals"""
        timer_id = f"{key}_{interval}"
        while self.is_running and timer_id in self.timers:
            try:
                # Only send key if a window is selected
                if self.selected_window:
                    window_utils.send_key_to_window(self.selected_window, key)
            except Exception as e:
                pass
            time.sleep(interval / 1000.0)  # Convert ms to seconds
            
    def start_pressing(self):
        if self.is_running:
            return
        if self.edit_entry:
            self.cancel_edit()
        active_configs = [config for config in self.key_configs if config['active']]
        if not active_configs:
            messagebox.showwarning(self.get_text("warning_title"), self.get_text("warning_no_active"))
            return
        self.is_running = True
        self.timers = {}
        self.key_press_thread = threading.Thread(target=self.key_press_manager)
        self.key_press_thread.daemon = True
        self.key_press_thread.start()
        for config in active_configs:
            key = config['key']
            interval = config['interval']
            timer_id = f"{key}_{interval}"
            thread = threading.Thread(target=self.key_press_worker, args=(key, interval))
            thread.daemon = True
            self.timers[timer_id] = thread
            thread.start()
        # Disable all controls except STOP
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.add_button.config(state='disabled')
        self.remove_button.config(state='disabled')
        self.key_entry.config(state='disabled')
        self.interval_entry.config(state='disabled')
        self.tree.config(selectmode='none')
        if hasattr(self, 'window_combo'):
            self.window_combo.config(state='disabled')
        self.status_label.config(text=self.get_text("status_running"), foreground="green")
        
    def stop_pressing(self):
        if not self.is_running:
            return
        self.is_running = False
        self.timers = {}
        while not self.key_queue.empty():
            try:
                self.key_queue.get_nowait()
            except queue.Empty:
                break
        # Re-enable all controls
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.add_button.config(state='normal')
        self.remove_button.config(state='normal')
        self.key_entry.config(state='normal')
        self.interval_entry.config(state='normal')
        self.tree.config(selectmode='extended')
        if hasattr(self, 'window_combo'):
            self.window_combo.config(state='readonly')
        self.status_label.config(text=self.get_text("status_stopped"), foreground="red")
        
    def on_closing(self):
        """Handle application closing"""
        self.stop_pressing()
        try:
            # Remove hotkeys before closing
            keyboard.unhook_all_hotkeys()
        except:
            pass
        self.root.destroy()

    def get_text(self, key, **kwargs):
        return self.i18n.get_text(key, **kwargs)

    def update_window_list(self):
        windows = window_utils.list_windows()
        self.window_list = windows  # Store full window info dicts
        if hasattr(self, 'window_combo'):
            # Update combobox with window titles
            titles = [w['title'] for w in windows]
            self.window_combo['values'] = titles
            if titles:
                self.window_combo.current(0)
                self.selected_window = windows[0]
            else:
                self.selected_window = None

    def on_window_select(self, event=None):
        if hasattr(self, 'window_combo'):
            idx = self.window_combo.current()
            if 0 <= idx < len(self.window_list):
                self.selected_window = self.window_list[idx]
            else:
                self.selected_window = None

    def get_selected_window_info(self):
        if hasattr(self, 'selected_window_index') and self.selected_window_index is not None:
            if 0 <= self.selected_window_index < len(self.window_infos):
                return self.window_infos[self.selected_window_index]
        return None

    def focus_selected_window(self):
        win_info = self.get_selected_window_info()
        if win_info:
            window_utils.focus_window(win_info)

def main():
    try:
        # Check if keyboard library is available
        import keyboard
    except ImportError:
        messagebox.showerror("Error", "'keyboard' library is required. Install it with: pip install keyboard")
        return
        
    root = tk.Tk()
    app = KeyPresserApp(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    root.mainloop()

if __name__ == "__main__":
    main()
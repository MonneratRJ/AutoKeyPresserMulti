import sys
import threading
import time
import queue
import json
import os

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QMessageBox, QMenu, QLineEdit, QTreeWidgetItem, QCheckBox)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QIcon, QCursor

from i18n import I18nManager
import style
import window_utils
from resource_utils import resource_path

class KeyPresserApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 500, 500)
        self.setWindowTitle("Auto Key Presser")
        # Set application icon using resource_path for reliability
        ico_path = resource_path('autokeypresser.ico')
        png_path = resource_path('autokeypresser.png')
        if os.path.exists(ico_path):
            self.setWindowIcon(QIcon(ico_path))
        elif os.path.exists(png_path):
            self.setWindowIcon(QIcon(png_path))
        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
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
        # All UI setup and signal connections are handled in style.setup_ui(self)
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
        
        # Connect signals (replace with full logic)
        self.add_button.clicked.connect(self.add_key_config)
        self.remove_button.clicked.connect(self.remove_key_config)
        self.start_button.clicked.connect(self.start_pressing)
        self.stop_button.clicked.connect(self.stop_pressing)
        self.language_button.clicked.connect(self.show_language_menu)
        self.tree.itemDoubleClicked.connect(self.on_double_click)
    
    def on_double_click(self, item, column):
        """Handle double click for toggling active state or editing interval"""
        if self.is_running:
            return  # Don't allow editing while running
            
        # Cancel any existing edit
        if self.edit_entry:
            self.cancel_edit()
            
        if column == 2:  # Interval column
            self.start_edit(item, 'interval', item.treeWidget().visualItemRect(item).x() + item.treeWidget().header().sectionSize(2), item.treeWidget().visualItemRect(item).y())
    
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
            
        self.edit_item = item
        self.edit_column = column
        
        # Get current value
        index = self.tree.index(item)
        if column == 'interval' and 0 <= index < len(self.key_configs):
            current_value = str(self.key_configs[index]['interval'])
        else:
            return
            
        # Create entry widget
        self.edit_entry = QLineEdit(self.tree)
        self.edit_entry.setFrame(True)
        self.edit_entry.setGeometry(x, y, 100, 20)
        
        # Set current value and select all
        self.edit_entry.setText(current_value)
        self.edit_entry.selectAll()
        self.edit_entry.setFocus()
        
        # Bind events
        self.edit_entry.returnPressed.connect(self.save_edit)
        self.edit_entry.editingFinished.connect(self.save_edit)
        self.edit_entry.focusOutEvent = lambda event: self.cancel_edit()
        self.edit_entry.keyPressEvent = self.on_edit_keypress
    
    def on_edit_keypress(self, event):
        """Handle keypress in edit entry - only allow digits"""
        if event.key() in (Qt.Key_Backspace, Qt.Key_Delete, Qt.Key_Left, Qt.Key_Right, Qt.Key_Home, Qt.Key.End, Qt.Key_Tab):
            return
        if not event.text().isdigit():
            event.ignore()
    
    def save_edit(self):
        """Save the edited value"""
        if not self.edit_entry or not self.edit_item:
            return
            
        new_value = self.edit_entry.text().strip()
        
        # Validate the new value
        try:
            interval = int(new_value)
            if interval <= 0:
                raise ValueError("Interval must be positive")
        except ValueError:
            QMessageBox.critical(self, self.get_text("error_title"), 
                               self.get_text("error_valid_interval"))
            self.edit_entry.setFocus()
            return
        
        # Update the configuration
        index = self.tree.index(self.edit_item)
        if 0 <= index < len(self.key_configs):
            self.key_configs[index]['interval'] = interval
            self.update_tree()
            self.save_config()
        
        self.cleanup_edit()
    
    def cancel_edit(self):
        """Cancel editing without saving"""
        self.cleanup_edit()
    
    def cleanup_edit(self):
        """Clean up editing widgets and state"""
        if self.edit_entry:
            self.edit_entry.deleteLater()
            self.edit_entry = None
        self.edit_item = None
        self.edit_column = None
        self.tree.setFocus()
        
    def show_language_menu(self):
        """Show language selection menu"""
        menu = QMenu(self)
        for lang in self.available_languages:
            menu.addAction(
                lang['name'], 
                lambda l=lang['code']: self.change_language(l)
            )
        
        # Show menu at button position
        try:
            x = self.language_button.mapToGlobal(self.language_button.rect().bottomLeft()).x()
            y = self.language_button.mapToGlobal(self.language_button.rect().bottomLeft()).y()
            menu.exec(QPoint(x, y))
        except:
            menu.exec(QCursor.pos())
    
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
        self.setWindowTitle(self.get_text("app_title"))
        self.title_label.setText(self.get_text("app_title"))
        self.language_button.setText(self.get_text("language_button"))
        self.key_label.setText(self.get_text("key_label"))
        self.interval_label.setText(self.get_text("interval_label"))
        self.add_button.setText(self.get_text("add_button"))
        self.remove_button.setText(self.get_text("remove_button"))
        self.start_button.setText(self.get_text("start_button"))
        self.stop_button.setText(self.get_text("stop_button"))
        
        # Update treeview headers
        self.tree.setHeaderLabels([self.get_text("header_active"), self.get_text("header_key"), self.get_text("header_interval")])
        
        # Update status and hotkey labels
        if self.is_running:
            self.status_label.setText(self.get_text("status_running"))
        else:
            self.status_label.setText(self.get_text("status_stopped"))
        
        self.hotkey_label.setText(self.get_text("hotkeys_info"))
        
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
            QMessageBox.critical(self, "Error", f"Error loading config: {e}")
    
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
            QMessageBox.critical(self, "Error", f"Error saving config: {e}")
    
    def add_key_config(self):
        key = self.key_entry.text().strip().lower()
        interval_text = self.interval_entry.text().strip()
        
        if not key:
            QMessageBox.critical(self, self.get_text("error_title"), self.get_text("error_enter_key"))
            return
            
        try:
            interval = int(interval_text)
            if interval <= 0:
                raise ValueError("Interval must be positive")
        except ValueError:
            QMessageBox.critical(self, self.get_text("error_title"), self.get_text("error_valid_interval"))
            return
            
        # Check if key already exists
        for config in self.key_configs:
            if config['key'] == key:
                QMessageBox.critical(self, self.get_text("error_title"), 
                                   self.get_text("error_key_exists").replace('{key}', key))
                return
                
        self.key_configs.append({
            'key': key,
            'interval': interval,
            'active': True
        })
        
        self.update_tree()
        self.key_entry.clear()
        self.interval_entry.clear()
        self.save_config()  # Save after adding
        
    def remove_key_config(self):
        selection = self.tree.selectedItems()
        if not selection:
            QMessageBox.warning(self, self.get_text("warning_title"), self.get_text("warning_select_row"))
            return
            
        item = selection[0]
        index = self.tree.indexOfTopLevelItem(item)
        
        if 0 <= index < len(self.key_configs):
            self.key_configs.pop(index)
            self.update_tree()
            self.save_config()  # Save after removing
            
    def update_tree(self):
        # Clear existing items
        self.tree.clear()
        # Remove old checkbuttons
        for cb in getattr(self, 'checkbuttons', {}).values():
            cb.deleteLater()
        self.checkbuttons = {}
        self.checkbox_vars = {}
        # Add current configurations and overlay checkboxes
        for idx, config in enumerate(self.key_configs):
            item = QTreeWidgetItem([config['active'], config['key'], str(config['interval'])])
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.tree.addTopLevelItem(item)
            self.place_checkbox(item, idx)

    def place_checkbox(self, item, idx):
        # Checkboxes are now part of the QTreeWidgetItem, no manual placement needed
        var = self.checkbox_vars[idx] = QCheckBox()
        var.setChecked(self.key_configs[idx]['active'])
        var.stateChanged.connect(lambda state, i=idx: self.on_checkbox_toggle(i, state))
        self.checkbuttons[item] = var

    def on_checkbox_toggle(self, idx, state):
        self.key_configs[idx]['active'] = (state == Qt.Checked)
        self.save_config()

    def update_tree_checkboxes(self):
        # Reposition checkboxes after scroll/resize
        for idx, item in enumerate(self.tree.findItems("", Qt.MatchContains | Qt.MatchRecursive)):
            self.place_checkbox(item, idx)

    def setup_hotkeys(self):
        """Setup global hotkeys for start/stop functionality"""
        try:
            import keyboard
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
            QMessageBox.warning(self, self.get_text("warning_title"), self.get_text("warning_no_active"))
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
        self.set_controls_enabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText(self.get_text("status_running"))

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
        self.set_controls_enabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText(self.get_text("status_stopped"))
        
    def on_closing(self):
        """Handle application closing"""
        self.stop_pressing()
        try:
            # Remove hotkeys before closing
            import keyboard
            keyboard.unhook_all_hotkeys()
        except:
            pass
        self.close()

    def get_text(self, key, **kwargs):
        return self.i18n.get_text(key, **kwargs)

    def update_window_list(self):
        windows = window_utils.list_windows()
        self.window_list = windows  # Store full window info dicts
        if hasattr(self, 'window_combo'):
            # Update combobox with window titles
            titles = [w['title'] for w in windows]
            self.window_combo.clear()
            self.window_combo.addItems(titles)
            if titles:
                self.window_combo.setCurrentIndex(0)
                self.selected_window = windows[0]
            else:
                self.selected_window = None

    def on_window_select(self, event=None):
        if hasattr(self, 'window_combo'):
            idx = self.window_combo.currentIndex()
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

    def set_controls_enabled(self, enabled: bool):
        state = Qt.Enabled if enabled else Qt.Disabled
        self.start_button.setEnabled(state)
        self.add_button.setEnabled(state)
        self.remove_button.setEnabled(state)
        self.key_entry.setEnabled(state)
        self.interval_entry.setEnabled(state)
        self.tree.setEnabled(state)
        if hasattr(self, 'window_combo'):
            self.window_combo.setEnabled(state == Qt.Enabled)

def main():
    app = QApplication(sys.argv)
    # Set the application icon on QApplication as early as possible
    ico_path = os.path.abspath('autokeypresser.ico')
    png_path = os.path.abspath('autokeypresser.png')
    if os.path.exists(ico_path):
        app.setWindowIcon(QIcon(ico_path))
    elif os.path.exists(png_path):
        app.setWindowIcon(QIcon(png_path))
    window = KeyPresserApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
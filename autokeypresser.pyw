import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import keyboard
import queue
import json

class KeyPresserApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("500x500")
        
        # Configuration files
        self.config_file = "config.json"
        self.locales_file = "locales.json"
        
        # Language and localization
        self.current_language = "en"
        self.texts = {}
        self.available_languages = []
        
        # Data storage
        self.key_configs = []
        self.timers = {}
        self.is_running = False
        
        # Key press queue and lock for synchronization
        self.key_queue = queue.Queue()
        self.key_lock = threading.Lock()
        self.key_press_thread = None
        
        # Load configuration and language
        self.load_languages()
        self.load_texts()
        self.load_config()
        
        self.setup_ui()
        self.setup_hotkeys()
        self.update_ui_texts()
        self.update_tree()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Header frame with title and language button
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ttk.Label(header_frame, text="Auto Key Presser", font=("Arial", 16, "bold"))
        self.title_label.grid(row=0, column=0)
        
        # Language button
        self.language_button = ttk.Button(header_frame, text="Language", command=self.show_language_menu)
        self.language_button.grid(row=0, column=1, padx=(10, 0))
        
        # Add entry frame
        entry_frame = ttk.Frame(main_frame)
        entry_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.key_label = ttk.Label(entry_frame, text="Key:")
        self.key_label.grid(row=0, column=0, padx=(0, 5))
        self.key_entry = ttk.Entry(entry_frame, width=10)
        self.key_entry.grid(row=0, column=1, padx=(0, 10))
        
        self.interval_label = ttk.Label(entry_frame, text="Interval (ms):")
        self.interval_label.grid(row=0, column=2, padx=(0, 5))
        self.interval_entry = ttk.Entry(entry_frame, width=10)
        self.interval_entry.grid(row=0, column=3, padx=(0, 10))
        
        self.add_button = ttk.Button(entry_frame, text="Add", command=self.add_key_config)
        self.add_button.grid(row=0, column=4, padx=(0, 5))
        self.remove_button = ttk.Button(entry_frame, text="Remove", command=self.remove_key_config)
        self.remove_button.grid(row=0, column=5)
        
        # Table frame
        table_frame = ttk.Frame(main_frame)
        table_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Treeview for the table
        self.tree = ttk.Treeview(table_frame, columns=('key', 'interval'), show='tree headings', height=10)
        self.tree.heading('#0', text='Active')
        self.tree.heading('key', text='Key')
        self.tree.heading('interval', text='Interval (ms)')
        
        self.tree.column('#0', width=80, anchor='center')
        self.tree.column('key', width=150, anchor='center')
        self.tree.column('interval', width=150, anchor='center')
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Control buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, pady=(10, 0))
        
        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_pressing, style="Accent.TButton")
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_pressing)
        self.stop_button.grid(row=0, column=1)
        self.stop_button.config(state='disabled')
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Status: Stopped", foreground="red")
        self.status_label.grid(row=4, column=0, pady=(10, 0))
        
        # Hotkey info label
        self.hotkey_label = ttk.Label(main_frame, text="Hotkeys: F7 = Start | F8 = Stop", 
                                     font=("Arial", 9), foreground="gray")
        self.hotkey_label.grid(row=5, column=0, pady=(5, 0))
        
        # Bind double-click to toggle active state
        self.tree.bind('<Double-1>', self.toggle_active)
        
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
            self.current_language = language_code
            self.load_texts()
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
        
    def load_languages(self):
        """Load available languages from locales.json"""
        try:
            with open(self.locales_file, 'r', encoding='utf-8') as f:
                locales_data = json.load(f)
                self.available_languages = locales_data.get('languages', [])
        except FileNotFoundError:
            # Create default locales.json if it doesn't exist
            self.create_default_locales()
        except Exception as e:
            messagebox.showerror("Error", f"Error loading locales: {e}")
            self.available_languages = [{"code": "en", "name": "English", "file": "en.txt"}]
    
    def create_default_locales(self):
        """Create default locales.json file"""
        default_locales = {
            "languages": [
                {"code": "en", "name": "English", "file": "en.txt"},
                {"code": "pt", "name": "Português", "file": "pt.txt"},
                {"code": "sp", "name": "Español", "file": "sp.txt"}
            ]
        }
        try:
            with open(self.locales_file, 'w', encoding='utf-8') as f:
                json.dump(default_locales, f, indent=4, ensure_ascii=False)
            self.available_languages = default_locales['languages']
        except Exception as e:
            messagebox.showerror("Error", f"Error creating locales file: {e}")
    
    def load_texts(self):
        """Load texts for current language"""
        current_lang_file = None
        for lang in self.available_languages:
            if lang['code'] == self.current_language:
                current_lang_file = lang['file']
                break
        
        if not current_lang_file:
            current_lang_file = "en.txt"
        
        try:
            self.texts = {}  # Clear existing texts
            with open(current_lang_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and '=' in line:
                        key, value = line.split('=', 1)
                        self.texts[key.strip()] = value.strip()
        except FileNotFoundError:
            # Create default English texts if file doesn't exist
            self.create_default_language_files()
            self.load_texts()  # Retry loading
        except Exception as e:
            messagebox.showerror("Error", f"Error loading language file: {e}")
    
    def create_default_language_files(self):
        """Create default language files"""
        # English
        en_texts = {
            "app_title": "Auto Key Presser",
            "key_label": "Key:",
            "interval_label": "Interval (ms):",
            "add_button": "Add",
            "remove_button": "Remove",
            "start_button": "Start",
            "stop_button": "Stop",
            "status_stopped": "Status: Stopped",
            "status_running": "Status: Running",
            "hotkeys_info": "Hotkeys: F7 = Start | F8 = Stop",
            "language_button": "Language",
            "header_active": "Active",
            "header_key": "Key",
            "header_interval": "Interval (ms)",
            "error_title": "Error",
            "warning_title": "Warning",
            "error_enter_key": "Please enter a key",
            "error_valid_interval": "Please enter a valid positive interval in milliseconds",
            "error_key_exists": "Key '{key}' already exists",
            "warning_select_row": "Please select a row to remove",
            "warning_no_active": "No active key configurations found",
            "error_keyboard_lib": "'keyboard' library is required. Install it with: pip install keyboard"
        }
        
        # Portuguese
        pt_texts = {
            "app_title": "Pressionador Automático de Teclas",
            "key_label": "Tecla:",
            "interval_label": "Intervalo (ms):",
            "add_button": "Adicionar",
            "remove_button": "Remover",
            "start_button": "Iniciar",
            "stop_button": "Parar",
            "status_stopped": "Status: Parado",
            "status_running": "Status: Executando",
            "hotkeys_info": "Atalhos: F7 = Iniciar | F8 = Parar",
            "language_button": "Idioma",
            "header_active": "Ativo",
            "header_key": "Tecla",
            "header_interval": "Intervalo (ms)",
            "error_title": "Erro",
            "warning_title": "Aviso",
            "error_enter_key": "Por favor, digite uma tecla",
            "error_valid_interval": "Por favor, digite um intervalo positivo válido em milissegundos",
            "error_key_exists": "Tecla '{key}' já existe",
            "warning_select_row": "Por favor, selecione uma linha para remover",
            "warning_no_active": "Nenhuma configuração de tecla ativa encontrada",
            "error_keyboard_lib": "Biblioteca 'keyboard' é necessária. Instale com: pip install keyboard"
        }
        
        # Spanish
        sp_texts = {
            "app_title": "Presionador Automático de Teclas",
            "key_label": "Tecla:",
            "interval_label": "Intervalo (ms):",
            "add_button": "Agregar",
            "remove_button": "Eliminar",
            "start_button": "Iniciar",
            "stop_button": "Detener",
            "status_stopped": "Estado: Detenido",
            "status_running": "Estado: Ejecutando",
            "hotkeys_info": "Atajos: F7 = Iniciar | F8 = Detener",
            "language_button": "Idioma",
            "header_active": "Activo",
            "header_key": "Tecla",
            "header_interval": "Intervalo (ms)",
            "error_title": "Error",
            "warning_title": "Advertencia",
            "error_enter_key": "Por favor, ingrese una tecla",
            "error_valid_interval": "Por favor, ingrese un intervalo positivo válido en milisegundos",
            "error_key_exists": "La tecla '{key}' ya existe",
            "warning_select_row": "Por favor, seleccione una fila para eliminar",
            "warning_no_active": "No se encontraron configuraciones de teclas activas",
            "error_keyboard_lib": "Se requiere la biblioteca 'keyboard'. Instálela con: pip install keyboard"
        }
        
        # Create files
        try:
            self.write_language_file("en.txt", en_texts)
            self.write_language_file("pt.txt", pt_texts)
            self.write_language_file("sp.txt", sp_texts)
        except Exception as e:
            messagebox.showerror("Error", f"Error creating language files: {e}")
    
    def write_language_file(self, filename, texts):
        """Write language texts to file"""
        with open(filename, 'w', encoding='utf-8') as f:
            for key, value in texts.items():
                f.write(f"{key}={value}\n")
    
    def load_config(self):
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.key_configs = config.get('key_configs', [])
                self.current_language = config.get('language', 'en')
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
    
    def get_text(self, key, **kwargs):
        """Get localized text with optional formatting"""
        text = self.texts.get(key, key)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except:
                pass
        return text
            
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
        selection = self.tree.selection()
        if not selection:
            return
            
        item = selection[0]
        index = self.tree.index(item)
        
        if 0 <= index < len(self.key_configs):
            self.key_configs[index]['active'] = not self.key_configs[index]['active']
            self.update_tree()
            self.save_config()  # Save after toggling
            
    def update_tree(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Add current configurations
        for config in self.key_configs:
            active_text = "✓" if config['active'] else "✗"
            self.tree.insert('', 'end', values=(config['key'], config['interval']), 
                           text=active_text)
                           
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
                key_to_press = self.key_queue.get(timeout=0.1)
                
                # Press the key
                keyboard.press_and_release(key_to_press)
                
                # Minimum delay of 100ms between key presses
                time.sleep(0.1)  # 100ms delay
                
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
                # Add key to queue instead of pressing directly
                self.key_queue.put(key)
            except Exception as e:
                # Log errors silently
                pass
                
            time.sleep(interval / 2000.0)  # Convert ms to seconds
            
    def start_pressing(self):
        if self.is_running:
            return
            
        active_configs = [config for config in self.key_configs if config['active']]
        
        if not active_configs:
            messagebox.showwarning(self.get_text("warning_title"), self.get_text("warning_no_active"))
            return
            
        self.is_running = True
        self.timers = {}
        
        # Start the key press manager thread
        self.key_press_thread = threading.Thread(target=self.key_press_manager)
        self.key_press_thread.daemon = True
        self.key_press_thread.start()
        
        # Start a thread for each active key configuration
        for config in active_configs:
            key = config['key']
            interval = config['interval']
            timer_id = f"{key}_{interval}"
            
            thread = threading.Thread(target=self.key_press_worker, args=(key, interval))
            thread.daemon = True
            self.timers[timer_id] = thread
            thread.start()
            
        # Update UI
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.status_label.config(text=self.get_text("status_running"), foreground="green")
        
    def stop_pressing(self):
        if not self.is_running:
            return
            
        self.is_running = False
        self.timers = {}
        
        # Clear any remaining keys in the queue
        while not self.key_queue.empty():
            try:
                self.key_queue.get_nowait()
            except queue.Empty:
                break
        
        # Update UI
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
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
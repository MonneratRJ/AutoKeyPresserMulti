import json
import os
from tkinter import messagebox

class I18nManager:
    def __init__(self, locales_file="locales.json", default_language="en"):
        self.locales_file = locales_file
        self.current_language = default_language
        self.texts = {}
        self.available_languages = []
        self.load_languages()
        self.load_texts()

    def load_languages(self):
        try:
            with open(self.locales_file, 'r', encoding='utf-8') as f:
                locales_data = json.load(f)
                self.available_languages = locales_data.get('languages', [])
        except FileNotFoundError:
            self.create_default_locales()
        except Exception as e:
            messagebox.showerror("Error", f"Error loading locales: {e}")
            self.available_languages = [{"code": "en", "name": "English", "file": "en.txt"}]

    def create_default_locales(self):
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
        current_lang_file = None
        for lang in self.available_languages:
            if lang['code'] == self.current_language:
                current_lang_file = lang['file']
                break
        if not current_lang_file:
            current_lang_file = "en.txt"
        try:
            self.texts = {}
            with open(current_lang_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and '=' in line:
                        key, value = line.split('=', 1)
                        self.texts[key.strip()] = value.strip()
        except FileNotFoundError:
            self.create_default_language_files()
            self.load_texts()
        except Exception as e:
            messagebox.showerror("Error", f"Error loading language file: {e}")

    def create_default_language_files(self):
        en_texts = {
            "app_title": "Auto Key Presser by MoneyRat",
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
        pt_texts = {
            "app_title": "Pressionador Automático de Teclas por MoneyRat",
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
        sp_texts = {
            "app_title": "Presionador Automático de Teclas por MoneyRat",
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
            "error_valid_interval": "Por favor, ingrese un intervalo positivo válido en milissegundos",
            "error_key_exists": "La tecla '{key}' ya existe",
            "warning_select_row": "Por favor, seleccione una fila para eliminar",
            "warning_no_active": "No se encontraron configuraciones de teclas activas",
            "error_keyboard_lib": "Se requiere la biblioteca 'keyboard'. Instálela con: pip install keyboard"
        }
        try:
            self.write_language_file("en.txt", en_texts)
            self.write_language_file("pt.txt", pt_texts)
            self.write_language_file("sp.txt", sp_texts)
        except Exception as e:
            messagebox.showerror("Error", f"Error creating language files: {e}")

    def write_language_file(self, filename, texts):
        with open(filename, 'w', encoding='utf-8') as f:
            for key, value in texts.items():
                f.write(f"{key}={value}\n")

    def get_text(self, key, **kwargs):
        text = self.texts.get(key, key)
        if kwargs:
            try:
                text = text.format(**kwargs)
            except:
                pass
        return text

    def change_language(self, language_code):
        if language_code != self.current_language:
            self.current_language = language_code
            self.load_texts()

    def get_available_languages(self):
        return self.available_languages

    def get_current_language(self):
        return self.current_language

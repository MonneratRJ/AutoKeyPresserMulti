class I18nManager:
    def __init__(self):
        self.texts = {            "en": {
                "app_title": "MoneyRat's AutoKeyPresser",
                "start": "Start",
                "stop": "Stop",
                "add": "Add",
                "remove": "Remove",
                "language": "Language",
                "error": "An error occurred",
                "success": "Operation successful",
                "active": "Active",
                "key": "Key",
                "interval": "Interval (ms)",
                "actions": "Actions"
            },            "es": {
                "app_title": "MoneyRat's AutoPresionador de Teclas",
                "start": "Iniciar",
                "stop": "Detener",
                "add": "Agregar",
                "remove": "Eliminar",
                "language": "Idioma",
                "error": "Ocurrió un error",
                "success": "Operación exitosa",
                "active": "Activo",
                "key": "Tecla",
                "interval": "Intervalo (ms)",
                "actions": "Acciones"
            },            "pt": {
                "app_title": "MoneyRat's AutoPressionador de Teclas",
                "start": "Iniciar",
                "stop": "Parar",
                "add": "Adicionar",
                "remove": "Remover",
                "language": "Idioma",
                "error": "Ocorreu um erro",
                "success": "Operação bem-sucedida",
                "active": "Ativo",
                "key": "Tecla",
                "interval": "Intervalo (ms)",
                "actions": "Ações"
            },            "zh": {
                "app_title": "MoneyRat's 自动按键助手",
                "start": "开始",
                "stop": "停止",
                "add": "添加",
                "remove": "移除",
                "language": "语言",
                "error": "发生错误",
                "success": "操作成功",
                "active": "激活",
                "key": "按键",
                "interval": "间隔 (毫秒)",
                "actions": "操作"
            },            "fr": {
                "app_title": "MoneyRat's AutoPresseur de Touches",
                "start": "Démarrer",
                "stop": "Arrêter",
                "add": "Ajouter",
                "remove": "Supprimer",
                "language": "Langue",
                "error": "Une erreur s'est produite",
                "success": "Opération réussie",
                "active": "Actif",
                "key": "Touche",
                "interval": "Intervalle (ms)",
                "actions": "Actions"
            },            "de": {
                "app_title": "MoneyRat's AutoTastenpresser",
                "start": "Starten",
                "stop": "Stoppen",
                "add": "Hinzufügen",
                "remove": "Entfernen",
                "language": "Sprache",
                "error": "Ein Fehler ist aufgetreten",
                "success": "Operation erfolgreich",
                "active": "Aktiv",
                "key": "Taste",
                "interval": "Intervall (ms)",
                "actions": "Aktionen"
            }
        }
        self.current_language = "en"

    def get_text(self, key, **kwargs):
        try:
            text = self.texts[self.current_language][key]
            if kwargs:
                text = text.format(**kwargs)
            return text
        except KeyError:
            return self.texts["en"].get(key, key)

    def set_language(self, language_code):
        if language_code in self.texts:
            self.current_language = language_code
            return True
        return False

    def get_available_languages(self):
        return list(self.texts.keys())

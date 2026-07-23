import json
import os
from datetime import datetime

# Ruta al archivo de configuración
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app_config.json")

class AppConfig:
    def __init__(self):
        # Valores por defecto (Fallback)
        self.APP_NAME = "Happy Vision"
        self.OWNER_NAME = "Propietario de la Óptica"
        self.OWNER_RUC = "0000000000001"
        self.SUPPORT_PHONE = "+593 00 000 0000"
        self.SUPPORT_EMAIL = "soporte@happyvision.com"
        self.PRIMARY_COLOR = "#2563eb"
        self.SECONDARY_COLOR = "#0f172a"
        self.LOGIN_BG_PATH = "login_bg.png"
        self.MAIN_BG_PATH = "main_bg.png"
        self.THEME_PRESET = "Cristal Elegante"
        self.LOGO_PATH = "logo.png"
        self.FOOTER_TEXT = "© 2024 Happy Vision Integral System"
        self.LICENSED_UUID = ""
        self.SETUP_COMPLETED = True
        self.STORAGE_MODE = "SUPABASE"
        self.SUPABASE_URL = "https://oqsdnoknuzkexknpakyd.supabase.co"
        self.SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9xc2Rub2tudXprZXhrbnBha3lkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQ4MTQyMDcsImV4cCI6MjEwMDM5MDIwN30.5LQBs5FQuttXbaRoDuwUqSwwSY-5aiNqvbm9D5-OrMI"

        self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.APP_NAME = data.get("APP_NAME", self.APP_NAME)
                    self.OWNER_NAME = data.get("OWNER_NAME", self.OWNER_NAME)
                    self.OWNER_RUC = data.get("OWNER_RUC", self.OWNER_RUC)
                    self.SUPPORT_PHONE = data.get("SUPPORT_PHONE", self.SUPPORT_PHONE)
                    self.SUPPORT_EMAIL = data.get("SUPPORT_EMAIL", self.SUPPORT_EMAIL)
                    self.PRIMARY_COLOR = data.get("PRIMARY_COLOR", self.PRIMARY_COLOR)
                    self.SECONDARY_COLOR = data.get("SECONDARY_COLOR", self.SECONDARY_COLOR)
                    self.LOGIN_BG_PATH = data.get("LOGIN_BG_PATH", self.LOGIN_BG_PATH)
                    self.MAIN_BG_PATH = data.get("MAIN_BG_PATH", self.MAIN_BG_PATH)
                    self.THEME_PRESET = data.get("THEME_PRESET", self.THEME_PRESET)
                    self.LOGO_PATH = data.get("LOGO_PATH", self.LOGO_PATH)
                    self.LICENSED_UUID = data.get("LICENSED_UUID", "")
                    self.FOOTER_TEXT = data.get("FOOTER_TEXT", f"© {datetime.now().year} {self.APP_NAME}")
                    self.SETUP_COMPLETED = data.get("SETUP_COMPLETED", True)
                    self.STORAGE_MODE = data.get("STORAGE_MODE", "SUPABASE")
                    self.SUPABASE_URL = data.get("SUPABASE_URL", self.SUPABASE_URL)
                    self.SUPABASE_KEY = data.get("SUPABASE_KEY", self.SUPABASE_KEY)
            except Exception as e:
                print(f"Error loading config: {e}")

    def save_config(self):
        """Persiste la configuración actual al archivo JSON."""
        data = {
            "APP_NAME": self.APP_NAME,
            "OWNER_NAME": self.OWNER_NAME,
            "OWNER_RUC": self.OWNER_RUC,
            "SUPPORT_PHONE": self.SUPPORT_PHONE,
            "SUPPORT_EMAIL": self.SUPPORT_EMAIL,
            "PRIMARY_COLOR": self.PRIMARY_COLOR,
            "SECONDARY_COLOR": self.SECONDARY_COLOR,
            "LOGIN_BG_PATH": self.LOGIN_BG_PATH,
            "MAIN_BG_PATH": self.MAIN_BG_PATH,
            "THEME_PRESET": self.THEME_PRESET,
            "LOGO_PATH": self.LOGO_PATH,
            "LICENSED_UUID": self.LICENSED_UUID,
            "FOOTER_TEXT": self.FOOTER_TEXT,
            "SETUP_COMPLETED": self.SETUP_COMPLETED,
            "STORAGE_MODE": self.STORAGE_MODE,
            "SUPABASE_URL": self.SUPABASE_URL,
            "SUPABASE_KEY": self.SUPABASE_KEY
        }
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error guardando config: {e}")

# Instancia única para importar en toda la app
config = AppConfig()

# paths/base_paths.py

import sys
import json
from pathlib import Path
import os

if getattr(sys, 'frozen', False):  # Executável compilado
    BASE_DIR = Path(sys._MEIPASS) / "src"  # Diretório temporário + 'src'
else:  # Ambiente de desenvolvimento
    BASE_DIR = Path(__file__).resolve().parent.parent
  
DEFAULT_DATABASE_DIR = BASE_DIR / "database"
DEFAULT_JSON_DIR = DEFAULT_DATABASE_DIR / "json"
DEFAULT_SQL_DIR = DEFAULT_DATABASE_DIR / "sql"
ASSETS_DIR = BASE_DIR / "assets"
DEFAULT_TEMPLATE_DIR = ASSETS_DIR / "templates"

CONFIG_FILE = BASE_DIR / "config.json"

MODULES_DIR = BASE_DIR / "modules"

def get_config_value(key, default_value):
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get(key, default_value)
    except (FileNotFoundError, json.JSONDecodeError):
        return default_value

# Definição dos diretórios com base no caminho do usuário
DATABASE_DIR = Path(get_config_value("DATABASE_DIR", str(DEFAULT_DATABASE_DIR)))
JSON_DIR = Path(get_config_value("JSON_DIR", str(DEFAULT_JSON_DIR)))
TEMPLATE_DIR = Path(get_config_value("TEMPLATE_DIR", str(DEFAULT_TEMPLATE_DIR)))
SQL_DIR = Path(get_config_value("SQL_DIR", str(DEFAULT_SQL_DIR)))


# Assets
TEMPLATE_DIR = ASSETS_DIR / "templates"
ICONS_DIR = ASSETS_DIR / "icons"
ICONS_MENU_DIR = ICONS_DIR / "menu"

def load_global_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print("Erro ao carregar configuração:", e)
    return {}

global_config = load_global_config()
custom_base_path = global_config.get("BASE_PATH")
USER_BASE_PATH = Path(custom_base_path) if custom_base_path else BASE_DIR

def reload_paths():
    """Recarrega os diretórios a partir do arquivo de configuração e atualiza as variáveis globais."""
    global DATABASE_DIR, JSON_DIR, TEMPLATE_DIR, CONFIG_FILE
    DATABASE_DIR = Path(get_config_value("DATABASE_DIR", str(DEFAULT_DATABASE_DIR)))
    JSON_DIR = Path(get_config_value("JSON_DIR", str(DEFAULT_JSON_DIR)))
    TEMPLATE_DIR = Path(get_config_value("TEMPLATE_DIR", str(DEFAULT_TEMPLATE_DIR)))

    # print("reload_paths() => DATABASE_DIR:", DATABASE_DIR)
    # print("reload_paths() => JSON_DIR:", JSON_DIR)
    # print("reload_paths() => TEMPLATE_DIR:", TEMPLATE_DIR)

# Garante que os diretórios existam
os.makedirs(JSON_DIR, exist_ok=True)

def save_config(key, value):
    config = {}
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    config[key] = value
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f)

def update_base_paths(new_base_path):
    global USER_BASE_PATH, DATABASE_DIR, JSON_DIR, CONFIG_FILE
    USER_BASE_PATH = Path(new_base_path)
    DATABASE_DIR = USER_BASE_PATH / "database"
    JSON_DIR = DATABASE_DIR / "json"
    CONFIG_FILE = JSON_DIR / "config.json"
    os.makedirs(JSON_DIR, exist_ok=True)
    # Atualiza a configuração persistente
    save_config("BASE_PATH", new_base_path)


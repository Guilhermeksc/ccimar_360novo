# paths/base_paths.py

import sys
import json
from pathlib import Path
import os

if getattr(sys, 'frozen', False):  # Executável compilado
    BASE_DIR = Path(sys._MEIPASS) / "src"  # Diretório temporário + 'src'
else:  # Ambiente de desenvolvimento
    BASE_DIR = Path(__file__).resolve().parent.parent
  
DATABASE_DIR = BASE_DIR / "database"    
MODULES_DIR = BASE_DIR / "modules"

JSON_DIR = DATABASE_DIR / "json"
JSON_COMPRASNET_CONTRATOS = JSON_DIR / "consulta_comprasnet"
CONFIG_FILE = JSON_DIR / "config.json"
CONFIG_API_KEY_FILE = JSON_DIR / "config_api_key.json"  

def load_config():
    try:
        with open(CONFIG_API_KEY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Erro ao carregar o arquivo de configuração: {e}")
        return {}

# Carregar configurações
CONFIG = load_config()

# Obter API_KEY do JSON ou variável de ambiente
API_KEY = CONFIG.get("API_KEY") or os.getenv("OPENAI_API_KEY")

SQL_DIR = DATABASE_DIR / "sql"
CONTROLE_DADOS = SQL_DIR / "controle_dados.db"

# Assets
ASSETS_DIR = BASE_DIR / "assets"
TEMPLATE_DIR = ASSETS_DIR / "templates"
STYLE_PATH = ASSETS_DIR / "style.css" 
ICONS_DIR = ASSETS_DIR / "icons"
IMAGE_DIR = ASSETS_DIR / "image"
CCIMAR360_PATH = IMAGE_DIR / "CCIMAR-360.png"
ICONS_MENU_DIR = ICONS_DIR / "menu"



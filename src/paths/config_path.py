from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from .base_path import JSON_DIR, DATABASE_DIR, CONFIG_FILE
from pathlib import Path
import json

def load_config_path_id():
    if not Path(CONFIG_FILE).exists():
        return {}
    with open(CONFIG_FILE, 'r') as file:
        return json.load(file)

def load_config(key, default_value):
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return config.get(key, default_value)
    except (FileNotFoundError, json.JSONDecodeError):
        return default_value

def save_config(key, value):
    config = {}
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    config[key] = value
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def update_dir(title, key, default_value, parent=None):
    new_dir = QFileDialog.getExistingDirectory(parent, title)
    if new_dir:
        save_config(key, new_dir)
        return Path(new_dir)
    return default_value

PRE_DEFINICOES_JSON = JSON_DIR / "pre_definicioes.json"
AGENTES_RESPONSAVEIS_FILE = JSON_DIR / "agentes_responsaveis.json"
ORGANIZACOES_FILE = JSON_DIR / "organizacoes.json"

PDF_DIR = Path(load_config("PDF_DIR", DATABASE_DIR / "pdf"))

class ConfigManager(QObject):
    config_updated = pyqtSignal(str, Path)  # sinal emitido quando uma configuração é atualizada

    def __init__(self, config_file):
        super().__init__()
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_config(self, key, value):
        self.config[key] = value
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)
        self.config_updated.emit(key, Path(value))
        
    def update_config(self, key, value):
        # Aqui garantimos que ambos os parâmetros sejam passados corretamente para save_config
        self.save_config(key, value)
        self.config_updated.emit(key, Path(value))

    def get_config(self, key, default_value):
        return self.config.get(key, default_value)
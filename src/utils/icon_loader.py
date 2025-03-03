# config/icon_loader.py
from pathlib import Path
from PyQt6.QtGui import QIcon
from paths import ICONS_DIR, ICONS_MENU_DIR
import logging

# Configuração de logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Cache para ícones
_icon_cache = {}

def load_icon(icon_name):
    """Carrega e armazena em cache os ícones como QIcon. Verifica se o arquivo existe antes de carregar."""
    if icon_name not in _icon_cache:
        # Primeiro, tenta carregar de ICONS_DIR
        icon_path = ICONS_DIR / icon_name
        if not icon_path.exists():
            # Se não encontrar, tenta em ICONS_MENU_DIR
            icon_path = ICONS_MENU_DIR / icon_name

        if icon_path.exists():
            _icon_cache[icon_name] = QIcon(str(icon_path))
        else:
            logger.warning(f"Ícone '{icon_name}' não encontrado em {ICONS_DIR} nem em {ICONS_MENU_DIR}")
            _icon_cache[icon_name] = QIcon()  # Retorna um ícone vazio em caso de falha

    return _icon_cache[icon_name]

# Funções específicas para carregar ícones usados frequentemente #8AB4F7 #FFFFFF
def load_icons():
    return {
        "number-10": load_icon("number-10.png"),
        "number-10-b": load_icon("number-10-b.png"),
        "number-11": load_icon("number-11.png"),
        "number-11-b": load_icon("number-11-b.png"),
        "number-12": load_icon("number-12.png"),
        "number-12-b": load_icon("number-12-b.png"),
        "number-13": load_icon("number-13.png"),
        "number-13-b": load_icon("number-13-b.png"),
        "number-14": load_icon("number-14.png"),
        "number-14-b": load_icon("number-14-b.png"),
        "number-15": load_icon("number-15.png"),
        "number-15-b": load_icon("number-15-b.png"),
        "number-16": load_icon("number-16.png"),
        "number-16-b": load_icon("number-16-b.png"),
        
        "initdataprocessing": load_icon("initdataprocessing.png"),    
        "initdatacollection": load_icon("initdatacollection.png"),    
        "initexploration": load_icon("initexploration.png"),    
        "data-collection": load_icon("data-collection.png"),
        "data-collection_blue": load_icon("data-collection_blue.png"),        
        "data-processing": load_icon("data-processing.png"),
        "data-processing_blue": load_icon("data-processing_blue.png"),        
        "initreport": load_icon("initreport.png"),   
        "click": load_icon("click.png"),   
        "analytics": load_icon("analytics.png"),   
        "report": load_icon("report.png"),   
        "criteria": load_icon("criteria.png"),   

        "doc": load_icon("doc.png"),
        "chat": load_icon("chat.png"),
        "mail": load_icon("mail.png"),
        "prioridade": load_icon("prioridade.png"),
        "api_azul": load_icon("API_azul.png"),    
        "statistics_azul": load_icon("statistics_azul.png"),
        "statistics": load_icon("statistics.png"),
        "pdf": load_icon("pdf.png"),
        "word": load_icon("word.png"),
        "timeline": load_icon("timeline.png"),
        "process": load_icon("process.png"),
        "delete": load_icon("delete.png"),

        # "pdf_button": load_icon("pdf_button.png"),
        # "pdf_button_blue": load_icon("pdf_button_blue.png"),
        # "planning": load_icon("planning.png"),
        # "info": load_icon("info.png"),
        "360-degrees": load_icon("360-degrees.png"),
        "data-science": load_icon("data-science.png"),

        "brasil": load_icon("brasil.png"),
        "mensagem": load_icon("mensagem.png"),
        "excel": load_icon("excel.png"),

        "api": load_icon("api.png"),
        "meeting": load_icon("meeting.png"),
        "auditor": load_icon("auditor.png"),
        "link": load_icon("link.png"),
        "dashboard": load_icon("dashboard.png"),
        # "api_button": load_icon("api_button.png"),
        "menu": load_icon("menu.png"),
        "menu-open": load_icon("menu-open.png"),
        "sign": load_icon("sign.png"),
        "init": load_icon("init.png"),
        "init_hover": load_icon("init_hover.png"),
        "contrato": load_icon("contrato.png"),
        "contrato_blue": load_icon("contrato_blue.png"),
        # "plan": load_icon("plan.png"),
        # "plan_hover": load_icon("plan_hover.png"),
        "contract": load_icon("contract.png"),
        "contract_hover": load_icon("contract_hover.png"),
        "config": load_icon("config.png"),
        "config_hover": load_icon("config_hover.png"),
        # "confirm": load_icon("confirm.png"),
        "magnifying-glass": load_icon("magnifying-glass.png"),
        "analysis": load_icon("analysis.png"),
        "data_blue": load_icon("data_blue.png"),
        "data": load_icon("data.png"),
}
# src/modules/ccimar12_planejamento/menu/menu_callbacks.py

from PyQt6.QtWidgets import QLabel, QFrame, QVBoxLayout, QMessageBox
from .content.modulo_contratos import create_vigencia_contratos
from .content.modulo_atas import create_atas
from .content.modulo_trilha_auditoria import create_trilha_auditoria
from .content.modulo_webscraping import create_webscrapping
from .content.modulo_rpa import create_rpa_layout
from .content.modulo_api.api_Model import APIModel
from .content.modulo_api.api_View import APIView
from .content.modulo_api.api_Controller import APIController
from paths import SQL_DIR

API_PATH = SQL_DIR / "api_pncp_comprasnet.db"

def show_teste_widget(view, icons):
    view.clear_content()
    view.content_layout.addWidget(create_vigencia_contratos("Contratos teste", icons))
    
def show_vigencia_contratos(view, icons):
    view.clear_content()
    view.content_layout.addWidget(create_vigencia_contratos("Contratos teste", icons))

def show_trilha_auditoria(view, icons):
    view.clear_content()
    view.content_layout.addWidget(create_trilha_auditoria("Trilha de Auditoria", icons))
    
def show_webscraping(view, icons):
    view.clear_content()
    view.content_layout.addWidget(create_webscrapping("WebScraping", icons))
    
def show_atas(view, icons):
    view.clear_content()
    view.content_layout.addWidget(create_atas("Atas", icons))
    
def show_limites_governanca(view, icons):
    view.clear_content()
    view.content_layout.addWidget(create_vigencia_contratos("Limites de Governança", icons))
    
def show_rpa(view, icons):
    view.clear_content()
    view.content_layout.addWidget(create_rpa_layout("Robotic Process Automation (RPA)", icons))
        
def show_api(view, icons):
    try:
        view.clear_content()
        view.api_model = APIModel(API_PATH)
        title_text = "Aplication Programming Interface (API)"
        
        # 🔹 Configura o modelo SQL corretamente
        sql_model = view.api_model.setup_model("tabela_api_pncp_comprasnet", editable=True)

        # 🔹 Cria a view do API PNCP
        view.api_view = APIView(
            icons, 
            sql_model,
            title_text, 
            view.api_model.database_manager.db_path
        )

        # 🔹 Cria o controlador e armazena na view principal
        view.api_controller = APIController(icons, view.api_view, view.api_model)

        # 🔹 Adiciona a view ao layout da janela principal
        view.content_layout.addWidget(view.api_view)

    except Exception as e:
        QMessageBox.warning(view, "Erro", f"Falha ao carregar API PNCP: {e}")
        print(f"Erro ao carregar API PNCP: {e}")
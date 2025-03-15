# src/config/menu/menu_callbacks.py

from .content.agentes_responsaveis import create_agentes_responsaveis
from .content.local_salvamento import create_local_salvamento

def show_agentes_responsaveis(view, icons):
    view.clear_content()
    view.content_layout.addWidget(create_agentes_responsaveis("Contratos teste", icons))
    
def show_local_salvamento(view, icons):
    view.clear_content()
    view.content_layout.addWidget(create_local_salvamento("Contratos teste", icons))

# src/config/menu/menu_callbacks.py

from .content.modulo_agentes_responsaveis import create_agentes_responsaveis
from .content.modulo_local_salvamento import create_local_salvamento

def show_agentes_responsaveis(view, icons):
    view.clear_content()
    view.content_layout.addWidget(create_agentes_responsaveis("Agentes Responsáveis", icons))
    
def show_local_salvamento(view, icons):
    view.clear_content()
    view.content_layout.addWidget(create_local_salvamento("Local de Salvamento", icons))

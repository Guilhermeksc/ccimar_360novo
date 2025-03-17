# src/modules/ccimar12_planejamento/menu/menu_callbacks.py

from .content.modulo_contratos import create_vigencia_contratos

def show_teste(view, icons):
    view.clear_content()
    view.content_layout.addWidget(create_vigencia_contratos("Contratos teste", icons))
    

# src/modules/ccimar12_planejamento/menu/menu_callbacks.py

from PyQt6.QtWidgets import QLabel, QFrame, QVBoxLayout
from .content.modulo_contratos import create_vigencia_contratos
from .content.modulo_atas import create_atas
from .content.modulo_trilha_auditoria import create_trilha_auditoria
from .content.modulo_webscraping import create_webscrapping
from .content.modulo_excel import create_excel_layout

def show_excel_layout(view, icons):
    view.clear_content()
    view.content_layout.addWidget(create_excel_layout("Excel Teste", icons))
    
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
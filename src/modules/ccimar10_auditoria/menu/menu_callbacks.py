# src/modules/ccimar11_planejamento/menu/menu_callbacks.py

from PyQt6.QtWidgets import QLabel, QFrame, QVBoxLayout

def create_content(title_text):
    """Creates a content layout inside a styled QFrame."""
    content_frame = QFrame()

    layout = QVBoxLayout(content_frame)
    layout.setContentsMargins(0, 0, 0, 0) 
    layout.setSpacing(0)  # Keep spacing flexible

    title = QLabel(title_text)
    title.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF")  
    layout.addWidget(title)

    return content_frame

def show_criterio1_execucao_licitacao(view):
    view.clear_content()
    view.content_layout.addWidget(create_content("Conselho de Gestão"))

def show_criterio2_pagamento(view):
    view.clear_content()
    view.content_layout.addWidget(create_content("Conselho de Gestão"))
    
def show_criterio3_munic(view):
    view.clear_content()
    view.content_layout.addWidget(create_content("Conselho de Gestão"))

def show_criterio4_patrimonio(view):
    view.clear_content()
    view.content_layout.addWidget(create_content("Conselho de Gestão"))

def show_criterio5_anos_sem_audit(view):
    view.clear_content()
    view.content_layout.addWidget(create_content("Conselho de Gestão"))

def show_criterio6_foco_externo(view):
    view.clear_content()
    view.content_layout.addWidget(create_content("Conselho de Gestão"))

def show_criteriox_omps(view):
    view.clear_content()
    view.content_layout.addWidget(create_content("Conselho de Gestão"))

def show_conselho_de_gestao(view, icons):
    view.clear_content()
    view.content_layout.addWidget(create_content("Conselho de Gestão"))

def show_gerar_notas_widget(view):
    view.clear_content()
    view.content_layout.addWidget(create_content("Gerar Notas"))

def show_relatorio_consultas_airflow_widget(view):
    view.clear_content()
    view.content_layout.addWidget(create_content("Consultas do Airflow"))

def show_relatorio_sgm_widget(view):
    view.clear_content()
    view.content_layout.addWidget(create_content("Relatório SGM"))

def show_relatorio_ccimar11_widget(view):
    view.clear_content()
    view.content_layout.addWidget(create_content("Relatório CCIMAR-11"))

def show_relatorio_cofamar_widget(view):
    view.clear_content()
    view.content_layout.addWidget(create_content("Relatório COFAMAR"))

def show_relatorio_calculo_total_widget(view):
    view.clear_content()
    view.content_layout.addWidget(create_content("Gerar Nota com Cálculo Total"))

def show_relatorio_notas_monitoradas_widget(view):
    view.clear_content()
    view.content_layout.addWidget(create_content("Notas Monitoradas"))

def show_relatorio_audcont_widget(view):
    view.clear_content()
    view.content_layout.addWidget(create_content("AUDCONT - Notas Vencidas"))

def show_oficio_apresentacao_widget(view):
    view.clear_content()
    view.content_layout.addWidget(create_content("Ofício de Apresentação"))

def show_teste_widget(view):
    view.clear_content()
    view.content_layout.addWidget(create_content("Teste"))

def show_chat_bot(view, icons):
    view.clear_content()
    # Se necessário, passe os ícones para create_chatbot ou armazene-os em view
    view.content_layout.addWidget(create_content("Conselho de Gestão"))

def show_chat_bot_local(view, icons):
    view.clear_content()
    # Se necessário, passe os ícones para create_chatbot ou armazene-os em view
    view.content_layout.addWidget(create_content("Conselho de Gestão"))


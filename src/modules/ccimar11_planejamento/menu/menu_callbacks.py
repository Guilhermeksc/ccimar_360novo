# src/modules/ccimar11_planejamento/menu/menu_callbacks.py

from PyQt6.QtWidgets import QLabel, QFrame, QVBoxLayout
from .content.criterio1_execucao_licitacao import create_criterio1_execucao_licitacao
from .content.criterio2_pagamento import create_criterio2_pagamento
from .content.criterio3_municiamento import create_criterio3_municiamento
from .content.criterio4_patrimonio import create_criterio4_patrimonio
from .content.criterio5_periodo_sem_auditoria import create_criterio5_anos_sem_audit
from .content.criterio6_em_foco_externo import create_criterio6_foco_externo
from .content.criteriox_omps import create_x
from .content.chatbot import create_chatbot
from .content.criterios_pesos import create_criterios_pesos
from .content.cadastro_objetos_auditaveis import create_cadastro_objetos_auditaveis
from .content.objetivos_navais import create_objetivos_navais
from .content.objetos_auditaveis import create_objetos_auditaveis
from .content.om_representativas import create_om_representativas
from paths import OBJETIVOS_NAVAIS_PATH

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

def show_criterios_pesos(view):
    view.clear_content()
    view.content_layout.addWidget(create_criterios_pesos("Planejamento", view.database_model))

def show_objetivos_navais(view, icons):
    view.clear_content()
    view.content_layout.addWidget(create_objetivos_navais("PEM 2040", icons, json_file_path=OBJETIVOS_NAVAIS_PATH))

def show_objetos_auditaveis(view, icons):
    view.clear_content()
    view.content_layout.addWidget(create_objetos_auditaveis("Anexo A - Obj.Auditáveis", icons))

def show_cadastro_objetivos_navais(view, icons):
    view.clear_content()
    view.content_layout.addWidget(create_cadastro_objetos_auditaveis("Anexo A - Obj.Auditáveis", icons))

def show_om_representativas(view, icons):
    view.clear_content()
    view.content_layout.addWidget(create_om_representativas("Anexo B - OM Represent.", icons))

def show_criterio1_execucao_licitacao(view):
    view.clear_content()
    view.content_layout.addWidget(create_criterio1_execucao_licitacao("Critério 1 - Execução Financeira", view.database_model))

def show_criterio2_pagamento(view):
    view.clear_content()
    view.content_layout.addWidget(create_criterio2_pagamento("Critério 2 - Pagamento", view.database_model))
    
def show_criterio3_munic(view):
    view.clear_content()
    view.content_layout.addWidget(create_criterio3_municiamento("Critério 3 - Municiamento", view.database_model))

def show_criterio4_patrimonio(view):
    view.clear_content()
    view.content_layout.addWidget(create_criterio4_patrimonio("Critério 4 - Patrimônio", view.database_model))

def show_criterio5_anos_sem_audit(view):
    view.clear_content()
    view.content_layout.addWidget(create_criterio5_anos_sem_audit("Critério 5 - Anos sem Auditoria", view.database_model))

def show_criterio6_foco_externo(view):
    view.clear_content()
    view.content_layout.addWidget(create_criterio6_foco_externo("Critério 6 - Em Foco Externo", view.database_model))

def show_criteriox_omps(view): 
    view.clear_content()
    view.content_layout.addWidget(create_x("Organizações", view.database_model))

def show_oficio_ccimar20_widget(view, icons):
    view.clear_content()
    view.content_layout.addWidget(create_content("Ofício do CCIMAR-20"))

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
    view.content_layout.addWidget(create_chatbot("CCIMAR360 CHAT", view.database_model, icons))


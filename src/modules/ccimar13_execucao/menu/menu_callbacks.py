# src/modules/ccimar11_planejamento/menu/menu_callbacks.py

from PyQt6.QtWidgets import QLabel, QFrame, QVBoxLayout, QMessageBox
from .content.nota_auditoria_teste1 import create_content_nota_auditoria_test1
from .content.nota_auditoria_teste2 import create_content_nota_auditoria_test2
from .content.nota_auditoria_teste3 import create_content_nota_auditoria_test3
from .content.cartao_corporativo.cartaomodel import CartaoCorporativoModel
from .content.cartao_corporativo.cartaoview import CartaoCorporativoView
from .content.cartao_corporativo.cartaocontroller import CartaoCorporativoController
from paths import CARTAO_CORPORATIVO_PATH

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

def show_nota_auditoria_teste1(view):
    view.clear_content()
    view.content_layout.addWidget(create_content_nota_auditoria_test1("Nota de Auditoria Teste 1"))

def show_nota_auditoria_teste2(view):
    view.clear_content()
    view.content_layout.addWidget(create_content_nota_auditoria_test2("Nota de Auditoria Teste 2"))
    
def show_nota_auditoria_teste3(view):
    view.clear_content()
    view.content_layout.addWidget(create_content_nota_auditoria_test3("Nota de Auditoria Teste 3"))

def show_oficio_ccimar20_widget(view):
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

def show_cartao_corporativo(view, icons):
    """
    Cria e integra o MVC do Cartão Corporativo utilizando a estrutura correta.
    """
    try:
        view.clear_content()

        # 🔹 Cria o modelo do Cartão Corporativo
        view.cartao_corporativo_model = CartaoCorporativoModel(CARTAO_CORPORATIVO_PATH)
        
        # 🔹 Configura o modelo SQL corretamente
        sql_model = view.cartao_corporativo_model.setup_model("tabela_cartao_corporativo", editable=True)

        # 🔹 Cria a view do Cartão Corporativo
        view.cartao_corporativo_view = CartaoCorporativoView(
            icons, 
            sql_model, 
            view.cartao_corporativo_model.database_manager.db_path
        )

        # 🔹 Cria o controlador e armazena na view principal
        view.cartao_corporativo_controller = CartaoCorporativoController(icons, view.cartao_corporativo_view, view.cartao_corporativo_model)

        # 🔹 Adiciona a view ao layout da janela principal
        view.content_layout.addWidget(view.cartao_corporativo_view)

    except Exception as e:
        QMessageBox.warning(view, "Erro", f"Falha ao carregar Cartão Corporativo: {e}")
        print(f"Erro ao carregar Cartão Corporativo: {e}")




def show_oficio_apresentacao_widget(view):
    view.clear_content()
    view.content_layout.addWidget(create_content("Ofício de Apresentação"))

def show_teste_widget(view):
    view.clear_content()
    view.content_layout.addWidget(create_content("Teste"))

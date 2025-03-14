from PyQt6.QtWidgets import (
    QTabWidget, QWidget, QMessageBox, QVBoxLayout, QHBoxLayout, QPlainTextEdit,
    QComboBox, QLabel, QLineEdit, QFrame, QPushButton, QTreeView
)
from PyQt6.QtCore import Qt
from utils.styles.style_add_button import add_button_func
from utils.styles.styles_edit_button import apply_edit_dialog_style
from .trilha_2_01.create_tab import create_tab_2_01

def create_tab_2_12(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("2.12 Preço Homologado acima do Estimado"))
    return widget

def create_tab_2_13(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.13"))
    return widget

def create_tab_2_20(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.20"))
    return widget

def create_tab_2_21(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.21"))
    return widget

def create_tab_2_22(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.22"))
    return widget

def create_tab_2_22_1(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.22.1"))
    return widget

def create_tab_2_22_2(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.22.2"))
    return widget

def create_tab_2_22_3(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.22.3"))
    return widget

def create_tab_2_22_4(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.22.4"))
    return widget

def create_tab_2_28(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.28"))
    return widget

def create_tab_2_29(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.29"))
    return widget

def create_tab_2_3(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.3"))
    return widget

def create_tab_2_30(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.30"))
    return widget

def create_tab_2_31(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.31"))
    return widget

def create_tab_2_32(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.32"))
    return widget

def create_tab_2_33(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.33"))
    return widget

def create_tab_2_5(icons):
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.addWidget(QLabel("Conteúdo customizado para 2.5"))
    return widget

def create_trilha_auditoria(title_text, icons):
    main_frame = QFrame()
    main_layout = QVBoxLayout(main_frame)
    main_layout.setContentsMargins(10, 10, 10, 10)
    main_layout.setSpacing(15)
    apply_edit_dialog_style(main_frame)

    # Barra de título
    title_layout = QHBoxLayout()
    title_label = QLabel("")  # Será atualizado conforme a aba selecionada
    title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
    title_layout.addWidget(title_label)
    title_layout.addStretch()
    main_layout.addLayout(title_layout)

    # Frame com o QTabWidget
    tab_frame = QFrame()
    tab_layout = QVBoxLayout(tab_frame)
    tab_widget = QTabWidget()
    tab_layout.addWidget(tab_widget)
    tab_widget.tabBar().setCursor(Qt.CursorShape.PointingHandCursor)

    # Mapeamento dos valores (rótulo reduzido) para as funções customizadas
    tab_functions = {
        "2.01": lambda: create_tab_2_01(icons),
        "2.12": lambda: create_tab_2_12(icons),
        "2.13": lambda: create_tab_2_13(icons),
        "2.20": lambda: create_tab_2_20(icons),
        "2.21": lambda: create_tab_2_21(icons),
        "2.22": lambda: create_tab_2_22(icons),
        "2.22.1": lambda: create_tab_2_22_1(icons),
        "2.22.2": lambda: create_tab_2_22_2(icons),
        "2.22.3": lambda: create_tab_2_22_3(icons),
        "2.22.4": lambda: create_tab_2_22_4(icons),
        "2.28": lambda: create_tab_2_28(icons),
        "2.29": lambda: create_tab_2_29(icons),
        "2.3": lambda: create_tab_2_3(icons),
        "2.30": lambda: create_tab_2_30(icons),
        "2.31": lambda: create_tab_2_31(icons),
        "2.32": lambda: create_tab_2_32(icons),
        "2.33": lambda: create_tab_2_33(icons),
        "2.5": lambda: create_tab_2_5(icons),
    }

    # Dicionário para mapear o rótulo reduzido para o título completo da aba
    full_titles = {
        "2.01": "2.01 Solicitação de Auditoria - Alta Materialidade",
        "2.12": "2.12 Preço Homologado acima do Estimado",
        "2.13": "2.13 Limite de Dispensa de Licitação (PDM)",
        "2.2": "2.2 Análise de Pregões Abandonados",
        "2.20": "2.20 Registro de Penalidade no SICAF",
        "2.21": "2.21 Ausência de negociação do valor da proposta.",
        "2.22": "2.22 Ausência de publicação do aviso do edital no Portal de Licitações",
        "2.22.1": "2.22.1 Ausência de divulgação no Portal de Licitações (Publicação de Inexigibilidade/Dispensa)",
        "2.22.2": "2.22.2 Ausência de divulgação no Portal de Licitações (Publicação de extrato do contrato)",
        "2.22.3": "2.22.3 Ausência de divulgação no Portal de Licitações (Publicação de extrato de ata de registro de preços)",
        "2.22.4": "2.22.4 Divulgação, no Portal de Licitações de documentos que não permite a pesquisa de conteúdos",
        "2.28": "2.28 Fragilidade na Estimativa da Demanda",
        "2.29": "2.29 Assinatura de documento nato-digital",
        "2.3": "2.3 Análise de Publicação de Matérias da Seção 3 do DOU",
        "2.30": "2.30 Aplicação de Sações Administrativas",
        "2.31": "2.31 Fornecedor com restrição para contratação",
        "2.32": "2.32 Aplicabilidade da Lei Geral de Proteção de Dados (LGPD) aos Contratos",
        "2.33": "2.33 Dispensa Eletrônica",
        "2.5": "2.5 Análise Processual de Alta Materialidade",
    }

    # Criação das abas com o rótulo reduzido
    for key, func in tab_functions.items():
        tab_widget.addTab(func(), key)

    # Função para atualizar o título concatenado (title_text + título completo da aba)
    def update_title(index):
        tab_key = tab_widget.tabText(index)
        full_title = full_titles.get(tab_key, "")
        title_label.setText(f"{title_text} - {full_title}")

    tab_widget.currentChanged.connect(update_title)
    if tab_widget.count() > 0:
        update_title(0)

    main_layout.addWidget(tab_frame)
    return main_frame

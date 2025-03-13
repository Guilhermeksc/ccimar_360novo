import webbrowser
from PyQt6.QtWidgets import (
    QWidget, QMessageBox, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QFrame, QPushButton, QTreeView
)
from PyQt6.QtCore import QRegularExpression, Qt
from PyQt6.QtGui import QRegularExpressionValidator, QStandardItemModel, QStandardItem
import datetime
from utils.styles.style_add_button import add_button_func
from .treeview import consultar_atas, load_unidades, load_atas_detalhes, save_atas_to_db, create_tables
from utils.styles.style_treeview import apply_treeview_style

### 📌 CONFIGURAÇÃO DO TREEVIEW ###
def setup_treeview(tree_view, icons):
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(["Informações"])
    
    # Carregar as unidades ao inicializar
    load_unidades(model)  
    
    # Conectar a expansão ao carregamento sob demanda, passando os ícones
    tree_view.setModel(model)
    tree_view.expanded.connect(lambda index: load_atas_detalhes(model, model.itemFromIndex(index), icons))
    tree_view.clicked.connect(lambda index: on_treeview_click(index, model))
    
    return model

def on_treeview_click(index, model):
    """Captura o clique no TreeView e abre o PDF se o item for um link."""
    item = model.itemFromIndex(index)
    if item and item.data(Qt.ItemDataRole.UserRole):
        url = item.data(Qt.ItemDataRole.UserRole)
        print(f"🔗 Abrindo PDF: {url}")  # Debug para verificar
        webbrowser.open(url)
        
### 📌 FUNÇÃO PRINCIPAL DA INTERFACE ###
def create_atas(title_text, icons):
    icons = icons
    main_frame = QFrame()
    main_layout = QVBoxLayout(main_frame)
    main_layout.setContentsMargins(10, 10, 10, 10)
    main_layout.setSpacing(15)

    main_frame.setStyleSheet("""
        QLabel {
            color: #FFFFFF;
            font-size: 16px;            
        }
        QLineEdit {
            background-color: #FFFFFF;
            font-size: 16px;            
        }   
    """)

    # Barra de título
    title_layout = QHBoxLayout()
    title_label = QLabel(title_text)
    title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
    title_layout.addWidget(title_label)
    title_layout.addStretch()
    main_layout.addLayout(title_layout)

    # Layout principal
    content_layout = QHBoxLayout()

    # **Widget para input_layout (Largura fixa de 300px)**
    input_widget = QWidget()
    input_widget.setFixedWidth(300)
    input_layout = QVBoxLayout(input_widget)

    # **Widget para response_layout (Expansível)**
    response_widget = QWidget()
    response_layout = QVBoxLayout(response_widget)
    response_layout.setContentsMargins(10, 0, 0, 0)  # Margem esquerda para separação

    # **Input Fields**
    def add_input(label_text, default_value="", validator_pattern=None):
        label = QLabel(label_text)
        input_field = QLineEdit()
        input_field.setText(default_value)
        if validator_pattern:
            input_field.setValidator(QRegularExpressionValidator(QRegularExpression(validator_pattern)))
        input_layout.addWidget(label)
        input_layout.addWidget(input_field)
        return input_field

    data_inicial_input = add_input("Data Inicial * (YYYYMMDD):", (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y%m%d'), "[0-9]{8}")
    data_final_input = add_input("Data Final * (YYYYMMDD):", datetime.datetime.now().strftime('%Y%m%d'), "[0-9]{8}")
    cnpj_input = add_input("CNPJ (default: 00394502000144):", "00394502000144", "[0-9]{14}")
    codigo_unidade_input = add_input("Código UASG (6 digits):", "", "[0-9]{6}")

    # **TreeView para exibir a resposta**
    tree_view = QTreeView()
    apply_treeview_style(tree_view)  # Aplica o estilo ao TreeView
    response_layout.addWidget(tree_view)

    # Configurar o TreeView com carregamento sob demanda
    model = setup_treeview(tree_view, icons)

    # **Função de consulta**
    def on_consultar_button_click():
        data_inicial = data_inicial_input.text()
        data_final = data_final_input.text()
        cnpj = cnpj_input.text()
        codigo_unidade = codigo_unidade_input.text()

        atas = consultar_atas(data_inicial, data_final, cnpj, codigo_unidade)
        if atas:
            print(f"Total de atas recuperadas: {len(atas)}")  # Print de verificação final

            # Salvar as atas no banco de dados antes de carregar no TreeView
            save_atas_to_db(atas)

            # Atualizar o TreeView
            model.clear()
            model.setHorizontalHeaderLabels(["Informações"])
            load_unidades(model)

    # **Centralizar botão no layout**
    button_layout = QHBoxLayout()
    button_layout.addStretch()  # Espaço antes do botão
    btn_consulta_ata = add_button_func("Consultar Atas", "api", on_consultar_button_click, button_layout, icons, tooltip="Clique para consultar as atas", button_size=(200, 40))
    button_layout.addStretch()  # Espaço depois do botão

    input_layout.addLayout(button_layout)  # Adicionar botão centralizado ao input_layout
    input_layout.addStretch()  # Espaço depois do botão

    # **Adicionar widgets ao layout principal**
    content_layout.addWidget(input_widget)   # Largura fixa de 300px
    content_layout.addWidget(response_widget, 1)  # Expansível
    main_layout.addLayout(content_layout)

    return main_frame

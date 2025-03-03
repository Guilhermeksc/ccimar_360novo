from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import os
import subprocess
from docx import Document
from paths import TEMPLATE_TEST_PATH
from .treeview_menu import TreeMenu
from .draggable_view_pdf import DraggableGraphicsView
from utils.add_button import add_button

class UtilsView(QMainWindow):
    # Sinais para comunicação com o controlador
    prev_page = pyqtSignal()
    next_page = pyqtSignal()
    selectpdf = pyqtSignal()
   
    def __init__(self, icons, model, database_path, parent=None):
        super().__init__(parent)
        self.icons = icons
        self.model = model
        self.database_path = database_path
        self.document = None
        # Configura a interface de usuário
        self.setup_ui()
        self.current_content_layout = None

    def setup_ui(self):
        """Configura o layout com menu lateral via TreeMenu."""
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Menu lateral utilizando TreeMenu
        menu_layout = QVBoxLayout()
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(0)

        self.tree_menu = TreeMenu(owner=self)
        menu_layout.addWidget(self.tree_menu)

        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        menu_layout.addItem(spacer)

        menu_widget = QWidget()
        menu_widget.setLayout(menu_layout)
        menu_widget.setStyleSheet("background-color: #181928;")
        main_layout.addWidget(menu_widget, stretch=1)

        # Área de conteúdo
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        main_layout.addWidget(self.content_widget, stretch=4)

    def show_oficio_ccimar20_widget(self):
        """Exibe o visualizador de PDF e configura o layout."""
        self.clear_content()
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Título
        title = QLabel("Extração de Ofício do CCIMAR-20")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #4E648B")
        main_layout.addWidget(title)

        button_layout = QHBoxLayout()
        select_pdf_text = QLabel("Selecione o arquivo PDF para processar:")
        button_layout.addWidget(select_pdf_text)

        add_button("Selecione", "click", self.selectpdf, button_layout, self.icons,
                tooltip="Selecione o PDF para ser processado")

        process_pdf_text = QLabel("Processar o arquivo PDF:")
        button_layout.addWidget(process_pdf_text)

        add_button("PDF escaneado", "pdf", self.selectpdf, button_layout, self.icons,
                tooltip="Selecione o PDF para ser processado")

        add_button("PDF não escaneado", "pdf", self.selectpdf, button_layout, self.icons,
                tooltip="Selecione o PDF para ser processado")
        main_layout.addLayout(button_layout)

        self.pdf_path_label = QLabel("Nenhum arquivo selecionado")

        main_layout.addWidget(self.pdf_path_label)

        # Layout horizontal principal
        content_layout = QHBoxLayout()

        # ─── Painel Central: Visualizador de PDF ───
        viewer_layout = QVBoxLayout()
        
        self.pdf_view = DraggableGraphicsView()
        self.scene = QGraphicsScene()
        self.pdf_view.setScene(self.scene)
        self.pdf_view.setFixedSize(700, 700)
        viewer_layout.addWidget(self.pdf_view)

        # Botões de navegação
        navigation_widget = QWidget()
        nav_buttons_layout = QHBoxLayout(navigation_widget)

        self.prev_page_button = QPushButton("← Página Anterior")
        self.prev_page_button.clicked.connect(self.prev_page)

        self.page_label = QLabel("1 de 1")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_label.setStyleSheet("font-size: 14px; margin: 5px;")

        self.next_page_button = QPushButton("Próxima Página →")
        self.next_page_button.clicked.connect(self.next_page)

        nav_buttons_layout.addWidget(self.prev_page_button)
        nav_buttons_layout.addWidget(self.page_label, 1)
        nav_buttons_layout.addWidget(self.next_page_button)
        
        navigation_widget.setMaximumWidth(700)
        viewer_layout.addWidget(navigation_widget)

        content_layout.addLayout(viewer_layout)
        main_layout.addLayout(content_layout)

        self.content_layout.addWidget(widget)

    def adjust_zoom(self, value):
        # Calcula o fator de escala com base no valor do slider (mínimo 0.5)
        scale_factor = max(value / 100.0, 0.2)
        self.pdf_view.resetTransform()
        self.pdf_view.scale(scale_factor, scale_factor)

    def display_pdf(self, item, column):
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        if file_path:
            print(f"Tentando abrir o arquivo PDF: {file_path}")
            self.load_pdf(file_path)

    def update_preview_size(self, value):
        # Atualiza o tamanho da visualização do PDF conforme o slider
        self.pdf_preview.setFixedSize(value, value)

    def show_relatorio_consultas_airflow_widget(self):
        self.clear_content()
        # Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        # Widget principal para o conteúdo da scroll area
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        # Título
        title = QLabel("Consultas do Airflow")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #4E648B")
        layout.addWidget(title)

        # Configura o widget no scroll area
        scroll_area.setWidget(scroll_widget)

        # Adiciona o scroll area ao layout principal
        self.content_layout.addWidget(scroll_area)

    def show_relatorio_sgm_widget(self):
        self.clear_content()
        # Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        # Widget principal para o conteúdo da scroll area
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        # Título
        title = QLabel("Relatório SGM")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #4E648B")
        layout.addWidget(title)

        # Configura o widget no scroll area
        scroll_area.setWidget(scroll_widget)

        # Adiciona o scroll area ao layout principal
        self.content_layout.addWidget(scroll_area)

    def show_relatorio_ccimar11_widget(self):
        self.clear_content()
        # Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        # Widget principal para o conteúdo da scroll area
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        # Título
        title = QLabel("Relatório CCIMAR-11")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #4E648B")
        layout.addWidget(title)

        # Configura o widget no scroll area
        scroll_area.setWidget(scroll_widget)

        # Adiciona o scroll area ao layout principal
        self.content_layout.addWidget(scroll_area)

    def show_relatorio_cofamar_widget(self):
        self.clear_content()
        # Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        # Widget principal para o conteúdo da scroll area
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        # Título
        title = QLabel("Relatório COFAMAR")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #4E648B")
        layout.addWidget(title)

        # Configura o widget no scroll area
        scroll_area.setWidget(scroll_widget)

        # Adiciona o scroll area ao layout principal
        self.content_layout.addWidget(scroll_area)

    def show_relatorio_calculo_total_widget(self):
        self.clear_content()
        # Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        # Widget principal para o conteúdo da scroll area
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        # Título
        title = QLabel("Gerar Nota com Cálculo Total")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #4E648B")
        layout.addWidget(title)

        # Configura o widget no scroll area
        scroll_area.setWidget(scroll_widget)

        # Adiciona o scroll area ao layout principal
        self.content_layout.addWidget(scroll_area)

    def show_relatorio_notas_monitoradas_widget(self):
        self.clear_content()
        # Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        # Widget principal para o conteúdo da scroll area
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        # Título
        title = QLabel("Notas Monitoradas")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #4E648B")
        layout.addWidget(title)

        # Configura o widget no scroll area
        scroll_area.setWidget(scroll_widget)

        # Adiciona o scroll area ao layout principal
        self.content_layout.addWidget(scroll_area)

    def show_relatorio_audcont_widget(self):
        self.clear_content()
        # Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        # Widget principal para o conteúdo da scroll area
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        # Título
        title = QLabel("AUDCONT - Notas Vencidas")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #4E648B")
        layout.addWidget(title)

        # Configura o widget no scroll area
        scroll_area.setWidget(scroll_widget)

        # Adiciona o scroll area ao layout principal
        self.content_layout.addWidget(scroll_area)
    def handle_tree_double_click(self, index):
        item = self.tree_model.itemFromIndex(index)
        callback = item.data(Qt.ItemDataRole.UserRole)
        if callable(callback):
            callback()
            
    def set_selected_button(self, selected_button):
        """Define o botão selecionado no menu lateral."""
        for button in self.config_menu_buttons:
            button.setChecked(False)
        selected_button.setChecked(True)

    def clear_content(self):
        """Limpa o layout atual do content_widget."""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

    def clear_layout(self, layout):
        """Recursivamente limpa um layout."""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())


    def show_gerar_notas_widget(self):
        self.clear_content()
        # Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        # Widget principal para o conteúdo da scroll area
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)
        # Título
        title = QLabel("Gerar Notas")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #4E648B")
        layout.addWidget(title)

        # Configura o widget no scroll area
        scroll_area.setWidget(scroll_widget)

        # Adiciona o scroll area ao layout principal
        self.content_layout.addWidget(scroll_area)

    def show_teste_widget(self):
        self.clear_content()
        # Widget principal para o conteúdo da scroll area
        teste_widget = QWidget()
        layout = QVBoxLayout(teste_widget)
        # Título
        title = QLabel("Teste")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #4E648B")
        layout.addWidget(title)

        # Campos de entrada
        self.pasta_input = QLineEdit()
        self.pasta_input.setPlaceholderText("Nome da Pasta")
        layout.addWidget(self.pasta_input)
        
        self.setor_input = QLineEdit()
        self.setor_input.setPlaceholderText("Setor Responsável")
        layout.addWidget(self.setor_input)
        
        self.natalia_input = QLineEdit()
        self.natalia_input.setPlaceholderText("natalia")
        layout.addWidget(self.natalia_input)

        # Botões
        self.btn_criar_pasta = QPushButton("Criar Pasta")
        self.btn_criar_pasta.clicked.connect(self.criar_pasta)
        layout.addWidget(self.btn_criar_pasta)
        
        self.btn_criar_pasta_docx = QPushButton("Criar Pasta e Arquivos DOCX")
        self.btn_criar_pasta_docx.clicked.connect(self.criar_pasta_e_docx)
        layout.addWidget(self.btn_criar_pasta_docx)
        
        self.btn_criar_pasta_pdf = QPushButton("Criar Pasta e Arquivos PDF")
        self.btn_criar_pasta_pdf.clicked.connect(self.criar_pasta_e_pdf)
        layout.addWidget(self.btn_criar_pasta_pdf)

        # Adiciona o scroll area ao layout principal
        self.content_layout.addWidget(teste_widget)


    def criar_pasta(self):
        nome_pasta = self.pasta_input.text().strip()
        if nome_pasta:
            caminho_pasta = os.path.join(os.path.expanduser("~/Desktop"), nome_pasta)
            os.makedirs(caminho_pasta, exist_ok=True)
            try:
                if os.name == "nt":  # Windows
                    os.startfile(caminho_pasta)
                elif os.name == "posix":  # Linux/Mac
                    subprocess.run(["xdg-open", caminho_pasta])
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao abrir a pasta: {e}")

    def criar_pasta_e_docx(self):
        self.criar_pasta()
        nome_pasta = self.pasta_input.text().strip()
        setor_responsavel = self.setor_input.text().strip()
        natalia = self.natalia_input.text().strip()
        caminho_pasta = os.path.join(os.path.expanduser("~/Desktop"), nome_pasta)
        
        if nome_pasta:
            try:
                doc = Document(TEMPLATE_TEST_PATH)
                for var in doc.paragraphs:
                    if "{{setor_responsavel}}" in var.text:
                        var.text = var.text.replace("{{setor_responsavel}}", setor_responsavel)
                    if "{{natalia}}" in var.text:
                        var.text = var.text.replace("{{natalia}}", natalia)

                doc_path = os.path.join(caminho_pasta, "documento.docx")
                doc.save(doc_path)
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao criar o arquivo DOCX: {e}")

    def criar_pasta_e_pdf(self):
        self.criar_pasta_e_docx()  # Criar DOCX primeiro
        nome_pasta = self.pasta_input.text().strip()
        caminho_pasta = os.path.join(os.path.expanduser("~/Desktop"), nome_pasta)
        
        if nome_pasta:
            docx_path = os.path.join(caminho_pasta, "documento.docx")
            pdf_path = os.path.join(caminho_pasta, "documento.pdf")
            
            # Convert DOCX to PDF (necessário o LibreOffice ou outra solução instalada)
            try:
                os.system(f'libreoffice --headless --convert-to pdf "{docx_path}" --outdir "{caminho_pasta}"')
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao converter para PDF: {e}")
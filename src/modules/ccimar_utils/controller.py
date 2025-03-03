from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import QObject, Qt
from PyQt6.QtGui import QPixmap, QImage
import fitz  # PyMuPDF para manipular PDFs
import os

class UtilsController(QObject): 
    def __init__(self, icons, view, model):
        super().__init__()
        self.icons = icons
        self.view = view
        self.model_add = model
        self.model = model.setup_model("controle_planejamento")
        self.document = None
        self.current_page = 0  # Página atual
        self.setup_connections()

    def setup_connections(self):
        """Conecta os sinais da view aos métodos do controlador"""
        self.view.selectpdf.connect(self.select_pdf_file)
        self.view.prev_page.connect(self.prev_page)
        self.view.next_page.connect(self.next_page)

    def select_pdf_file(self):
        """Abre um diálogo para selecionar um PDF e exibe no visualizador."""
        file_path, _ = QFileDialog.getOpenFileName(
            self.view,
            "Selecionar PDF",
            "",
            "Arquivos PDF (*.pdf)"
        )

        if file_path:
            file_path = os.path.normpath(file_path)  # Normaliza o caminho para Windows e Linux
            self.view.pdf_path_label.setText(file_path)  # Atualiza o caminho no QLabel
            self.load_pdf(file_path)  # Carrega o PDF no visualizador
        else:
            QMessageBox.warning(self.view, "Aviso", "Nenhum arquivo PDF foi selecionado.")

    def load_pdf(self, file_path):
        """Carrega o PDF e exibe a primeira página"""
        try:
            self.view.document = fitz.open(file_path)  # ✅ Armazena na View
            self.view.current_page = 0  # ✅ Armazena na View
            self.show_page(self.view.current_page)  # Exibe a página
        except Exception as e:
            QMessageBox.critical(self.view, "Erro", f"Erro ao carregar o PDF:\n{str(e)}")

    def show_page(self, page_number):
        """Renderiza e exibe uma página do PDF"""
        if self.view.document:  # ✅ Agora acessamos self.view.document
            try:
                page = self.view.document[page_number]
                mat = fitz.Matrix(4, 4)  # Ajuste de escala para melhor qualidade
                pix = page.get_pixmap(matrix=mat)
                img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(img)

                self.view.scene.clear()  # Limpa a cena antes de adicionar uma nova página
                self.view.scene.addPixmap(pixmap)

                # Atualiza a contagem de páginas
                total_pages = len(self.view.document)
                self.view.page_label.setText(f"{page_number + 1} de {total_pages}")
            except Exception as e:
                QMessageBox.critical(self.view, "Erro", f"Erro ao exibir a página:\n{str(e)}")

    def next_page(self):
        """Avança para a próxima página do PDF"""
        if self.view.document and self.view.current_page < len(self.view.document) - 1:
            self.view.current_page += 1
            self.show_page(self.view.current_page)

    def prev_page(self):
        """Retorna à página anterior do PDF"""
        if self.view.document and self.view.current_page > 0:
            self.view.current_page -= 1
            self.show_page(self.view.current_page)

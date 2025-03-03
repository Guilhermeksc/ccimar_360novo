# src/modules/ccimar11_planejamento/controller.py
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

class CCIMAR12Controller(QObject): 
    def __init__(self, icons, view, model):
        super().__init__()
        self.icons = icons
        self.view = view
        self.model = model.setup_model("ccimar12_db")
        self.setup_connections()

    def setup_connections(self):
        # Conecta os sinais da view aos métodos do controlador
        self.view.teste.connect(self.teste)

    def teste(self):
        pass

def show_warning_if_view_exists(view, title, message):
    if view is not None:
        QMessageBox.warning(view, title, message)
    else:
        print(message)  # Mensagem para o log, caso `view` esteja indisponível
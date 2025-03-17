import sys
import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from PyQt6.QtCore import Qt, QSize, QMetaObject, QThread, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QWidget, QComboBox, QFrame
)

# URLS das opções
URL_BASE = "https://www.google.com.br"
URLS = {
    "Licitações": "https://licitacoescontratos.marinha.mil.br/licitacoes",
    "Adesões": "https://licitacoescontratos.marinha.mil.br/licitacao/OMParticipanteeAdesao",
    "Contratações Diretas": "https://licitacoescontratos.marinha.mil.br/contratacoesdiretas",
    "Atas de Registro de Preços": "https://licitacoescontratos.marinha.mil.br/atas",
    "Contratos": "https://licitacoescontratos.marinha.mil.br/atas"
}

class RPAThread(QThread):
    """Thread para exibir a sobreposição RPA corretamente no loop de eventos do Qt."""
    overlay_ready = pyqtSignal(QWidget)

    def __init__(self, driver, main_window):
        super().__init__()
        self.driver = driver
        self.main_window = main_window
        self.overlay = None

    def run(self):
        """Executa a sobreposição na thread correta do Qt."""
        self.create_overlay()

    @pyqtSlot()
    def create_overlay(self):
        """Cria e exibe a sobreposição na thread principal"""
        self.overlay = RPAOverlay(self.driver, self.main_window, self)
        self.overlay_ready.emit(self.overlay)
        self.overlay.show()

class RPAOverlay(QWidget):
    """ Janela flutuante fixa no topo com botões de controle e seleção de opções """
    def __init__(self, driver, main_window, rpa_thread):
        super().__init__()
        self.driver = driver
        self.main_window = main_window
        self.rpa_thread = rpa_thread  # Referência para encerrar corretamente
        
        # ✅ Garante que a janela fique SEMPRE no topo e não perca foco
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool |
            Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self.setFixedSize(300, 150)
        self.setStyleSheet("background-color: #1E1E2E; color: white; border-radius: 10px; padding: 10px;")

        # Layout principal
        main_layout = QVBoxLayout(self)

        # Header layout (Botões)
        header_layout = QHBoxLayout()
        self.play_button = QPushButton("▶ Play")
        self.play_button.setEnabled(False)
        self.stop_button = QPushButton("⏹ Stop")
        self.exit_button = QPushButton("✖")

        self.play_button.clicked.connect(self.start_script)
        self.stop_button.clicked.connect(self.restart_script)
        self.exit_button.clicked.connect(self.close_app)

        header_layout.addWidget(self.play_button)
        header_layout.addWidget(self.stop_button)
        header_layout.addWidget(self.exit_button)

        # Combobox de opções
        self.combo_box = QComboBox()
        self.combo_box.addItems(["Selecione uma opção"] + list(URLS.keys()))
        self.combo_box.currentIndexChanged.connect(self.enable_play_button)

        # Adicionando elementos ao layout principal
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.combo_box)

        # ✅ Centralizar a sobreposição no topo da tela
        screen_geometry = QApplication.primaryScreen().geometry()
        self.move(
            screen_geometry.center().x() - self.width() // 2,
            50  # Mantém no topo da tela
        )

        self.show()



    def button_style(self):
        """ Retorna o estilo dos botões """
        return """
            QPushButton {
                background-color: #A17B00;
                color: white;
                font-weight: bold;
                border: 1px solid #CCCCCC;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #D9A400; }
        """

    def exit_button_style(self):
        """ Estilo do botão de fechar """
        return """
            QPushButton {
                background-color: red;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: darkred; }
        """

    def enable_play_button(self):
        """ Habilita o botão de play quando uma opção for selecionada """
        self.play_button.setEnabled(self.combo_box.currentIndex() > 0)

    def start_script(self):
        """ Navega para a página correspondente ao clicar em Play """
        selected_option = self.combo_box.currentText()
        if selected_option in URLS:
            self.driver.get(URLS[selected_option])

    def restart_script(self):
        """ Retorna à página inicial ao clicar em Stop """
        self.driver.get(URL_BASE)
        self.combo_box.setCurrentIndex(0)
        self.play_button.setEnabled(False)

    def close_app(self):
        """ Fecha o aplicativo, encerra a thread e restaura a janela principal """
        self.driver.quit()
        self.close()

        # **Encerra a thread corretamente**
        if self.rpa_thread:
            self.rpa_thread.quit()
            self.rpa_thread.wait()

        if self.main_window:
            self.main_window.showNormal()  # Restaura a janela minimizada


def iniciar_script():
    """ Inicia o navegador Selenium e exibe a janela flutuante corretamente no loop do Qt """
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)  # Mantém o navegador aberto
    service = Service()  # Ajuste o caminho do driver, se necessário
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(URL_BASE)

    # Obtém a janela principal
    main_window = QApplication.activeWindow()
    if main_window and isinstance(main_window, QMainWindow):
        main_window.showMinimized()

        # 🔥 **Armazena a thread na janela principal** para evitar que seja coletada pelo GC
        if not hasattr(main_window, "rpa_thread") or main_window.rpa_thread is None:
            main_window.rpa_thread = RPAThread(driver, main_window)
            main_window.rpa_thread.overlay_ready.connect(lambda overlay: overlay.show())
            main_window.rpa_thread.start()





def create_rpa_layout(title_text, icons):
    icons = icons
    """ Cria o layout do frame RPA """
    main_frame = QFrame()
    main_layout = QVBoxLayout(main_frame)
    main_layout.setContentsMargins(10, 10, 10, 10)
    main_layout.setSpacing(15)

    title_layout = QHBoxLayout()
    title_label = QLabel(title_text)
    title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
    title_layout.addWidget(title_label)

    start_button = QPushButton("Abrir Portal de Licitações")
    start_button.setFixedSize(QSize(300, 30))
    start_button.setStyleSheet("background-color: #1E1E2E; color: white; font-size: 14px; border-radius: 5px;")
    start_button.setToolTip("Iniciar processamento de licitações")

    # ✅ Call `iniciar_script` without parameters
    start_button.clicked.connect(iniciar_script)

    title_layout.addWidget(start_button)
    main_layout.addLayout(title_layout)
    return main_frame

from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy, QLabel, QFrame
from PyQt6.QtCore import pyqtSignal, Qt
from .menu.treeview_menu import TreeMenu
from .menu.menu_callbacks import *

class CCIMAR11View(QMainWindow):
    teste = pyqtSignal()

    def __init__(self, icons, model, database_model, parent=None):
        super().__init__(parent)
        self.icons = icons
        self.model = model
        self.database_model = database_model
        self.document = None
        self.current_content_layout = None
        self.setup_ui()
        self.load_initial_content() 

    def setup_ui(self):
        """Configures the layout with a sidebar menu using TreeMenu."""
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar menu using TreeMenu
        self.menu_layout = QVBoxLayout()  # Armazena como atributo
        self.menu_layout.setContentsMargins(0, 0, 0, 0)
        self.menu_layout.setSpacing(0)

        self.label = QLabel("CCIMAR11", self)
        self.label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.label.setAttribute(Qt.WidgetAttribute.WA_Hover, True)  # Ativa o hover
        self.label.setStyleSheet("""
            QLabel {
                color: #FFF;
                font-size: 24px;
            }
            QLabel:hover {
                color: #FFD700;
            }
        """)

        self.label.mousePressEvent = self.reload_content  # 🔹 Conectar clique ao recarregar conteúdo

        sub_label = QLabel("Planejamento e Monitoramento", self)
        sub_label.setStyleSheet("color: #FFF; font-size: 12px")

        self.menu_layout.addWidget(self.label)
        self.menu_layout.addWidget(sub_label)
        
        line = QFrame(self)
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #FFF;")
        self.menu_layout.addWidget(line)
        
        spacer = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.menu_layout.addItem(spacer)

        self.tree_menu = TreeMenu(self.icons, owner=self)
        self.menu_layout.addWidget(self.tree_menu)

        # Criando um widget para o menu lateral e armazenando como atributo
        self.menu_widget = QWidget()
        self.menu_widget.setLayout(self.menu_layout)
        self.menu_widget.setStyleSheet("background-color: #181928;")
        self.menu_widget.setFixedWidth(250)  # Largura fixa para o menu

        main_layout.addWidget(self.menu_widget, stretch=0)

        # Área de conteúdo com QFrame para fundo
        self.content_widget = QFrame()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        main_layout.addWidget(self.content_widget, stretch=1)

    def load_initial_content(self):
        """Carrega o conteúdo inicial dentro do content_widget."""
        self.clear_content()

        initial_label = QLabel(" CCIMAR11", self.content_widget)
        initial_label.setStyleSheet("font-size: 18px; color: #333; font-weight: bold;")
        initial_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.content_layout.addWidget(initial_label)

    def reload_content(self, event=None):
        """Recarrega o conteúdo inicial ao clicar no QLabel."""
        self.load_initial_content()

    def toggle_menu(self):
        """Exibe ou oculta o menu lateral dentro da View."""
        menu_visible = self.menu_widget.isVisible()
        self.menu_widget.setVisible(not menu_visible)

    def clear_content(self):
        """Clears the current content inside the content widget."""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

    def clear_layout(self, layout):
        """Recursively clears a layout."""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self.clear_layout(item.layout())

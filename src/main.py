from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from paths import *
from pathlib import Path
from utils.icon_loader import load_icons
from assets.styles.styles import get_menu_button_style, get_menu_button_activated_style
from modules.widgets import *
from config.config_widget import ConfigManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.icons = load_icons()
        self.buttons = {}
        self.active_button = None
        self.inicio_widget = None
        self.setup_ui()
        self.open_initial_page()

    # ====== SETUP DA INTERFACE ======
    def setup_ui(self):
        """Configura a interface principal da aplicação."""
        self.configure_window()
        self.setup_central_widget()
        self.setup_menu()
        self.setup_toggle_button()
        self.setup_content_area()

    def configure_window(self):
        """Configurações básicas da janela principal."""
        self.setWindowTitle("CCIMAR360 - Ciência de Dados Aplicada à Auditoria")
        self.setWindowIcon(self.icons["data-science"])        
        # Posiciona a janela no canto superior esquerdo
        screen_geometry = self.screen().geometry()
        self.move(screen_geometry.left(), screen_geometry.top())
        
    def setup_central_widget(self):
        """Define o widget central e layout principal."""
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.central_layout = QHBoxLayout(self.central_widget)
        self.central_layout.setSpacing(0)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        
    def setup_menu(self):
        """Configura o menu lateral com botões de ícone que mudam de cor ao hover e adiciona tooltips personalizados."""
        self.menu_layout = QVBoxLayout()
        self.menu_layout.setSpacing(0)
        self.menu_layout.setContentsMargins(0, 0, 0, 0)
        self.menu_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Tooltip personalizado
        self.tooltip_label = QLabel("", self)
        self.tooltip_label.setStyleSheet("""
            background-color: #13141F;
            color: white;
            border: 1px solid #8AB4F7;
            padding: 4px;
            border-radius: 4px;
        """)
        self.tooltip_label.setFont(QFont("Arial", 12))
        self.tooltip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tooltip_label.setVisible(False)  # Inicialmente oculto

        # Definindo os botões do menu e seus contextos
        self.menu_buttons = [
            ("init", "init_hover", "Página Inicial", self.show_inicio),
            ("number-10-b", "number-10", "Departamento de Auditoria Interna (CCIMAR-10)", self.show_ccimar10),
            ("number-11-b", "number-11", "Divisão de Planejamento e Monitoramento (CCIMAR-11)", self.show_ccimar11),
            ("number-12-b", "number-12", "Divisão de Licitações (CCIMAR-12)", self.show_ccimar12),
            ("number-13-b", "number-13", "Divisão de Execução (CCIMAR-13)", self.show_ccimar13),
            ("number-14-b", "number-14", "Divisão de Pagamento (CCIMAR-14)", self.show_ccimar14),
            ("number-15-b", "number-15", "Divisão de Material (CCIMAR-15)", self.show_ccimar15),
            ("number-16-b", "number-16", "Divisão de Ciência de Dados Aplicada à Auditoria (CCIMAR-16)", self.show_ccimar16),
            ("data_blue", "data", "Utilidades", self.show_ccimar_utils),
            ("config", "config_hover", "Configurações", self.show_config),
        ]

        # Criando os botões e adicionando-os ao layout do menu
        for icon_key, hover_icon_key, tooltip_text, callback in self.menu_buttons:
            button = self.create_icon_button(icon_key, hover_icon_key, icon_key)
            button.clicked.connect(callback)
            button.installEventFilter(self)  # Instala um filtro de evento para gerenciar o tooltip
            button.setProperty("tooltipText", tooltip_text)  # Define o texto do tooltip como propriedade
            self.menu_layout.addWidget(button)
            self.buttons[icon_key] = button 
            
        # Adiciona um espaço flexível para empurrar o ícone para o final
        self.menu_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Adiciona o ícone 360-degrees.png na parte inferior

        icon_label = QLabel(self)
        icon_label.setPixmap(self.icons["360-degrees"].pixmap(40, 40))  # Define o ícone com tamanho 50x50
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.menu_layout.addWidget(icon_label)

        # Cria um widget para o menu e adiciona o layout
        self.menu_widget = QWidget()
        self.menu_widget.setLayout(self.menu_layout)
        self.menu_widget.setStyleSheet("background-color: #13141F;")

        self.central_layout.addWidget(self.menu_widget)
            
    def eventFilter(self, obj, event):
        """Filtra eventos para exibir tooltips personalizados alinhados à direita dos botões do menu e gerenciar ícones."""
        if isinstance(obj, QPushButton):
            # Evento de entrada do mouse no botão
            if event.type() == QEvent.Type.Enter and obj in self.buttons.values():
                tooltip_text = obj.property("tooltipText")
                if tooltip_text:
                    self.tooltip_label.setText(tooltip_text)
                    self.tooltip_label.adjustSize()

                    # Posição do tooltip alinhada à direita do botão
                    button_pos = obj.mapToGlobal(QPoint(obj.width(), 0))  # Posição global do botão
                    tooltip_x = button_pos.x() + 5  # Ajuste para a direita do botão
                    tooltip_y = button_pos.y() + (obj.height() - self.tooltip_label.height()) // 2  # Centraliza verticalmente
                    self.tooltip_label.move(self.mapFromGlobal(QPoint(tooltip_x, tooltip_y)))  # Converte para coordenadas da janela
                    self.tooltip_label.setVisible(True)

                # Altera o ícone do botão para o estado de hover, se não estiver selecionado
                if not obj.property("isSelected"):
                    obj.setIcon(obj.hover_icon)

            # Evento de saída do mouse do botão
            elif event.type() == QEvent.Type.Leave and obj in self.buttons.values():
                self.tooltip_label.setVisible(False)

                # Retorna o ícone ao estado padrão, se não estiver selecionado
                if not obj.property("isSelected"):
                    obj.setIcon(obj.default_icon)

            # Evento de clique no botão
            elif event.type() == QEvent.Type.MouseButtonPress and obj in self.buttons.values():
                # Desmarca todos os botões e reseta os ícones
                for btn in self.buttons.values():
                    btn.setProperty("isSelected", False)
                    btn.setIcon(btn.default_icon)

                # Marca o botão clicado como selecionado e altera o ícone
                obj.setProperty("isSelected", True)
                obj.setIcon(obj.selected_icon)

        return super().eventFilter(obj, event)        

    def setup_toggle_button(self):
        """Cria um botão sobreposto para ocultar/exibir o menu lateral, posicionado acima do canto inferior esquerdo."""
        self.toggle_button = QPushButton(self)
        self.toggle_button.setIcon(self.icons["menu"])  # Ícone do menu
        self.toggle_button.setIconSize(QSize(30, 30))
        self.toggle_button.setFixedSize(40, 40)
        self.toggle_button.setCursor(Qt.CursorShape.PointingHandCursor) 

        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 100);
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 50);
            }
        """)
        self.toggle_button.clicked.connect(self.toggle_menu)

        # Posicionar o botão dinamicamente ao iniciar e ao redimensionar a janela
        self.update_toggle_button_position()

    def update_toggle_button_position(self):
        """Atualiza a posição do botão para mantê-lo acima do canto inferior esquerdo."""
        margin_bottom = 60  # Distância do canto inferior
        margin_left = 5  # Distância do canto esquerdo

        new_x = margin_left
        new_y = self.height() - self.toggle_button.height() - margin_bottom  # Posição baseada na altura da janela

        self.toggle_button.move(new_x, new_y)

    def resizeEvent(self, event):
        """Recalcula a posição do botão ao redimensionar a janela."""
        self.update_toggle_button_position()
        super().resizeEvent(event)

    def create_icon_button(self, icon_key, hover_icon_key, selected_icon_key):
        button = QPushButton()
        button.setIcon(self.icons[icon_key])  # Ícone padrão
        button.setIconSize(QSize(30, 30))
        button.setStyleSheet(get_menu_button_style())
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setFixedSize(50, 50)

        # Armazena os ícones padrão, de hover e de seleção
        button.default_icon = self.icons[icon_key]
        button.hover_icon = self.icons[hover_icon_key]
        button.selected_icon = self.icons[selected_icon_key]
        button.icon_key = icon_key  # Armazena a chave do ícone

        # Propriedade para gerenciar o estado selecionado
        button.setProperty("isSelected", False)

        # Instala o event filter para capturar eventos de hover e selected
        button.installEventFilter(self)

        return button

    def toggle_menu(self):
        """Exibe ou oculta todo o menu lateral (menu_layout) no MainWindow e na View ativa."""
        menu_visible = self.menu_widget.isVisible()

        # Alterna visibilidade do menu lateral principal
        self.menu_widget.setVisible(not menu_visible)

        # Alterna visibilidade do menu lateral da View, se houver
        if hasattr(self, "current_view") and hasattr(self.current_view, "menu_widget"):
            self.current_view.menu_widget.setVisible(not menu_visible)

        # Atualiza o ícone do botão com base no estado do menu
        self.toggle_button.setIcon(self.icons["menu-open"] if menu_visible else self.icons["menu"])

        # Atualiza layout para evitar espaços vazios
        self.central_layout.update()

    def set_active_button(self, button):
        """Define o botão ativo e altera o ícone para o estado hover permanente."""
        # Reseta o estilo do botão anteriormente ativo
        if self.active_button and self.active_button != button:
            self.active_button.setIcon(self.active_button.default_icon)
            self.active_button.setStyleSheet(get_menu_button_style())

        # Aplica o estilo de botão ativo
        button.setIcon(button.hover_icon)
        button.setStyleSheet(get_menu_button_activated_style())
        self.active_button = button 

    # ====== MÓDULOS ======
    def _show_module(self, model_class, view_class, controller_class, path, module_name: str, button_key: str) -> None:
        """Ensure the model is properly instantiated before passing it."""
        
        self.clear_content_area()

        # 🔍 Convert `path` to a model instance if it's a file path
        if isinstance(path, (str, Path)):  
            model = model_class(str(path))  # ✅ Convert the path to a `CCIMAR11Model` instance
        else:
            model = path  # Already a model instance

        sql_model = model.setup_model(module_name, editable=True)
        
        view = view_class(self.icons, sql_model, model.database_manager.db_path)
        self.current_view = view

        # ✅ Ensure `view.database_model` is an instance, not a path
        view.database_model = model

        controller_class(self.icons, view, model)

        self.content_layout.addWidget(view)
        self.set_active_button(self.buttons[button_key])

    def show_ccimar10(self) -> None:
        self._show_module(CCIMAR10Model, CCIMAR10View, CCIMAR10Controller, CCIMAR10_PATH, "ccimar10", "number-10-b")

    def show_ccimar11(self) -> None:
        self._show_module(CCIMAR11Model, CCIMAR11View, CCIMAR11Controller, CCIMAR11_PATH, "ccimar11", "number-11-b")

    def show_ccimar12(self) -> None:
        self._show_module(CCIMAR12Model, CCIMAR12View, CCIMAR12Controller, CCIMAR12_PATH, "ccimar12", "number-12-b")

    def show_ccimar13(self) -> None:
        self._show_module(CCIMAR13Model, CCIMAR13View, CCIMAR13Controller, CCIMAR13_PATH, "ccimar13", "number-13-b")

    def show_ccimar14(self) -> None:
        self._show_module(CCIMAR14Model, CCIMAR14View, CCIMAR14Controller, CCIMAR14_PATH, "ccimar14", "number-14-b")

    def show_ccimar15(self) -> None:
        self._show_module(CCIMAR15Model, CCIMAR15View, CCIMAR15Controller, CCIMAR15_PATH, "ccimar15", "number-15-b")

    def show_ccimar16(self) -> None:
        self._show_module(CCIMAR16Model, CCIMAR16View, CCIMAR16Controller, CCIMAR16_PATH, "ccimar16", "number-16-b")

    def show_ccimar_utils(self) -> None:
        self._show_module(UtilsModel, UtilsView, UtilsController, CCIMAR_UTIL_PATH, "ccimar_utils", "number-16-b")

    def show_config(self):
        self.clear_content_area()
        # Instanciar o ConfigManager com os ícones
        self.config_manager = ConfigManager(self.icons, self)
        # Adicionar o ConfigManager à área de conteúdo
        self.content_layout.addWidget(self.config_manager)
        # Define o botão correspondente como ativo
        self.set_active_button(self.buttons["config"])

    def show_inicio(self):
        self.clear_content_area()
        self.inicio_widget = InicioWidget(self.icons)
        self.content_layout.addWidget(self.inicio_widget)
        # Define o botão "init" como o ativo (correspondente ao botão inicial)
        self.set_active_button(self.buttons["init"])    
        
    def open_initial_page(self):
        """Abre a página inicial da aplicação."""
        self.clear_content_area()
        # Verifica se inicio_widget foi iniciado corretamente, caso contrário, chama show_inicio
        if not self.inicio_widget :
            self.show_inicio()
        else:
            self.content_layout.addWidget(self.inicio_widget )

        # Define o botão "init" como ativo
        self.set_active_button(self.buttons["init"]) 
        
    # ====== ÁREA DE CONTEÚDO ======
    def setup_content_area(self) -> None:
        """Configura a área principal de conteúdo."""
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(0)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content_image_label = QLabel(self.central_widget)
        self.content_image_label.hide()
        self.content_layout.addWidget(self.content_image_label)
        self.content_widget = QFrame()
        self.content_widget.setObjectName("contentWidget")
        self.content_widget.setLayout(self.content_layout)
        self.content_widget.setMinimumSize(1400, 750)
        self.content_widget.setFrameStyle(QFrame.Shape.NoFrame)
        self.content_widget.setStyleSheet("""
            QFrame#contentWidget {
                background-color: #181928;
            }
        """)
        self.central_layout.addWidget(self.content_widget)

    def clear_content_area(self, keep_image_label: bool = False) -> None:
        """Remove todos os widgets da área de conteúdo, exceto a imagem opcional."""
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget and (widget is not self.content_image_label or not keep_image_label):
                widget.setParent(None)
                    
    # ====== EVENTO DE FECHAMENTO DA JANELA ======

    def closeEvent(self, event):
        """Solicita confirmação ao usuário antes de fechar a janela."""
        reply = QMessageBox.question(
            self, 'Confirmar Saída', "Você realmente deseja fechar o aplicativo?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        event.accept() if reply == QMessageBox.StandardButton.Yes else event.ignore()
                    
if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

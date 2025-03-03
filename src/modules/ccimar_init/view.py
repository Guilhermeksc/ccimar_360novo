from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from pathlib import Path
from paths import ICONS_DIR, CCIMAR360_PATH
from assets.styles.styles import title_view_stylesheet

class InicioWidget(QWidget):
    def __init__(self, icons, parent=None):
        super().__init__(parent)
        self.icons = icons
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # --- Image Label ---
        self.image_label = QLabel(self)
        pixmap = QPixmap(str(CCIMAR360_PATH))
        self.image_label.setPixmap(pixmap.scaledToWidth(250, Qt.TransformationMode.SmoothTransformation))  # Resize width to 250px
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Centering the image
        image_layout = QHBoxLayout()
        image_layout.addStretch()
        image_layout.addWidget(self.image_label)
        image_layout.addStretch()

        self.layout.addLayout(image_layout)

        # Sinopse do projeto
        self.synopsis_label = QLabel(
            "O CCIMAR360 é um aplicativo desenvolvido para aprimorar e automatizar processos relacionados às atividades "
            "de auditoria do Centro de Controle Interno da Marinha (CCIMAR). \n\n"
            "A solução permite a extração, manipulação e análise de documentos em diversos formatos, facilitando a "
            "produção de relatórios e o monitoramento da aplicação de recursos públicos. \n\n"
            "Além disso, incorpora automações baseadas em Robotic Process Automation (RPA) para aprimorar a identificação de"
            "impropriedades, otimizar o fluxo de trabalho e reforçar os controles internos administrativos, garantindo maior"
            "eficiência e transparência nas atividades de auditoria."
        )

        self.synopsis_label.setAlignment(Qt.AlignmentFlag.AlignJustify)
        self.synopsis_label.setWordWrap(True)
        self.synopsis_label.setStyleSheet("font-size: 16px; padding: 10px; color: #BEE3DB;")

        # Adiciona os widgets ao layout
        self.layout.addWidget(self.synopsis_label)

        # Contato
        self.contact_label = QLabel(self)

        self.contact_label.setText(
            'Para suporte, entre em contato pelo e-mail: '
            '<a href="mailto:siqueira.campos@marinha.mil.br" style="color:#FFF; text-decoration:none;">'
            'siqueira.campos@marinha.mil.br</a>'
        )
        self.contact_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contact_label.setOpenExternalLinks(True)
        self.contact_label.setStyleSheet("""
            font-size: 16px;
            padding: 10px;
            color: #BEE3DB;  /* Cor do texto geral */
        """)

        # Adiciona o contato ao layout
        self.layout.addWidget(self.contact_label)


        # Adiciona um espaço flexível para empurrar o contato para o final
        self.layout.addStretch()
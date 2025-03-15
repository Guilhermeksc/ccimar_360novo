from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

class InicioWidget(QWidget):
    def __init__(self, icons, parent=None):
        super().__init__(parent)
        self.icons = icons
        self.title = "DATA-SCIENCEMAR"
        self.setup_ui()
        
    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        datascience_title_layout = QHBoxLayout()
        datascience_title_layout.setContentsMargins(0, 0, 0, 0)
        datascience_title_layout.setSpacing(0)
        
        datascience_title_layout.addStretch()
        # --- Image Label ---
        icon_label = QLabel(self)
        icon_label.setPixmap(self.icons["datasciencemar"].pixmap(200, 200))  # Define o ícone com tamanho 50x50
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        datascience_title_layout.addWidget(icon_label)

        # --- Title Label ---
        title_label = QLabel(self.title)
        title_label.setStyleSheet("font-size: 60px; font-weight: bold; color: #FFFFFF")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        datascience_title_layout.addWidget(title_label)
        datascience_title_layout.addStretch()
        
        self.layout.addStretch()
        self.layout.addLayout(datascience_title_layout)
        self.layout.addStretch()
        # Sinopse do projeto
        self.synopsis_label = QLabel(
            f"O {self.title} é um aplicativo desenvolvido para aprimorar e automatizar processos relacionados às atividades "
            "de auditoria do Centro de Controle Interno da Marinha (CCIMAR). \n\n"
            "A solução permite a extração, manipulação, tratamento e análise de documentos em diversos formatos, facilitando a "
            "produção de relatórios e o monitoramento da aplicação de recursos públicos. \n\n"
            "Além disso, incorpora automações baseadas em Robotic Process Automation (RPA) para aprimorar a identificação de"
            "impropriedades, otimizar o fluxo de trabalho e reforçar os controles internos administrativos, garantindo maior"
            "eficiência e transparência nas atividades de auditoria."
        )

        self.synopsis_label.setAlignment(Qt.AlignmentFlag.AlignJustify)
        self.synopsis_label.setWordWrap(True)
        self.synopsis_label.setStyleSheet("font-size: 18px; padding: 10px; color: #BEE3DB;")

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

        self.layout.addStretch()
        
        # Adiciona o contato ao layout
        self.layout.addWidget(self.contact_label)
        

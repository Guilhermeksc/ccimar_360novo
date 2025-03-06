from PyQt6.QtWidgets import (QLabel, QFrame, QHBoxLayout, QVBoxLayout, QTreeView,
                          QDialog, QPushButton, QLineEdit, QComboBox, QMessageBox,
                          QFileDialog, QListWidget, QListWidgetItem, QWidget, QSizePolicy)
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QFont, QIcon, QDrag, QCursor
from PyQt6.QtCore import Qt, QMimeData
import json
import os
import pandas as pd
import subprocess
import sys
from paths import OBJETIVOS_NAVAIS_PATH


class ClickableLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked_callback()

class CriterioWidget(QWidget):
    def __init__(self, criterio_text, delete_callback, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        # Remove todas as margens
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(2)
        
        # Define o fundo como transparente
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        
        # Botão de exclusão com tamanho reduzido
        delete_label = ClickableLabel()
        delete_label.setText("❌")  # Emoji X como ícone de exclusão
        delete_label.setStyleSheet("color: #ff5555; font-size: 10px; background: transparent; padding: 0px;")
        delete_label.setFixedWidth(15)  # Largura fixa para o botão de exclusão
        delete_label.clicked_callback = delete_callback
        
        # Label do texto do critério
        text_label = QLabel(criterio_text)
        text_label.setStyleSheet("color: #f8f8f2; background: transparent; padding: 0px;")
        
        layout.addWidget(delete_label)
        layout.addWidget(text_label, 1)  # O texto expande para ocupar o espaço disponível
        
        # Ajusta o tamanho do widget para ser o menor possível
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

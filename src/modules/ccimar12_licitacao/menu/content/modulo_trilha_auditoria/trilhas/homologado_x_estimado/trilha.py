from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import QRegularExpressionValidator
from utils.styles.style_add_button import add_button_func
from utils.styles.styles_edit_button import apply_edit_dialog_style
from utils.styles.style_table import apply_table_style
import json
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from paths import JSON_DIR

PATH_DOU_DATA = JSON_DIR / "dou_data.json"

def widget_homologado_x_estimado(title_text, icons):
    class TrilhaWidget(QFrame):
        def __init__(self, title_text, icons):
            super().__init__()
            self.setup_ui(title_text, icons)
            
        def setup_ui(self, title_text, icons):
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(10, 10, 10, 10)
            main_layout.setSpacing(15)
            apply_edit_dialog_style(self)

            title_layout = QHBoxLayout()
            title_label = QLabel(title_text)
            title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
            title_layout.addWidget(title_label)

            # Add buttons
            btn_consultar = add_button_func("Consultar", "add", self.consultar_pncp, title_layout, icons, tooltip="Consultar Diário Oficial da União")

            main_layout.addLayout(title_layout)
            main_layout.addWidget(self.download_link)

        def consultar_pncp(self):
            selected_date = self.date_edit.date().toString("dd-MM-yyyy")
            url = f"https://www.in.gov.br/leiturajornal?secao=dou3&data={selected_date}&org=Minist%C3%A9rio%20da%20Defesa&org_sub=Comando%20da%20Marinha"


class DownloadDouThread(QThread):
    update_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(int)

    def __init__(self, selected_date, parent=None):
        super().__init__(parent)
        self.selected_date = selected_date

    def run(self):
        json_file = 'endpoints.json'
        if not os.path.exists(json_file):
            self.update_signal.emit("Arquivo endpoints.json não encontrado.")
            self.finished_signal.emit(0)
            return

        with open(json_file, 'r', encoding='utf-8') as f:
            endpoints_data = json.load(f)

        date_entry = endpoints_data.get(self.selected_date, {})
        endpoints = date_entry.get("data", [])
        if not endpoints:
            self.update_signal.emit("Nenhum endpoint encontrado para a data selecionada.")
            self.finished_signal.emit(0)
            return

        # Cria a pasta base com a data selecionada
        base_folder = self.selected_date
        if not os.path.exists(base_folder):
            os.makedirs(base_folder)

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=options)
        base_url = "https://www.in.gov.br"
        saved_count = 0

        for endpoint in endpoints:
            full_url = base_url + endpoint
            self.update_signal.emit(f"🚀 Acessando: {full_url}")
            driver.get(full_url)
            time.sleep(2)  # Aguarda o carregamento da página
            page_source = driver.page_source

            if not page_source.strip():
                self.update_signal.emit(f"❌ Conteúdo vazio para: {full_url}")
                continue

            if endpoint.startswith("/web/dou/-/"):
                folder_part = endpoint[len("/web/dou/-/"):]
                folder_name = folder_part.replace("/", "-")
            else:
                folder_name = endpoint.replace("/", "-")
            
            # Cria a subpasta para o endpoint
            endpoint_folder = os.path.join(base_folder, folder_name)
            if not os.path.exists(endpoint_folder):
                os.makedirs(endpoint_folder)

            # Salva o HTML da página para referência
            html_path = os.path.join(endpoint_folder, "page.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(page_source)
            self.update_signal.emit(f"💾 Página salva em: {html_path}")

            saved_count += 1

        driver.quit()
        self.finished_signal.emit(saved_count)
 
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QFont
from PyQt6.QtWidgets import (
    QDateEdit, QWidget, QMessageBox, QVBoxLayout, QHBoxLayout, QDialog,
    QComboBox, QLabel, QPushButton, QFrame, QTextBrowser, QHeaderView
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QThread
from utils.styles.style_add_button import add_button_func
from utils.styles.styles_edit_button import apply_edit_dialog_style
from .tableview import CustomTableView, load_config
from utils.styles.style_table import apply_table_style
import datetime
import json
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import requests
from urllib.parse import urljoin

class ScraperThread(QThread):
    update_signal = pyqtSignal(str)
    result_signal = pyqtSignal(str, int)

    def __init__(self, url, selected_date, parent=None):
        super().__init__(parent)
        self.url = url
        self.selected_date = selected_date

    def run(self):
        self.update_signal.emit("Iniciando scraping com Selenium...")
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=options)
        driver.get(self.url)
        
        # Aguarda o carregamento do elemento principal
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.ID, "hierarchy_content")))
        
        all_endpoints = []
        
        while True:
            time.sleep(2)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            hierarchy_content = soup.find("div", {"id": "hierarchy_content"})
            
            if hierarchy_content:
                h5_tags = hierarchy_content.find_all("h5", class_="title-marker")
                for h5 in h5_tags:
                    a_tag = h5.find("a")
                    if a_tag and a_tag.get("href"):
                        endpoint = a_tag["href"]
                        print("Encontrado:", endpoint)
                        all_endpoints.append(endpoint)
            else:
                self.update_signal.emit("Elemento principal não encontrado!")
                break

            try:
                next_button = driver.find_element(By.XPATH, "//div[contains(@class, 'pagination')]//span[text()='Próximo »']")
                if next_button:
                    self.update_signal.emit("Navegando para próxima página...")
                    next_button.click()
                else:
                    self.update_signal.emit("Botão 'Próximo »' não encontrado. Encerrando scraping.")
                    break
            except Exception:
                self.update_signal.emit("Botão 'Próximo »' não encontrado. Encerrando scraping.")
                break

        driver.quit()

        # Carrega os dados existentes (se houver) e atualiza com a nova data e total de registros
        file_path = 'endpoints.json'
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    json_data = json.load(f)
                except json.JSONDecodeError:
                    json_data = {}
        else:
            json_data = {}

        json_data[self.selected_date] = {
            "data": all_endpoints,
            "total": len(all_endpoints)
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)

        self.update_signal.emit(f"Scraping finalizado. {len(all_endpoints)} endpoints encontrados.")
        self.result_signal.emit("Consulta realizada com sucesso.", len(all_endpoints))
        
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

            # # Extração dos links de download com base no atributo id
            # soup = BeautifulSoup(page_source, "html.parser")
            # download_links = {}
            # for a in soup.find_all("a"):
            #     a_id = a.get("id", "").strip().lower()
            #     if a_id == "versao-certificada":
            #         download_links["versao_certificada"] = a.get("href")
            #         self.update_signal.emit(f"🔍 [DEBUG] Extraído 'Versão certificada': {a.get('href')}")
            #     elif a_id == "diario-completo":
            #         download_links["diario_completo"] = a.get("href")
            #         self.update_signal.emit(f"🔍 [DEBUG] Extraído 'Diário Completo': {a.get('href')}")
            #     elif a_id == "printfunction":
            #         self.update_signal.emit("⚠️ [DEBUG] Ignorado 'Impressão' (link não válido)")
            # self.update_signal.emit(f"🔗 [DEBUG] Links de download encontrados: {download_links}")

            # # Para cada link extraído, obtenha a URL real do PDF e faça o download
            # for key, link in download_links.items():
            #     if not link:
            #         continue
            #     download_url = base_url + link if link.startswith("/") else link
            #     self.update_signal.emit(f"⬇️ Tentando baixar {key} de: {download_url}")

            #     # Acessa a URL de download com Selenium
            #     driver.get(download_url)
            #     time.sleep(2)
            #     pdf_url = download_url  # Valor padrão
            #     page_html = driver.page_source

            #     # Se houver frameset, tenta extrair a URL real do PDF via frame "visualizador"
            #     if "frameset" in page_html.lower():
            #         self.update_signal.emit("🔄 Frameset detectado; alternando para o frame 'visualizador'...")
            #         try:
            #             driver.switch_to.frame("visualizador")
            #             time.sleep(2)
            #             pdf_url = driver.current_url
            #             self.update_signal.emit(f"🔍 URL do PDF extraída: {pdf_url}")
            #         except Exception as e:
            #             self.update_signal.emit(f"❌ Erro ao acessar o frame 'visualizador': {str(e)}")
            #         finally:
            #             driver.switch_to.default_content()
            #     else:
            #         self.update_signal.emit("🔍 Frameset não detectado; utilizando URL original.")

            #     # Configura headers para replicar a requisição do navegador
            #     ua = driver.execute_script("return navigator.userAgent;")
            #     headers = {
            #         "User-Agent": ua,
            #         "Referer": download_url
            #     }

            #     # Cria uma sessão requests e transfere os cookies do Selenium
            #     session = requests.Session()
            #     for cookie in driver.get_cookies():
            #         session.cookies.set(cookie["name"], cookie["value"])

            #     try:
            #         response = session.get(pdf_url, stream=True, headers=headers, timeout=20)
            #         response.raise_for_status()
            #     except Exception as e:
            #         self.update_signal.emit(f"❌ Erro ao baixar o PDF: {str(e)}")
            #         continue

            #     file_name = f"{key}.pdf"
            #     file_path = os.path.join(endpoint_folder, file_name)
            #     with open(file_path, "wb") as f:
            #         for chunk in response.iter_content(chunk_size=8192):
            #             f.write(chunk)
            #     self.update_signal.emit(f"✅ PDF salvo em: {file_path}")

            saved_count += 1

        driver.quit()
        self.finished_signal.emit(saved_count)
                    
def create_webscrapping(title_text, icons):
    main_frame = QFrame()
    main_layout = QVBoxLayout(main_frame)
    main_layout.setContentsMargins(10, 10, 10, 10)
    main_layout.setSpacing(15)
    apply_edit_dialog_style(main_frame)

    title_layout = QHBoxLayout()
    title_label = QLabel("Cadastro - Objetos Auditáveis")
    title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")
    title_layout.addWidget(title_label)

    date_edit = QDateEdit()
    date_edit.setCalendarPopup(True)
    date_edit.setDate(QDate.currentDate())
    date_edit.setStyleSheet("font-size: 14px;")
    title_layout.addWidget(date_edit)
    title_layout.addStretch()

    message_popup = QDialog()
    message_popup.setWindowTitle("Consultando DOU")
    popup_layout = QVBoxLayout(message_popup)
    message_label = QTextBrowser()
    popup_layout.addWidget(message_label)
    message_popup.setModal(True)

    def consultar_dou():
        selected_date = date_edit.date().toString("dd-MM-yyyy")
        url = f"https://www.in.gov.br/leiturajornal?secao=dou3&data={selected_date}&org=Minist%C3%A9rio%20da%20Defesa&org_sub=Comando%20da%20Marinha"

        def update_message(msg):
            message_label.append(msg)

        def process_result(status, num_pages):
            message_label.append(status)
            if num_pages:
                message_label.append(f"Número de páginas encontradas: {num_pages}")
            message_popup.accept()

        scraper_thread = ScraperThread(url, selected_date, message_popup)
        scraper_thread.update_signal.connect(update_message)
        scraper_thread.result_signal.connect(process_result)
        scraper_thread.start()
        message_popup.exec()
    
    def iniciar_download_dou():
        json_file = 'endpoints.json'
        if not os.path.exists(json_file):
            print("Arquivo endpoints.json não encontrado.")
            return

        with open(json_file, 'r', encoding='utf-8') as f:
            endpoints_data = json.load(f)
        
        available_dates = list(endpoints_data.keys())
        if not available_dates:
            print("Nenhuma data disponível no arquivo endpoints.json.")
            return

        # Diálogo para seleção da data
        dialog = QDialog()
        dialog.setWindowTitle("Selecione a Data")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Escolha uma data para consulta:"))
        combo = QComboBox()
        combo.addItems(available_dates)
        layout.addWidget(combo)
        buttons_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancelar")
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            print("Operação cancelada pelo usuário.")
            return

        selected_date = combo.currentText()
        print(f"Data selecionada: {selected_date}")

        download_thread = DownloadDouThread(selected_date)
        download_thread.update_signal.connect(lambda msg: print(msg))
        download_thread.finished_signal.connect(lambda count: print(f"Download finalizado. Páginas salvas: {count}"))
        # Armazena a referência no widget principal (ex.: main_frame)
        main_frame.download_thread = download_thread
        download_thread.start()

                
    btn_consultar = add_button_func("Consultar", "add", consultar_dou, title_layout, icons, tooltip="Consultar Diário Oficial da União")
    btn_dowload = add_button_func("Exportar", "export", iniciar_download_dou, title_layout, icons, tooltip="Exportar dados")
    btn_import = add_button_func("Importar", "import", lambda: None, title_layout, icons, tooltip="Importar dados")
    btn_relatorio = add_button_func("Relatório", "report", lambda: None, title_layout, icons, tooltip="Visualizar relatório")

    main_layout.addLayout(title_layout)

    # table_view = CustomTableView()
    # table_view.setFont(QFont("Arial", 12))
    # apply_table_style(table_view)

    # model = QStandardItemModel()
    # table_view.setModel(model)
    # headers = ["UASG", "Tipo", "Objetos Auditáveis", "Objetivo da Auditoria", "Origem da Demanda", "Início", "Conclusão", "HH", "Situação", "Observações/Justificativas"]
    # model.setHorizontalHeaderLabels(headers)

    # for col in range(len(headers)):
    #     header_item = model.horizontalHeaderItem(col)
    #     if header_item:
    #         header_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

    # table_view.verticalHeader().setDefaultSectionSize(30)
    # main_layout.addWidget(table_view)

    return main_frame

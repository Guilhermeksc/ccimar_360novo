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
import calendar

def widget_trilha(title_text, icons):
    main_frame = QFrame()
    main_layout = QVBoxLayout(main_frame)
    main_layout.setContentsMargins(10, 10, 10, 10)
    main_layout.setSpacing(15)
    apply_edit_dialog_style(main_frame)

    title_layout = QHBoxLayout()
    title_label = QLabel(title_text)
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

    return main_frame

import os
import json
import time
from PyQt6.QtCore import QThread, pyqtSignal
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

class ScraperThread(QThread):
    update_signal = pyqtSignal(str)
    result_signal = pyqtSignal(str, int)

    def __init__(self, url, selected_date, parent=None):
        super().__init__(parent)
        self.url = url
        self.selected_date = selected_date  # Data da consulta (DD-MM-YYYY)

    def run(self):
        self.update_signal.emit("Iniciando scraping com Selenium...")
        options = Options()
        options.add_argument("--headless")  # Executa sem abrir janela
        options.add_argument("--disable-gpu")
        driver = webdriver.Firefox(options=options)
        driver.get(self.url)

        # Aguarda o carregamento da seção principal do conteúdo
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
                        full_url = f"https://www.in.gov.br{endpoint}"  # Formata corretamente a URL
                        print(f"Encontrado: {full_url}")  # Debug para conferir os links
                        all_endpoints.append(full_url)
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

        # Identifica o ano e mês da consulta
        day, month, year = self.selected_date.split("-")
        year = int(year)
        month_name = calendar.month_abbr[int(month)].upper()  # Obtém o nome do mês em maiúsculas

        # Nome do arquivo JSON
        json_filename = f"controle_dou_{year}.json"

        # Carrega os dados existentes no arquivo, se houver
        if os.path.exists(json_filename):
            with open(json_filename, 'r', encoding='utf-8') as f:
                try:
                    json_data = json.load(f)
                except json.JSONDecodeError:
                    json_data = {}
        else:
            json_data = {}

        # Se o ano não estiver no JSON, inicializa com meses vazios
        if str(year) not in json_data:
            json_data[str(year)] = {m.upper(): [] for m in calendar.month_abbr if m}  # Cria meses vazios

        # Acessar cada endpoint e salvar os dados no JSON
        for idx, endpoint in enumerate(all_endpoints):
            try:
                print(f"\n[Acessando] {endpoint}")  # Confirma que estamos acessando a URL
                driver.get(endpoint)

                # Esperar que o conteúdo dinâmico seja carregado
                wait.until(EC.presence_of_element_located((By.ID, "materia")))

                time.sleep(3)  # Pequeno delay extra para garantir o carregamento completo

                # Captura do HTML atualizado com JavaScript ativado
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, "html.parser")

                # Extraindo informações da publicação
                article = soup.find("article", {"id": "materia"})

                if article:
                    # Extraindo detalhes do cabeçalho
                    data_publicacao = article.find("span", class_="publicado-dou-data").text.strip() if article.find("span", class_="publicado-dou-data") else "Data não encontrada"
                    secao = article.find("span", class_="secao-dou-data").text.strip() if article.find("span", class_="secao-dou-data") else "Seção não encontrada"
                    pagina = article.find("span", class_="secao-dou-data").text.strip() if article.find("span", class_="secao-dou-data") else "Página não encontrada"
                    orgao = article.find("span", class_="orgao-dou-data").text.strip() if article.find("span", class_="orgao-dou-data") else "Órgão não encontrado"

                    # Extraindo o conteúdo principal da matéria
                    texto_dou = article.find("div", class_="texto-dou")
                    if texto_dou:
                        texto_conteudo = "\n".join([p.get_text(strip=True) for p in texto_dou.find_all("p")])
                        titulo = texto_dou.find("p", class_="identifica").get_text(strip=True) if texto_dou.find("p", class_="identifica") else "Título não encontrado"
                    else:
                        texto_conteudo = "Conteúdo não encontrado!"
                        titulo = "Título não encontrado"

                    # Extraindo a URL da versão certificada
                    versao_certificada_tag = soup.find("a", id="versao-certificada")
                    versao_certificada_url = versao_certificada_tag["href"] if versao_certificada_tag else "Não disponível"

                    # Adicionar os dados ao JSON
                    json_data[str(year)][month_name].append({
                        "data": self.selected_date,
                        "orgao": orgao,
                        "secao": secao,
                        "pagina": pagina,
                        "titulo": titulo,
                        "conteudo": texto_conteudo,
                        "versao_certificada": versao_certificada_url
                    })

                    print(f"[SALVO] Consulta {idx + 1} adicionada ao JSON.")

            except Exception as e:
                self.update_signal.emit(f"Erro ao acessar {endpoint}: {str(e)}")
                print(f"[ERRO] {endpoint}: {str(e)}")  # Debug para erros

        driver.quit()

        # Salvar os dados no arquivo JSON
        with open(json_filename, 'w', encoding='utf-8') as f:
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

            saved_count += 1

        driver.quit()
        self.finished_signal.emit(saved_count)
 
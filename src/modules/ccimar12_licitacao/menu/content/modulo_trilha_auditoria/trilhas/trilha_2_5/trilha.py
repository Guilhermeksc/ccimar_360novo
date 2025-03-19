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
from pathlib import Path
from paths import JSON_DIR
from datetime import datetime, timedelta
import locale
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import pandas as pd

PATH_DOU_DATA = JSON_DIR / "dou_data.json"

def widget_trilha(title_text, icons):
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

            self.date_edit = QDateEdit()
            self.date_edit.setCalendarPopup(True)
            self.date_edit.setDate(QDate.currentDate())
            self.date_edit.setStyleSheet("font-size: 14px;")
            title_layout.addWidget(self.date_edit)
            title_layout.addStretch()

            # Create download link label
            self.download_link = QLabel()
            self.download_link.setOpenExternalLinks(True)
            self.download_link.hide()
            
            # Create message popup
            self.message_popup = QDialog(self)
            self.message_popup.setWindowTitle("Consultando DOU")
            popup_layout = QVBoxLayout(self.message_popup)
            self.message_label = QTextBrowser()
            popup_layout.addWidget(self.message_label)
            self.message_popup.setModal(True)

            # Add buttons
            btn_consultar = add_button_func("Consultar", "add", self.consultar_dou, title_layout, icons, tooltip="Consultar Diário Oficial da União")
            btn_verificar_mes_de_referencia = add_button_func("Exportar", "export", self.verificar_mes_de_referencia, title_layout, icons, tooltip="Selecione o mês e ano de referência")
            btn_import = add_button_func("Importar", "import", lambda: None, title_layout, icons, tooltip="Importar dados")
            btn_relatorio = add_button_func("Relatório", "report", self.gerar_relatorio, title_layout, icons, tooltip="Visualizar relatório")

            main_layout.addLayout(title_layout)
            main_layout.addWidget(self.download_link)

        def consultar_dou(self):
            selected_date = self.date_edit.date().toString("dd-MM-yyyy")
            url = f"https://www.in.gov.br/leiturajornal?secao=dou3&data={selected_date}&org=Minist%C3%A9rio%20da%20Defesa&org_sub=Comando%20da%20Marinha"

            def update_message(msg):
                self.message_label.append(msg)

            def process_result(status, num_pages):
                self.message_label.append(status)
                if num_pages:
                    self.message_label.append(f"Número de páginas encontradas: {num_pages}")
                self.message_popup.accept()

            scraper_thread = ScraperThread(url, selected_date, self.message_popup)
            scraper_thread.update_signal.connect(update_message)
            scraper_thread.result_signal.connect(process_result)
            scraper_thread.start()
            self.message_popup.exec()

        def verificar_mes_de_referencia(self):
            # Create dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Selecionar Mês e Ano de Referência")
            dialog.setModal(True)
            layout = QVBoxLayout(dialog)

            # Create month combobox
            month_label = QLabel("Mês:")
            month_combo = QComboBox()
            months = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                      "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
            month_combo.addItems(months)
            
            # Set previous month as default
            current_month = QDate.currentDate().month()
            previous_month = 11 if current_month == 1 else current_month - 1
            month_combo.setCurrentIndex(previous_month - 1)

            # Create year input
            year_label = QLabel("Ano:")
            year_edit = QLineEdit()
            year_edit.setText(str(QDate.currentDate().year()))
            # Only allow 4 digit numbers
            year_edit.setValidator(QRegularExpressionValidator(QRegularExpression("\\d{4}")))

            # Create buttons
            button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                         QDialogButtonBox.StandardButton.Cancel)
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)

            # Add widgets to layout
            layout.addWidget(month_label)
            layout.addWidget(month_combo)
            layout.addWidget(year_label)
            layout.addWidget(year_edit)
            layout.addWidget(button_box)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                selected_month = month_combo.currentText()
                selected_year = year_edit.text()
                
                # Create progress dialog
                progress_dialog = QDialog(self)
                progress_dialog.setWindowTitle("Baixando Dados")
                progress_dialog.setModal(True)
                progress_layout = QVBoxLayout(progress_dialog)
                
                status_label = QLabel("Iniciando...")
                progress_layout.addWidget(status_label)
                
                cancel_button = QPushButton("Cancelar")
                progress_layout.addWidget(cancel_button)
                
                # Create and start scraper thread
                scraper_thread = DadosAbertosScraperThread(selected_month, selected_year, progress_dialog)
                
                def update_status(msg):
                    status_label.setText(msg)
                
                def handle_finished(success, msg):
                    status_label.setText(msg)
                    if success:
                        QTimer.singleShot(2000, progress_dialog.accept)
                    else:
                        cancel_button.setText("Fechar")
                
                def cancel_download():
                    scraper_thread.stop()
                    progress_dialog.reject()
                
                cancel_button.clicked.connect(cancel_download)
                scraper_thread.update_signal.connect(update_status)
                scraper_thread.finished_signal.connect(handle_finished)
                
                scraper_thread.start()
                progress_dialog.exec()
                
                # Ensure thread is properly cleaned up
                if scraper_thread.isRunning():
                    scraper_thread.stop()
                    scraper_thread.wait()

        def gerar_relatorio(self):
            try:
                # Criar diretório para relatórios se não existir
                reports_dir = os.path.join(os.getcwd(), "reports")
                os.makedirs(reports_dir, exist_ok=True)

                # Nome dos arquivos com timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                pdf_filename = f"relatorio_publicacoes_{timestamp}.pdf"
                excel_filename = f"relatorio_publicacoes_{timestamp}.xlsx"
                pdf_filepath = os.path.join(reports_dir, pdf_filename)
                excel_filepath = os.path.join(reports_dir, excel_filename)

                # Carregar dados do JSON
                if not os.path.exists(PATH_DOU_DATA):
                    QMessageBox.warning(
                        self,
                        "Aviso",
                        "Nenhum dado encontrado. Por favor, exporte os dados primeiro."
                    )
                    return

                with open(PATH_DOU_DATA, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)

                # Criar lista para armazenar dados para o Excel
                excel_data = []

                # Processar dados para o Excel
                for year in json_data:
                    for month in json_data[year]:
                        month_data = json_data[year][month]
                        for art_type in month_data:
                            if month_data[art_type]:
                                for categoria in month_data[art_type]:
                                    items = month_data[art_type][categoria]
                                    for item in items:
                                        excel_data.append({
                                            'Ano': year,
                                            'Mês': month,
                                            'Tipo': art_type,
                                            'Categoria': categoria,
                                            'Data Publicação': item.get('pubDate', ''),
                                            'Identificação': item.get('identifica', ''),
                                            'Nº Edição': item.get('editionNumber', ''),
                                            'Link PDF': item.get('pdfPage', ''),
                                            'Texto Completo': item.get('texto_completo', '')
                                        })

                # Criar DataFrame e salvar como Excel
                df = pd.DataFrame(excel_data)
                
                # Configurar o writer do Excel com algumas formatações
                with pd.ExcelWriter(excel_filepath, engine='xlsxwriter') as writer:
                    df.to_excel(writer, sheet_name='Publicações', index=False)
                    
                    # Obter o workbook e a worksheet
                    workbook = writer.book
                    worksheet = writer.sheets['Publicações']
                    
                    # Definir formatos
                    header_format = workbook.add_format({
                        'bold': True,
                        'text_wrap': True,
                        'valign': 'top',
                        'fg_color': '#2C3E50',
                        'font_color': 'white',
                        'border': 1
                    })
                    
                    cell_format = workbook.add_format({
                        'text_wrap': True,
                        'valign': 'top',
                        'border': 1
                    })
                    
                    link_format = workbook.add_format({
                        'font_color': 'blue',
                        'underline': True,
                        'text_wrap': True,
                        'valign': 'top',
                        'border': 1
                    })
                    
                    # Aplicar formatos
                    for col_num, value in enumerate(df.columns.values):
                        worksheet.write(0, col_num, value, header_format)
                        
                    # Ajustar largura das colunas
                    worksheet.set_column('A:B', 10)  # Ano e Mês
                    worksheet.set_column('C:D', 20)  # Tipo e Categoria
                    worksheet.set_column('E:E', 15)  # Data Publicação
                    worksheet.set_column('F:F', 40)  # Identificação
                    worksheet.set_column('G:G', 12)  # Nº Edição
                    worksheet.set_column('H:H', 50)  # Link PDF
                    worksheet.set_column('I:I', 100)  # Texto Completo
                    
                    # Aplicar formato para todas as células de dados
                    for row in range(1, len(df) + 1):
                        for col in range(len(df.columns)):
                            if df.columns[col] == 'Link PDF':
                                # Para links, usar formato especial
                                url = df.iloc[row-1]['Link PDF']
                                if url:
                                    worksheet.write_url(row, col, url, link_format, '📄 Visualizar')
                            else:
                                worksheet.write(row, col, df.iloc[row-1][df.columns[col]], cell_format)

                # Configurar documento PDF
                doc = SimpleDocTemplate(
                    pdf_filepath,
                    pagesize=A4,
                    rightMargin=72,
                    leftMargin=72,
                    topMargin=72,
                    bottomMargin=72
                )

                # Estilos
                styles = getSampleStyleSheet()
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=24,
                    spaceAfter=30,
                    alignment=1  # Centralizado
                )
                heading_style = ParagraphStyle(
                    'CustomHeading',
                    parent=styles['Heading2'],
                    fontSize=16,
                    spaceAfter=12,
                    textColor=colors.HexColor('#2C3E50')
                )
                normal_style = ParagraphStyle(
                    'CustomNormal',
                    parent=styles['Normal'],
                    fontSize=10,
                    leading=14,
                    alignment=4,  # Justificado (4 = TA_JUSTIFY)
                    spaceAfter=10
                )
                link_style = ParagraphStyle(
                    'LinkStyle',
                    parent=styles['Normal'],
                    fontSize=8,
                    textColor=colors.HexColor('#2980b9'),
                    underline=True
                )
                subtitle_style = ParagraphStyle(
                    'CustomSubtitle',
                    parent=styles['Heading2'],
                    fontSize=14,
                    spaceAfter=20,
                    alignment=1
                )

                # Conteúdo do PDF
                elements = []

                # Título
                elements.append(Paragraph("Relatório de Publicações do DOU", title_style))
                elements.append(Spacer(1, 20))

                # Subtítulo com data
                data_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
                elements.append(Paragraph(f"Gerado em {data_geracao}", subtitle_style))
                elements.append(Spacer(1, 30))

                # Processar dados do JSON
                for year in json_data:
                    for month in json_data[year]:
                        month_data = json_data[year][month]
                        if month_data:  # Se houver dados para o mês
                            elements.append(Paragraph(f"Mês: {month}/{year}", heading_style))
                            elements.append(Spacer(1, 10))

                            for art_type in month_data:
                                if month_data[art_type]:  # Se houver dados para o tipo
                                    elements.append(Paragraph(f"Tipo: {art_type}", heading_style))
                                    elements.append(Spacer(1, 5))

                                    for categoria in month_data[art_type]:
                                        items = month_data[art_type][categoria]
                                        if items:  # Se houver itens na categoria
                                            elements.append(Paragraph(f"Categoria: {categoria}", heading_style))
                                            elements.append(Spacer(1, 5))

                                            # Criar tabela para os itens
                                            table_data = [['Data', 'Identificação', 'Nº Edição', 'Link PDF']]  # Cabeçalho
                                            for item in items:
                                                pdf_url = item.get('pdfPage', '')
                                                pdf_link = Paragraph(f'<link href="{pdf_url}">📄 Visualizar</link>', link_style) if pdf_url else ''
                                                
                                                row = [
                                                    item.get('pubDate', ''),
                                                    item.get('identifica', ''),
                                                    item.get('editionNumber', ''),
                                                    pdf_link
                                                ]
                                                table_data.append(row)

                                            # Estilo da tabela
                                            table = Table(table_data, colWidths=[80, 300, 60, 70])
                                            table.setStyle(TableStyle([
                                                # Estilo do cabeçalho
                                                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),
                                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                                ('FONTSIZE', (0, 0), (-1, 0), 10),
                                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                                
                                                # Estilo do corpo da tabela
                                                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                                                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                                                ('FONTSIZE', (0, 1), (-1, -1), 8),
                                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                                
                                                # Linhas alternadas
                                                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')])
                                            ]))

                                            elements.append(table)
                                            elements.append(Spacer(1, 20))

                                            # Adicionar detalhes completos de cada item
                                            for item in items:
                                                if item.get('texto_completo'):
                                                    # Substituir quebras de linha do JSON por tags <br/>
                                                    texto_formatado = item['texto_completo'].replace('\n', '<br/>')
                                                    elements.append(Paragraph(
                                                        f"<b>Detalhes da publicação:</b><br/>{texto_formatado}", 
                                                        normal_style
                                                    ))
                                                    elements.append(Spacer(1, 10))

                # Gerar PDF
                doc.build(elements)

                # Criar link de download para ambos os arquivos
                pdf_url = QUrl.fromLocalFile(pdf_filepath).toString()
                excel_url = QUrl.fromLocalFile(excel_filepath).toString()
                
                self.download_link.setText(
                    f'<div style="font-size: 14px; font-weight: bold;">'
                    f'<p><a href="{pdf_url}" style="color: #2980b9; text-decoration: none;">📥 Clique aqui para baixar o relatório PDF</a></p>'
                    f'<p><a href="{excel_url}" style="color: #27ae60; text-decoration: none;">📊 Clique aqui para baixar a planilha Excel</a></p>'
                    f'</div>'
                )
                self.download_link.show()

                # Mensagem de sucesso
                QMessageBox.information(
                    self,
                    "Sucesso",
                    "Relatório PDF e planilha Excel gerados com sucesso!\nClique nos links abaixo da tabela para baixar."
                )

            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Erro",
                    f"Erro ao gerar relatório: {str(e)}"
                )

    # Create and return instance of TrilhaWidget
    return TrilhaWidget(title_text, icons)

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

class DadosAbertosScraperThread(QThread):
    update_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, month, year, parent=None):
        super().__init__(parent)
        self.month = month
        self.year = year
        self.driver = None
        self.is_running = True

    def stop(self):
        self.is_running = False
        try:
            if self.driver:
                self.driver.quit()
        except Exception:
            pass  # Ignore errors during cleanup

    def run(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Firefox(options=options)
        
        try:
            # Navigate to the page
            self.update_signal.emit("Acessando página de dados abertos...")
            self.driver.get("https://www.in.gov.br/acesso-a-informacao/dados-abertos/base-de-dados")
            
            if not self.is_running:
                return

            # Wait for year select to be present and interactable
            wait = WebDriverWait(self.driver, 20)
            self.update_signal.emit("Aguardando carregamento do seletor de ano...")
            year_select = wait.until(
                EC.element_to_be_clickable((By.ID, "ano-dados"))
            )
            
            # Get available years first
            year_options = year_select.find_elements(By.TAG_NAME, "option")
            available_years = [opt.text.strip() for opt in year_options if opt.text.strip() and opt.text.strip() != "Selecione"]
            
            if not available_years:
                self.finished_signal.emit(False, "Não foi possível encontrar anos disponíveis")
                return
                
            if self.year not in available_years:
                self.finished_signal.emit(False, f"O ano {self.year} não está disponível. Anos disponíveis: {', '.join(available_years)}")
                return

            # Select the year
            self.update_signal.emit(f"Selecionando ano {self.year}...")
            year_select.click()
            time.sleep(1)  # Wait for dropdown to open
            
            # Try different methods to select the year
            try:
                # Try by xpath first
                year_option = self.driver.find_element(By.XPATH, f"//select[@id='ano-dados']/option[text()='{self.year}']")
                year_option.click()
            except:
                # If xpath fails, try selecting by value
                for option in year_options:
                    if option.text.strip() == self.year:
                        option.click()
                        break
            
            if not self.is_running:
                return

            # Wait for month select to be populated and clickable
            self.update_signal.emit("Aguardando carregamento dos meses...")
            time.sleep(2)  # Give extra time for JavaScript to update
            month_select = wait.until(
                EC.element_to_be_clickable((By.ID, "mes-dados"))
            )
            
            # Get available months
            month_options = month_select.find_elements(By.TAG_NAME, "option")
            available_months = [opt.text.strip() for opt in month_options if opt.text.strip() and opt.text.strip() != "Selecione"]
            
            if not available_months:
                self.finished_signal.emit(False, "Não foi possível encontrar meses disponíveis")
                return
                
            if self.month not in available_months:
                self.finished_signal.emit(False, f"O mês {self.month} não está disponível. Meses disponíveis: {', '.join(available_months)}")
                return

            # Select the month
            self.update_signal.emit(f"Selecionando mês {self.month}...")
            month_select.click()
            time.sleep(1)  # Wait for dropdown to open
            
            try:
                month_option = self.driver.find_element(By.XPATH, f"//select[@id='mes-dados']/option[text()='{self.month}']")
                month_option.click()
            except:
                for option in month_options:
                    if option.text.strip() == self.month:
                        option.click()
                        break

            if not self.is_running:
                return

            # After selecting month, wait for page to update
            self.update_signal.emit("Aguardando carregamento da lista de arquivos...")
            time.sleep(3)  # Initial wait for JavaScript

            try:
                # Wait for the list to be present and try multiple times if needed
                max_attempts = 5
                attempt = 0
                download_list = None
                
                while attempt < max_attempts and not download_list and self.is_running:
                    try:
                        download_list = wait.until(
                            EC.presence_of_element_located((By.CLASS_NAME, "dados-abertos-lista"))
                        )
                        self.update_signal.emit("Lista de arquivos encontrada!")
                    except:
                        attempt += 1
                        self.update_signal.emit(f"Tentativa {attempt} de {max_attempts}...")
                        time.sleep(2)
                
                if not download_list:
                    self.finished_signal.emit(False, "Não foi possível carregar a lista de arquivos")
                    return

                links = download_list.find_elements(By.TAG_NAME, "a")
                if not links:
                    self.finished_signal.emit(False, "Nenhum arquivo encontrado para download")
                    return

                # Get desktop path
                desktop_path = str(Path.home() / "Desktop")
                
                # Verificar se arquivo S03 já existe
                existing_files = [f for f in os.listdir(desktop_path) if f.startswith('S03') and f.endswith('.zip')]
                
                if existing_files:
                    print(f"\nArquivo S03 encontrado: {existing_files[0]}")
                    file_path = os.path.join(desktop_path, existing_files[0])
                else:
                    # Process links and look for S03 file
                    for link in links:
                        if not self.is_running:
                            return
                        
                        url = link.get_attribute("href")
                        filename = link.text.strip()
                        
                        # Only process S03 files
                        if not filename.startswith("S03"):
                            continue
                        
                        print(f"\nBaixando arquivo: {filename}")
                        print(f"URL do arquivo: {url}")
                        
                        file_path = os.path.join(desktop_path, filename)
                        self.update_signal.emit(f"Baixando {filename}...")
                        
                        try:
                            import requests
                            headers = {
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                            }
                            
                            response = requests.get(url, headers=headers, stream=True, timeout=30)
                            response.raise_for_status()
                            
                            with open(file_path, 'wb') as f:
                                for chunk in response.iter_content(chunk_size=8192):
                                    if chunk:
                                        f.write(chunk)
                            
                            print(f"Download concluído: {filename}")
                            break  # Sai do loop após encontrar e baixar o arquivo S03
                            
                        except Exception as e:
                            print(f"Erro ao baixar {filename}: {str(e)}")
                            continue

                # Continua com o processamento do arquivo ZIP
                if os.path.exists(file_path):
                    print(f"\nProcessando arquivo ZIP: {os.path.basename(file_path)}")
                    
                    import zipfile
                    import xml.etree.ElementTree as ET
                    import json
                    from datetime import datetime
                    import re
                    
                    # Preparar estrutura do JSON
                    json_data = {
                        "2025": {
                            "JAN": {},  # Será preenchido com artType dinamicamente
                            "FEV": {},
                            "MAR": {},
                            "ABR": {},
                            "MAI": {},
                            "JUN": {},
                            "JUL": {},
                            "AGO": {},
                            "SET": {},
                            "OUT": {},
                            "NOV": {},
                            "DEZ": {}
                        }
                    }
                    
                    def extract_cdata_content(text):
                        if text:
                            match = re.search(r'<!\[CDATA\[(.*?)\]\]>', text, re.DOTALL)
                            if match:
                                return match.group(1).strip()
                        return ""
                    
                    # Processar arquivo ZIP
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        xml_files = [f for f in zip_ref.namelist() if f.endswith('.xml')]
                        total_files = len(xml_files)
                        print(f"\nTotal de arquivos XML encontrados: {total_files}")
                        
                        for index, xml_file in enumerate(xml_files, 1):
                            self.update_signal.emit(f"Processando arquivo {index}/{total_files}")
                            
                            try:
                                with zip_ref.open(xml_file) as xml_content:
                                    content = xml_content.read().decode('utf-8')
                                    root = ET.fromstring(content)
                                    
                                    # Procurar pelo elemento article
                                    articles = root.findall('article')
                                    
                                    for article in articles:
                                        # Verificar artCategory
                                        art_category = article.get('artCategory', '')
                                        
                                        # Se for da Marinha, processa
                                        if "Comando da Marinha" in art_category:
                                            # Pegar apenas a última parte do artCategory
                                            categoria_simplificada = art_category.split('/')[-1].strip()
                                            
                                            art_type = article.get('artType', '')
                                            # Verificar ambas as exceções
                                            if 'Edital de Concurso Público' in art_type or 'Edital de Processo Seletivo' in art_type:
                                                print(f"Ignorado - {art_type}")
                                                continue
                                                
                                            pub_date = article.get('pubDate', '')
                                            print(f"\nArquivo: {xml_file}")
                                            print(f"Categoria Original: {art_category}")
                                            print(f"Categoria Simplificada: {categoria_simplificada}")
                                            print(f"Data de publicação: {pub_date}")
                                            print(f"Tipo: {art_type}")
                                            
                                            try:
                                                # Obter o mês diretamente da data (DD/MM/YYYY)
                                                _, month, _ = pub_date.split('/')
                                                month = int(month)
                                                
                                                # Mapeamento direto dos meses
                                                month_map = {
                                                    1: 'JAN', 2: 'FEV', 3: 'MAR', 4: 'ABR',
                                                    5: 'MAI', 6: 'JUN', 7: 'JUL', 8: 'AGO',
                                                    9: 'SET', 10: 'OUT', 11: 'NOV', 12: 'DEZ'
                                                }
                                                
                                                month_abbr = month_map[month]
                                                formatted_date = pub_date.replace('/', '-')
                                                
                                                print(f"Mês processado: {month_abbr}")
                                                
                                                # Extrair conteúdo CDATA
                                                body = article.find('body')
                                                print("\n=== Debug do Body ===")
                                                print(f"Body encontrado: {body}")
                                                
                                                if body is not None:
                                                    identifica = body.find('Identifica')
                                                    identifica_text = identifica.text.strip() if identifica is not None else ""
                                                    identifica_text = identifica_text.replace('<![CDATA[', '').replace(']]>', '').strip()
                                                    
                                                    texto = body.find('Texto')
                                                    if texto is not None and texto.text:
                                                        # Limpar o CDATA e extrair o texto
                                                        texto_raw = texto.text.replace('<![CDATA[', '').replace(']]>', '').strip()
                                                        
                                                        # Usar BeautifulSoup para processar o HTML
                                                        soup = BeautifulSoup(texto_raw, 'html.parser')
                                                        
                                                        # Extrair todos os parágrafos
                                                        paragrafos = []
                                                        for p in soup.find_all('p'):
                                                            texto_p = p.get_text().strip()
                                                            paragrafos.append(texto_p)
                                                        
                                                        # Juntar os parágrafos em um texto
                                                        texto_completo = "\n".join(paragrafos)
                                                        print(f"\nTexto processado:")
                                                        print(texto_completo)
                                                    else:
                                                        texto_completo = ""
                                                else:
                                                    identifica_text = ""
                                                    texto_completo = ""
                                                
                                                # Criar item para o JSON (versão simplificada)
                                                item = {
                                                    "name": article.get('name', ''),
                                                    "artType": art_type,
                                                    "pubDate": pub_date,
                                                    "pdfPage": article.get('pdfPage', ''),
                                                    "editionNumber": article.get('editionNumber', ''),
                                                    "idMateria": article.get('idMateria', ''),
                                                    "identifica": identifica_text,
                                                    "texto_completo": texto_completo
                                                }

                                                # Organizar no JSON hierarquicamente usando a categoria simplificada
                                                month_data = json_data["2025"][month_abbr]
                                                
                                                # Criar estrutura se não existir
                                                if art_type not in month_data:
                                                    month_data[art_type] = {}
                                                
                                                if categoria_simplificada not in month_data[art_type]:
                                                    month_data[art_type][categoria_simplificada] = []
                                                
                                                # Adicionar item
                                                month_data[art_type][categoria_simplificada].append(item)
                                                
                                                print(f"\nItem adicionado:")
                                                print(f"Mês: {month_abbr}")
                                                print(f"Tipo: {art_type}")
                                                print(f"Categoria: {categoria_simplificada}")
                                                print("-" * 50)

                                            except Exception as e:
                                                print(f"Erro ao processar item: {str(e)}")
                                                print(f"Detalhes do erro para debug:")
                                                print(f"Mês numérico: {month}")
                                                print(f"Mês abreviado: {month_abbr}")
                                                print(f"Estrutura JSON atual: {list(json_data['2025'].keys())}")
                                                continue
                            
                            except Exception as e:
                                print(f"Erro ao processar XML {xml_file}: {str(e)}")
                                continue
                    
                    # Salvar JSON
                    with open(PATH_DOU_DATA, 'w', encoding='utf-8') as f:
                        json.dump(json_data, f, ensure_ascii=False, indent=4)
                    
                    # Após salvar o JSON, antes de finalizar
                    print(f"\nProcessamento concluído!")
                    print(f"Arquivo JSON salvo em: {PATH_DOU_DATA}")
                    
                    # Contagem de itens por mês
                    print("\nItens encontrados por mês:")
                    total_items = 0
                    for month, items in json_data["2025"].items():
                        count = len(items)
                        total_items += count
                        if count > 0:
                            print(f"{month}: {count} itens")
                    
                    print(f"\nTotal de itens salvos: {total_items}")
                    
                    # Fechar o driver corretamente
                    try:
                        if self.driver:
                            print("\nFechando o navegador...")
                            self.driver.close()
                            time.sleep(1)  # Pequena pausa
                            self.driver.quit()
                            self.driver = None
                            print("Navegador fechado com sucesso!")
                    except Exception as e:
                        print(f"Aviso: Erro ao fechar o navegador: {str(e)}")
                    
                self.finished_signal.emit(True, "Processamento concluído")
                
            except Exception as e:
                self.finished_signal.emit(False, f"Erro: {str(e)}")
                print(f"Erro detalhado: {str(e)}")
                # Garantir que o driver seja fechado mesmo em caso de erro
                try:
                    if self.driver:
                        self.driver.quit()
                        self.driver = None
                except:
                    pass
                
        except Exception as e:
            self.finished_signal.emit(False, f"Erro durante o processo: {str(e)}")
        finally:
            try:
                # Properly close the browser
                if self.driver:
                    self.driver.close()  # Close the current window first
                    time.sleep(1)  # Give it a moment
                    self.driver.quit()  # Then quit the browser
            except Exception:
                pass  # Ignore cleanup errors
            self.driver = None  # Clear the reference

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
 
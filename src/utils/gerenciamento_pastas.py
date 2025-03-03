from PyQt6.QtWidgets import QFileDialog, QMessageBox
import os
import subprocess
from docx import Document
import shutil
from docxtpl import DocxTemplate

# Helper functions for button actions
def open_folder(folder_name):
    """Opens the specified folder on the desktop."""
    if not folder_name:
        QMessageBox.warning(None, "Aviso", "Digite um nome para a pasta.")
        return

    folder_path = os.path.join(os.path.expanduser("~/Desktop"), folder_name)
    if os.path.exists(folder_path):
        try:
            if os.name == "nt":  # Windows
                os.startfile(folder_path)
            elif os.name == "posix":  # Linux/Mac
                subprocess.run(["xdg-open", folder_path])
        except Exception as e:
            QMessageBox.critical(None, "Erro", f"Erro ao abrir a pasta: {e}")
    else:
        QMessageBox.warning(None, "Erro", "A pasta não existe.")


def open_template():
    """Opens a file selection dialog for the user to choose a template."""
    file_path, _ = QFileDialog.getOpenFileName(None, "Selecionar Template", "", "Documentos (*.docx *.pdf)")
    if file_path:
        try:
            os.startfile(file_path)
        except Exception as e:
            QMessageBox.critical(None, "Erro", f"Erro ao abrir o arquivo: {e}")


def criar_pasta(folder_name):
    """Creates a folder on the desktop."""
    if not folder_name:
        QMessageBox.warning(None, "Aviso", "Digite um nome para a pasta.")
        return

    folder_path = os.path.join(os.path.expanduser("~/Desktop"), folder_name)
    os.makedirs(folder_path, exist_ok=True)
    
    try:
        if os.name == "nt":  # Windows
            os.startfile(folder_path)
        elif os.name == "posix":  # Linux/Mac
            subprocess.run(["xdg-open", folder_path])
    except Exception as e:
        QMessageBox.critical(None, "Erro", f"Erro ao abrir a pasta: {e}")

def criar_pasta_e_docx(folder_name, template_path, setor_responsavel, natalia):
    """
    Cria uma pasta no desktop e gera um arquivo DOCX baseado no template fornecido,
    mantendo a formatação original do documento.
    """
    if not folder_name:
        QMessageBox.warning(None, "Aviso", "Digite um nome para a pasta.")
        return
    
    # Caminho da pasta no Desktop
    folder_path = os.path.join(os.path.expanduser("~/Desktop"), folder_name)
    os.makedirs(folder_path, exist_ok=True)
    
    # Caminho do novo arquivo DOCX
    new_docx_path = os.path.join(folder_path, f"{folder_name}.docx")
    
    try:
        # Copiar o template para o novo local
        shutil.copy(template_path, new_docx_path)
        
        # Carregar o template
        doc = DocxTemplate(new_docx_path)
        
        # Dicionário de variáveis a serem substituídas
        variaveis = {
            "setor_responsavel": setor_responsavel,
            "natalia": natalia
        }
        
        # Renderizar o template
        doc.render(variaveis)
        
        # Salvar o documento modificado
        doc.save(new_docx_path)
        
        QMessageBox.information(None, "Sucesso", "Pasta e arquivo DOCX criados com sucesso!")
    
    except Exception as e:
        QMessageBox.critical(None, "Erro", f"Erro ao criar o arquivo DOCX: {e}")
    
    # Abrir a pasta após a criação
    try:
        if os.name == "nt":  # Windows
            os.startfile(folder_path)
        elif os.name == "posix":  # Linux/Mac
            subprocess.run(["xdg-open", folder_path])
    except Exception as e:
        QMessageBox.critical(None, "Erro", f"Erro ao abrir a pasta: {e}")



def criar_pasta_e_pdf(folder_name):
    """Creates a folder, generates a DOCX, and converts it to PDF."""
    criar_pasta_e_docx(folder_name, "", "")
    folder_path = os.path.join(os.path.expanduser("~/Desktop"), folder_name)

    if not folder_name:
        return

    docx_path = os.path.join(folder_path, "documento.docx")
    pdf_path = os.path.join(folder_path, "documento.pdf")

    # Convert DOCX to PDF (Requires LibreOffice)
    try:
        os.system(f'libreoffice --headless --convert-to pdf "{docx_path}" --outdir "{folder_path}"')
        QMessageBox.information(None, "Sucesso", "Arquivo PDF criado com sucesso.")
    except Exception as e:
        QMessageBox.critical(None, "Erro", f"Erro ao converter para PDF: {e}")
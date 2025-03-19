import os
import email
import imaplib
from dotenv import load_dotenv

# Carregar credenciais do arquivo .env
load_dotenv()

EMAIL_USER = "auditaccimar@gmail.com"
EMAIL_PASSWORD = "tvox kgdf xpdg mevx"
IMAP_SERVER = "imap.gmail.com"

def get_latest_email_attachment():
    try:
        # Conectar ao Gmail via IMAP
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASSWORD)
        mail.select("inbox")  # Acessar a Caixa de Entrada

        # Buscar o e-mail mais recente
        result, data = mail.search(None, "ALL")
        email_ids = data[0].split()
        if not email_ids:
            print("Nenhum e-mail encontrado.")
            return
        
        latest_email_id = email_ids[-1]  # Último e-mail recebido

        # Obter os dados do e-mail
        result, data = mail.fetch(latest_email_id, "(RFC822)")
        raw_email = data[0][1]

        # Decodificar o e-mail
        msg = email.message_from_bytes(raw_email)
        subject = msg["Subject"]
        print(f"Último e-mail recebido: {subject}")

        # Verificar e baixar anexos
        for part in msg.walk():
            if part.get_content_maintype() == "multipart":
                continue
            if part.get("Content-Disposition") is None:
                continue

            filename = part.get_filename()
            if filename:
                filepath = os.path.join(os.getcwd(), filename)
                with open(filepath, "wb") as f:
                    f.write(part.get_payload(decode=True))
                print(f"Anexo baixado: {filepath}")

        mail.logout()
    except Exception as e:
        print(f"Erro: {e}")

# Executar a função
get_latest_email_attachment()

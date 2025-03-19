import smtplib

server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
server.login("auditaccimar@gmail.com", "SENHA_DE_APP")
print("✅ Conectado ao SMTP!")
server.quit()

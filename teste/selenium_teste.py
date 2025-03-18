from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Caminho correto do chromedriver
CHROMEDRIVER_PATH = "/usr/local/bin/chromedriver"

# Configuração do Chrome
chrome_options = Options()
#chrome_options.add_argument("--headless")  # Executa sem interface gráfica (remova se quiser ver a janela)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Inicializa o WebDriver corretamente
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Acesse o Google
driver.get("https://www.google.com")

# Espere a página carregar (opcional)
driver.implicitly_wait(5)

# Tente obter o título da página
print("Título da página:", driver.title)

# Debug: Mostra o HTML da página para verificar se carregou corretamente
print("HTML da página:", driver.page_source[:500])  # Mostra os primeiros 500 caracteres

# Fecha o navegador
driver.quit()

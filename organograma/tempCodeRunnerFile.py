import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_organograma(url):
    print("Inicializando WebDriver para a URL:", url)
    options = Options()
    options.add_argument("--headless")  # Executa em modo headless
    options.add_argument("--ignore-certificate-errors")  # Ignora erros de certificado SSL
    options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=options)
    print("Acessando a página...")
    driver.get(url)
    
    print("Aguardando o carregamento do conteúdo via JavaScript...")
    try:
        wait = WebDriverWait(driver, 20)
        # Aguarda até que elementos com a classe "node-card__info" estejam presentes
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "node-card__info")))
        print("Conteúdo carregado!")
    except Exception as e:
        print("Erro ao aguardar o carregamento do conteúdo:", e)
    
    nodes = driver.find_elements(By.CLASS_NAME, "node-card__info")
    print(f"Foram encontrados {len(nodes)} elementos com a classe 'node-card__info'.")
    
    resultados = []
    for index, node in enumerate(nodes, start=1):
        print(f"\nProcessando item {index}:")
        try:
            sigla = node.find_element(By.CLASS_NAME, "node-card__sigla").text.strip()
            print("Sigla encontrada:", sigla)
        except Exception as e:
            sigla = None
            print("Erro ao extrair sigla:", e)
            
        try:
            posicao = node.find_element(By.CLASS_NAME, "node-card__position").text.strip()
            print("Posição encontrada:", posicao)
        except Exception as e:
            posicao = None
            print("Erro ao extrair posição:", e)
        
        item = {"sigla": sigla, "position": posicao}
        print("Dados extraídos:", item)
        resultados.append(item)
    
    driver.quit()
    print("\nExtração concluída. Total de itens extraídos:", len(resultados))
    return resultados

if __name__ == "__main__":
    url = "https://catalogo.prod.dadm.mb/organograma"
    dados = scrape_organograma(url)
    print("\nItens extraídos:")
    for item in dados:
        print(item)

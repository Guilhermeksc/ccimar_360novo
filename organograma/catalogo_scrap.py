from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

url = "https://catalogo.prod.dadm.mb/om/379"
print("Inicializando WebDriver para a URL:", url)

options = Options()
options.add_argument("--headless")  # Modo headless
options.add_argument("--ignore-certificate-errors")
options.add_argument("--disable-gpu")

driver = webdriver.Chrome(options=options)
resultados = []

try:
    driver.get(url)
    wait = WebDriverWait(driver, 20)

    # Aguarda e clica na aba "OM SUBORDINADAS"
    tab = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//span[contains(text(),'OM SUBORDINADAS')]")
    ))
    tab.click()

    # Aguarda os elementos que contenham o ícone "arrow_circle_right"
    elementos = wait.until(EC.presence_of_all_elements_located(
        (By.XPATH, "//span[.//mat-icon[text()='arrow_circle_right']]")
    ))

    for idx, elem in enumerate(elementos, start=1):
        texto = elem.text.strip()  # Ex: "arrow_circle_right 91800 - BNRJ - BASE NAVAL DO RIO DE JANEIRO"
        partes = texto.split(" ", 1)  # Separa o ícone do restante
        if len(partes) == 2:
            # Ignora o ícone e processa o restante
            restante = partes[1]
            dados = restante.split(" - ", 2)  # Separa uasg, sigla e nome
            if len(dados) == 3:
                uasg, sigla, nome = dados
                url_item = f"https://catalogo.prod.dadm.mb/om/{uasg}"
                resultados.append({
                    "uasg": uasg,
                    "sigla": sigla,
                    "nome": nome,
                    "url": url_item
                })
            else:
                print(f"Formato inesperado no elemento {idx}: {restante}")
        else:
            print(f"Formato inesperado no elemento {idx}: {texto}")

    # Salva os resultados no arquivo JSON
    with open("resultado.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=4)
    print("Resultado salvo em resultado.json")

except Exception as e:
    print("Erro durante a execução:", e)
finally:
    driver.quit()

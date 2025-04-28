from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

# Relação de OM's
relacao_om = {
    "Com1ºDN": "362",
    "Com2ºDN": "95",
    "Com3ºDN": "116",
    "Com4ºDN": "140",
    "Com5ºDN": "153",
    "Com6ºDN": "190",
    "Com7ºDN": "314"
    # "Com8ºDN": "",
    # "Com9ºDN": ""
}

options = Options()
options.add_argument("--headless")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--disable-gpu")

driver = webdriver.Chrome(options=options)
resultados = {}

try:
    for om, uasg in relacao_om.items():
        url_item = f"https://catalogo.prod.dadm.mb/om/{uasg}"
        print("Inicializando WebDriver para a URL:", url_item)
        driver.get(url_item)
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

        lista_om = []
        for idx, elem in enumerate(elementos, start=1):
            texto = elem.text.strip()
            partes = texto.split(" ", 1)
            if len(partes) == 2:
                restante = partes[1]
                dados = restante.split(" - ", 2)
                if len(dados) == 3:
                    uasg_sub, sigla, nome = dados
                    url_sub_item = f"https://catalogo.prod.dadm.mb/om/{uasg_sub}"
                    lista_om.append({
                        "uasg": uasg_sub,
                        "sigla": sigla,
                        "nome": nome,
                        "url": url_sub_item
                    })
                else:
                    print(f"Formato inesperado no elemento {idx}: {restante}")
            else:
                print(f"Formato inesperado no elemento {idx}: {texto}")

        resultados[om] = lista_om

    # Salva os resultados no arquivo JSON
    with open("resultado.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=4)
    print("Resultado salvo em resultado.json")

except Exception as e:
    print("Erro durante a execução:", e)
finally:
    driver.quit()

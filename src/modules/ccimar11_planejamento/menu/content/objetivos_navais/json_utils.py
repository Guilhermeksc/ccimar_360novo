import json

def load_objetivos_navais_data(json_file_path):
    """
    Carrega os dados do arquivo JSON contendo a estrutura dos objetivos navais.
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Erro ao carregar o arquivo JSON: {e}")
        return None

def save_objetivos_navais_data(data, json_file_path):
    """
    Salva os dados no arquivo JSON.
    """
    try:
        with open(json_file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erro ao salvar o arquivo JSON: {e}")
        return False
"""
Módulo para persistência de dados dos objetos auditáveis.

Este módulo contém funções para carregar e salvar dados relacionados aos objetos auditáveis,
incluindo multiplicadores e critérios.
"""

import os
import json
from pathlib import Path
from paths import CONFIG_PAINT_PATH

def load_multiplicadores():
    """
    Carrega os multiplicadores do arquivo de configuração.
    
    Returns:
        tuple: (materialidade, relevancia, criticidade) com os valores dos multiplicadores
    """
    try:
        if os.path.exists(CONFIG_PAINT_PATH):
            with open(CONFIG_PAINT_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Verificar se a configuração de multiplicadores existe
            if 'multiplicadores' in config:
                return (
                    config['multiplicadores'].get('materialidade', 4),
                    config['multiplicadores'].get('relevancia', 2),
                    config['multiplicadores'].get('criticidade', 4)
                )
        
        # Se o arquivo não existir ou não tiver a configuração, retornar valores padrão
        return 4, 2, 4
    except Exception as e:
        print(f"Erro ao carregar multiplicadores: {e}")
        return 4, 2, 4

def save_multiplicadores(materialidade, relevancia, criticidade):
    """
    Salva os multiplicadores no arquivo de configuração.
    
    Args:
        materialidade (int): Peso da materialidade
        relevancia (int): Peso da relevância
        criticidade (int): Peso da criticidade
    """
    try:
        # Carregar configuração existente ou criar nova
        config = {}
        if os.path.exists(CONFIG_PAINT_PATH):
            with open(CONFIG_PAINT_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
        
        # Atualizar ou criar a configuração de multiplicadores
        if 'multiplicadores' not in config:
            config['multiplicadores'] = {}
            
        config['multiplicadores']['materialidade'] = materialidade
        config['multiplicadores']['relevancia'] = relevancia
        config['multiplicadores']['criticidade'] = criticidade
        
        # Salvar a configuração atualizada
        with open(CONFIG_PAINT_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
            
    except Exception as e:
        print(f"Erro ao salvar multiplicadores: {e}")

def load_objetos_criterios():
    """
    Carrega os critérios dos objetos auditáveis do arquivo JSON.
    
    Returns:
        dict: Dicionário com os critérios dos objetos auditáveis
    """
    try:
        if os.path.exists(CONFIG_PAINT_PATH):
            with open(CONFIG_PAINT_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Erro ao carregar critérios dos objetos: {e}")
        return {}

def save_objetos_criterios(criterios_data):
    """
    Salva os critérios dos objetos auditáveis no arquivo JSON.
    
    Args:
        criterios_data (dict): Dicionário com os critérios dos objetos auditáveis
    """
    try:
        with open(CONFIG_PAINT_PATH, 'w', encoding='utf-8') as f:
            json.dump(criterios_data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao salvar critérios dos objetos: {e}")

def update_objeto_criterios(objeto_id, criterios):
    """
    Atualiza os critérios de um objeto auditável específico.
    
    Args:
        objeto_id (str): ID do objeto auditável
        criterios (dict): Dicionário com os critérios do objeto
    """
    try:
        # Carregar dados existentes
        criterios_data = load_objetos_criterios()
        
        # Atualizar ou adicionar os critérios do objeto
        criterios_data[objeto_id] = criterios
        
        # Salvar os dados atualizados
        save_objetos_criterios(criterios_data)
    except Exception as e:
        print(f"Erro ao atualizar critérios do objeto {objeto_id}: {e}")

def get_objeto_criterios(objeto_id):
    """
    Obtém os critérios de um objeto auditável específico.
    
    Args:
        objeto_id (str): ID do objeto auditável
        
    Returns:
        dict: Dicionário com os critérios do objeto ou None se não encontrado
    """
    criterios_data = load_objetos_criterios()
    return criterios_data.get(objeto_id)
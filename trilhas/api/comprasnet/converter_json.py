import csv
import json

def convert_csv_to_json(csv_path: str, json_path: str) -> None:
    data = []
    areaom_mapping = {
        "PRIMEIRO DN": "Com1ºDN",
        "SEGUNDO DN": "Com2ºDN",
        "TERCEIRO DN": "Com3ºDN",
        "QUARTO DN": "Com4ºDN",
        "QUINTO DN": "Com5ºDN",
        "SEXTO DN": "Com6ºDN",
        "SÉTIMO DN": "Com7ºDN",
        "OITAVO DN": "Com8ºDN",
        "NONO DN": "Com9ºDN"
    }
    with open(csv_path, mode='r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file, delimiter='|', quotechar='"')
        reader.fieldnames = [field.strip('"') for field in reader.fieldnames]
        for row in reader:
            row = {k: v.strip().strip('"') for k, v in row.items()}
            comimsup_str = row.get("COD_OM_COMIMSUP", "").strip()
            if comimsup_str.endswith(".0"):
                comimsup_str = comimsup_str[:-2]
            distrito_val = areaom_mapping.get(row.get("AREAOM", ""), row.get("AREAOM", ""))
            item = {
                "uasg": int(row["UASG"]),
                "id_audcont": int(row["CODOM"]),
                "id_pagamento": 0,
                "nome_om": row["NOMEOM"],
                "indicativo_om": row["INDICATIVOOM"],
                "sigla_om": row["SIGLAOM"],
                "uf": row["UF"],
                "distrito": distrito_val,
                "ods": "",
                "comimsup": comimsup_str,
                "oc": False,
                "of": False,
                "omps": False,
                "situacao": bool(int(row["SITUACAO"]))
            }
            data.append(item)
    with open(json_path, mode='w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    convert_csv_to_json("om_ativa.csv", "om_ativa.json")

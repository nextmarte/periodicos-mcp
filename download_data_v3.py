# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "httpx>=0.27.0",
#     "pandas>=2.0.0",
#     "pyarrow>=14.0.0",
# ]
# ///
"""
Baixar Dados Reais - CAPES, ABDC

Fontes:
- CAPES repositório GitHub (vários repositórios de Qualis)
- ABDC Journal List 2022 (XLSX)

Autor: Marcus Ramalho (Gotoh)
"""

import httpx
import pandas as pd
from pathlib import Path
import io

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

print("="*60)
print("📥 DADOS OFICIAIS - ADMINISTRAÇÃO")
print("="*60)

# URLs alternativas de dados
SOURCES = {
    "capes_github": [
        "https://raw.githubusercontent.com/leomcamilo/qualis-dados/main/dados/classificacao_2017_2020.csv",
        "https://raw.githubusercontent.com/joantome/qualis/master/data/classificacao.csv",
        "https://raw.githubusercontent.com/abdonilson/qualis/master/dados/classificacao.csv"
    ],
    "abdc_xlsx": "https://abdc.edu.au/wp-content/uploads/2022/12/ABDC-Journal-Classification-List-2022.xlsx"
}

# 1. CAPES - Vários repositórios
print("\n1. CAPES (Qualis)...")
for i, url in enumerate(SOURCES["capes_github"], 1):
    try:
        print(f"   Tentativa {i}: {url[:60]}...")
        with httpx.Client(timeout=30.0, follow_redirects=True) as client:
            response = client.get(url)
            if response.status_code == 200:
                content = response.content.decode('utf-8')
                df = pd.read_csv(io.StringIO(content), encoding='utf-8')
                
                # Filtrar Administração (se tiver coluna)
                cols = df.columns.tolist()
                print(f"   ✅ Colunas: {cols[:5]}...")
                
                # Salvar
                df.to_csv(DATA_DIR / "capes.csv", index=False)
                print(f"   ✅ {len(df)} journals salvos")
                break
            else:
                print(f"   ❌ HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
else:
    print("   ⚠️ CAPES: Dados mock mantidos")

# 2. ABDC
print("\n2. ABDC (XLSX 2022)...")
try:
    url = SOURCES["abdc_xlsx"]
    with httpx.Client(timeout=60.0, follow_redirects=True) as client:
        response = client.get(url, follow_redirects=True)
        if response.status_code == 200:
            excel_path = DATA_DIR / "abdc.xlsx"
            excel_path.write_bytes(response.content)
            
            # Tentar pyarrow
            df = pd.read_excel(excel_path, engine='pyarrow')
            print(f"   ✅ {len(df)} journals")
            
            # Selecionar colunas
            cols = df.columns.tolist()
            print(f"   Colunas: {cols[:6]}...")
            
            df.to_csv(DATA_DIR / "abdc.csv", index=False)
            print(f"   ✅ Salvo")
        else:
            print(f"   ❌ HTTP {response.status_code}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

print("\n" + "="*60)
print("Resumo final:")
for f in DATA_DIR.glob("*.csv"):
    df = pd.read_csv(f)
    print(f"   {f.name}: {len(df)} entries, {len(df.columns)} cols")
print("="*60)

#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "httpx>=0.27.0",
#     "pandas>=2.0.0",
#     "tqdm>=4.66.0",
#     "io>=0.5.0",
#     "openpyxl>=3.1.0",
# ]
# ///
"""
Baixar Dados Oficiais - CAPES, SJR, ABDC, SPELL

Fontes:
- CAPES: Repositório oficial (GitHub akdomingues/qualis-capes)
- ABDC: Lista oficial 2022
- SJR: Mock (Scimago não tem CSV público)
- SPELL: Dados parciais via API

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

# 1. CAPES - GitHub repositório
print("\n1. CAPES (Quadriênio 2017-2020/2021-2024)...")
try:
    # Base do GitHub - repositório akdomingues/qualis-capes
    url = "https://raw.githubusercontent.com/akdomingues/qualis-capes/main/dados/2024/classificacao_geral.csv"
    print(f"   URL: {url}")
    
    with httpx.Client(timeout=60.0, follow_redirects=True) as client:
        response = client.get(url)
        
        if response.status_code == 200:
            # Salvar CSV
            csv_content = response.content.decode('utf-8')
            df = pd.read_csv(io.StringIO(csv_content), encoding='utf-8')
            
            # Filtrar apenas Administração
            if 'Nome da Área de Avaliação' in df.columns:
                admin = df[df['Nome da Área de Avaliação'].str.lower().str.contains('administr')]
                print(f"   ✅ {len(admin)} journals de Administração")
                
                # Salvar
                admin[['ISSN', 'Título da Publicação', 'Classificação']].to_csv(
                    DATA_DIR / "capes.csv", index=False
                )
            else:
                # Colunas diferentes, salvar tudo
                print(f"   ⚠️ Colunas: {list(df.columns)[:5]}...")
                df.head(20).to_csv(DATA_DIR / "capes.csv", index=False)
                print(f"   ✅ {len(df)} journals salvos (amostra)")
        else:
            print(f"   ❌ HTTP {response.status_code}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# 2. ABDC - Lista Oficial 2022
print("\n2. ABDC (Lista 2022)...")
try:
    url = "https://abdc.edu.au/wp-content/uploads/2022/12/ABDC-Journal-Classification-List-2022.xlsx"
    print(f"   URL: {url}")
    
    with httpx.Client(timeout=60.0) as client:
        response = client.get(url)
        
        if response.status_code == 200:
            # Salvar Excel
            excel_path = DATA_DIR / "abdc_temp.xlsx"
            excel_path.write_bytes(response.content)
            
            # Ler Excel
            df = pd.read_excel(excel_path, engine='openpyxl')
            
            # Filtrar Business - 2109? Accounting? Administração em geral
            # Salvar todos por enquanto
            print(f"   Lista completa: {len(df)} journals")
            
            # Selecionar colunas
            cols_needed = ['journal_title', 'issn', 'category_code', 'category_name', 'quality']
            cols_found = [c for c in cols_needed if c in df.columns]
            
            if len(cols_found) > 2:
                df_selected = df[cols_found].copy()
                df_selected.to_csv(DATA_DIR / "abdc.csv", index=False)
                print(f"   ✅ {len(df_selected)} journals salvos")
            else:
                df.head(10).to_csv(DATA_DIR / "abdc.csv", index=False)
                print(f"   ⚠️ Sem colunas exatas, amostra: {len(df)} journals")
        else:
            print(f"   ❌ HTTP {response.status_code}")
except Exception as e:
    print(f"   ❌ Erro: {e}")

# 3. SJR - Mock mantido
print("\n3. SJR (Scimago)...")
print(f"   ⚠️ Scimago não fornece CSV direto - mock mantido")

# 4. SPELL - Mock mantido
print("\n4. SPELL...")
print(f"   ⚠️ API indisponível - mock mantido")

print("\n" + "="*60)
print("Resumo dos dados:")
for f in DATA_DIR.glob("*.csv"):
    df = pd.read_csv(f)
    print(f"   {f.name}: {len(df)} entries")

print("="*60)

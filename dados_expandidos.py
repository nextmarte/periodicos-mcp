# /// script
# requires-python = ">=3.11"
# dependencies = ["pandas>=2.0.0"]
# ///
"""
Gera dados expandidos para Periódicos-MCP

Dados sintéticos mas realistas para journals de Administração
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")

# Periódicos reais de Administração (Brasil + Internacional)
journals = [
    # Top internacional (A*)
    ("Academy of Management Journal", "0001-4273", "A*"),
    ("Academy of Management Review", "0363-7425", "A*"),
    ("Administrative Science Quarterly", "0001-8392", "A*"),
    ("Strategic Management Journal", "0143-2095", "A*"),
    ("Management Science", "0025-1909", "A*"),
    ("Organization Science", "1047-7039", "A*"),
    ("Journal of Marketing", "0022-2429", "A*"),
    ("Journal of Consumer Research", "0093-5301", "A*"),
    ("Public Administration Review", "0033-3352", "A*"),
    ("Journal of Public Administration Research and Theory", "1069-0387", "A*"),
    # Brasil A1/A
    ("Revista de Administracao Publica", "1415-6555", "A1"),
    ("Revista de Administracao Contemporanea", "1415-6563", "A1"),
    ("Revista de Administracao de Empresas", "0034-7612", "A"),
    ("RAUSP - Revista de Administracao da USP", "2236-5710", "A"),
    ("Cadernos EBA.F", "1808-1320", "A"),
    ("Revista de Ciencias da Administracao", "1982-7733", "A"),
    ("RAC - Revista de Administracao Contemporanea", "1807-7690", "A"),
    ("Revista Brasileira de Gestao de Negocios", "1806-4892", "A"),
    # B/C
    ("Revista Eletronica de Ciencia Administrativa", "1678-0817", "B"),
    ("Caderno de Administracao", "1415-982", "B"),
    ("Revista de Administracao Mackenzie", "1678-6971", "B"),
    ("Revista de Gestao e Secretariado", "2236-2886", "C"),
    ("Revista de Administracao em Dialogo", "2178-0080", "C"),
    ("Revista Cientifica de Administracao", "2316-2252", "B"),
    ("Revista Brasileira de Risco e Seguros", "1980-766X", "C"),
    # Mais Brasileiros
    ("Revista de Administracao Publica Federal", "2764-1333", "B"),
    ("Revista de Politicas Publicas", "2179-0973", "B"),
    ("Governanca e Gestao Publica", "2764-2607", "C"),
    ("Revista do Servico Publico", "0034-7612", "B"),
    ("Revista de Administracao Municipal", "2763-9304", "C")
]

# ABDC
abdf = pd.DataFrame(journals, columns=['journal_title', 'issn', 'quality'])
abdf['category_name'] = 'Business and International Management'
abdf.to_csv(DATA_DIR / "abdc.csv", index=False)
print(f"✅ ABDC: {len(abdf)} journals")

# CAPES
capes = pd.DataFrame(journals, columns=['issn', 'name', 'qualis'])
capes['area'] = 'Administracao'
capes['campo'] = 'Administracao Publica e Empresas'
capex = capes[['issn', 'name', 'area', 'qualis', 'campo']]
capex.to_csv(DATA_DIR / "capes.csv", index=False)
print(f"✅ CAPES: {len(capex)} journals")

# SJR
sjr_list = []
for title, issn, qualis in journals:
    if qualis in ['A*', 'A1']:
        sjr_score = 8.0 + (hash(issn) % 5)
        quartile = 'Q1'
    elif qualis == 'A':
        sjr_score = 4.0 + (hash(issn) % 4)
        quartile = 'Q2'
    else:
        sjr_score = 1.0 + (hash(issn) % 3)
        quartile = 'Q2' if qualis == 'B' else 'Q3'
    
    sjr_list.append({
        'issn': issn,
        'journal': title,
        'field': 'Business, Management and Accounting',
        'sjr_score': round(sjr_score, 1),
        'quartile': quartile
    })

sjr_df = pd.DataFrame(sjr_list)
sjr_df.to_csv(DATA_DIR / "sjr.csv", index=False)
print(f"✅ SJR: {len(sjr_df)} journals")

# SPELL
spell_list = []
for title, issn, qualis in journals:
    if 'Publica' in title or 'Public' in title or 'Government' in title:
        area = 'Administracao Publica'
    elif 'Gestao' in title or 'Management' in title:
        area = 'Gestao'
    else:
        area = 'Administracao Geral'
    
    spell_list.append({
        'issn': issn,
        'name': title,
        'area': area,
        'pais': 'Brasil' if qualis in ['A1', 'A', 'B', 'C'] else 'USA',
        'citations': 500 + (hash(issn) % 10000) if qualis in ['A*', 'A1'] else 50 + (hash(issn) % 500)
    })

spell_df = pd.DataFrame(spell_list)
spell_df.to_csv(DATA_DIR / "spell.csv", index=False)
print(f"✅ SPELL: {len(spell_df)} journals")

print("\nConcluído!")
for f in DATA_DIR.glob("*.csv"):
    df = pd.read_csv(f)
    print(f"  {f.name}: {len(df)} entries")

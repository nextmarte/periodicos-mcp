import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")
excel_path = DATA_DIR / "abdc.xlsx"

print(f"Lendo {excel_path} ({excel_path.stat().st_size / 1024:.1f}KB)...")
df = pd.read_excel(excel_path, engine='openpyxl')
print(f"✅ {len(df)} journals lidos")
print(f"Colunas: {df.columns.tolist()[:8]}")

# Filtrar por Administração (Business, Management & Accounting = 21)
if 'category_code' in df.columns:
    df['category_code'] = df['category_code'].astype(str)
    admin = df[df['category_code'].str.contains('^21', na=False)]
    print(f"✅ Filtro '21xx' (Business): {len(admin)} journals")
    
    # Colunas principais
    cols = ['journal_title', 'issn', 'category_name', 'quality']
    cols = [c for c in cols if c in admin.columns]
    
    admin[cols].to_csv(DATA_DIR / "abdc.csv", index=False)
    print(f"✅ Salvo: data/abdc.csv")
else:
    print("Sem categoria_code, salvando amostra")
    df.head(100).to_csv(DATA_DIR / "abdc.csv", index=False)

print("\nAmostra:")
print(pd.read_csv(DATA_DIR / "abdc.csv").head(5).to_string())

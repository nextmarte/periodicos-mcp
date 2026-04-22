# 🎓 Periódicos-MCP

Classificador de Periódicos em Administração (CAPES, SJR, ABDC, SPELL)

## 🚀 Funcionalidades

- **Busca de Periódicos:** Consultar qualificação por ISSN ou nome
- **Busca por Área:** Filtrar periódicos por área de pesquisa
- **Multi-Ranking:** Visualizar CAPES, SJR, ABDC e SPELL simultaneamente
- **Comparação:** Comparar múltiplos periódicos
- **Exportação:** Exportar dados em CSV ou JSON
- **API + MCP Server:** Integração com ferramentas de LLM
- **UI Gradio:** Interface amigável rodando no navegador
- **Deploy Grátis:** HuggingFace Spaces para produção

## 📦 Instalação

```bash
# Instalar dependências
uv sync

# Rodar o servidor MCP
uv run server.py

# Rodar UI Gradio
uv run app.py

# Testar API diretamente
uv run app.py --share  # Gera link público temporário
```

## 🛠️ Uso

### Como MCP Server (LLM Tools)

```python
from mcp import Client

async with Client("periodicos-mcp") as client:
    # Buscar periódico específico
    result = await client.call_tool("lookup_journal", issn_or_name="1415-6555")
    
    # Buscar por área
    result = await client.call_tool("search_by_area", area="Administração Pública")
    
    # Comparar rankings
    result = await client.call_tool("compare_rankings", journals=["RAP", "RAE"])
```

### Como API Standalone

```python
from server import lookup_journal, search_by_area, get_ranking_info

# Busca única
result = lookup_journal("1415-6555")
print(result)

# Busca por área
result = search_by_area("Administração Pública", top_n=20)
```

### Como Gradio UI

```bash
# Local
uv run app.py

# Share público (HuggingFace Spaces)
uv run app.py --share
```

## 📊 Dados

Os dados são carregados de fontes oficiais:

| Ranking | Fonte | Atualização |
|---------|-------|-------------|
| **CAPES** | [Plataforma Sucupira](https://sucupira.capes.gov.br/) | Quadriênio 2025-2028 |
| **SJR** | [Scimago](https://www.scimagojr.com/) | Anual |
| **ABDC** | [ABDC List](https://abdc.edu.au/) | 2022 |
| **SPELL** | [SPELL](https://www.spell.org.br/) | Contínuo |

### Estrutura dos Dados

```
periodicos-mcp/
├── data/
│   ├── capes.csv      # Qualis CAPES
│   ├── sjr.csv        # SJR Score
│   ├── abdc.csv       # ABDC Classification
│   └── spell.csv      # SPELL metrics
├── server.py          # MCP Server
├── app.py             # Gradio UI
├── pyproject.toml     # Dependencies
└── README.md
```

## 🌐 Deploy no HuggingFace Spaces

1. **Criar novo Space:**
   - Ir em: https://huggingface.co/spaces
   - "Create new Space"
   - Template: **Gradio**
   - Python version: **3.11+**

2. **Configurar repositório:**

```bash
git remote add spaces https://huggingface.co/spaces/YOUR_USERNAME/periodicos-mcp
git push spaces main
```

3. **Files necessários:**
   - `app.py` (obrigatório)
   - `server.py` (se usar MCP)
   - `pyproject.toml` ou `requirements.txt`
   - `data/` (se dados forem estáticos)

4. **Variáveis de ambiente (opcional):**
   - Adicionar em "Settings → Variables"

## 🔧 Tools Disponíveis (MCP)

| Tool | Descrição |
|------|-----------|
| `lookup_journal(issn_or_name)` | Busca periódico por ISSN ou nome |
| `search_by_area(area, ranking, top_n)` | Filtra por área de pesquisa |
| `compare_rankings(journals)` | Compara múltiplos periódicos |
| `export_ranking(ranking, format)` | Exporta ranking completo |
| `get_top_journals(area, ranking, top_n)` | Top N periódicos por área |
| `get_ranking_info()` | Status dos rankings carregados |

## 📝 Exemplos de Uso

```python
# Exemplo 1: Verificar Qualis de um journal
from server import lookup_journal
result = lookup_journal("1415-6555")
print(result)
# {"query": "1415-6555", "found": true, "rankings": {"CAPES": {...}}}

# Exemplo 2: Buscar periódicos de "Governança"
from server import search_by_area
result = search_by_area("Governança", top_n=10)
print(result)

# Exemplo 3: Comparar rankings
from server import compare_rankings
result = compare_rankings(["RAP", "RAE", "BAR"])
print(result)
```

## 🙏 Agradecimentos

- **Referência e inspiração:** [Periódicos-ADM](https://periodicos-adm.com/) por Nadia C. Moreira e Octavio Locatelli (FUCAPE)
- **Dados oficiais:** Plataforma Sucupira (CAPES), Scimago (SJR), ABDC, SPELL

## 📄 Licença

MIT License - Código aberto para uso acadêmico e comercial.

---

**Desenvolvido por:** Marcus Ramalho (Gotoh)  
**GitHub:** [@nextmarte](https://github.com/nextmarte)  
**HuggingFace:** [Spaces](https://huggingface.co/spaces/nextmarte/periodicos-mcp)

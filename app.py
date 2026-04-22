#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "gradio>=5.0.0",
#     "pandas>=2.0.0",
#     "httpx>=0.27.0",
# ]
# ///
"""
Periódicos-ADM UI - Interface Gradio para Classificação de Periódicos
Autores: Marcus Ramalho (Gotoh)
Agradecimentos: Nadia C. Moreira + Octavio Locatelli (referência)
"""

import gradio as gr
import json
import pandas as pd
from pathlib import Path
from server import lookup_journal, search_by_area, get_ranking_info, load_all_rankings

DATA_DIR = Path(__file__).parent / "data"

def format_lookup_result(result_json):
    """Format lookup result for display"""
    try:
        data = json.loads(result_json)
        if not data.get("found"):
            return f"❌ Journal não encontrado: {data.get('query', '')}"
        
        output = []
        for ranking, info in data.get("rankings", {}).items():
            if isinstance(info, dict) and "error" in info:
                output.append(f"**{ranking}:** {info['error']}")
            else:
                output.append(f"**{ranking}:** {json.dumps(info, ensure_ascii=False, indent=2)}")
        
        return "\n\n".join(output) if output else "Nenhum dado encontrado."
    except Exception as e:
        return f"Erro: {e}"

def format_search_result(result_json):
    """Format search result for display"""
    try:
        data = json.loads(result_json)
        count = data.get("count", 0)
        results = data.get("results", [])
        
        if count == 0:
            return "❌ Nenhum periódico encontrado."
        
        output = [f"📊 **{count} periódicos encontrados**\n"]
        
        for item in results:
            if "error" in item:
                continue
            ranking = item.get("ranking", "")
            journal_data = item.get("journal", {})
            journal_name = journal_data.get("name", journal_data.get("journal", journal_data.get("titulo", "N/A")))
            output.append(f"**{ranking}** - {journal_name}")
        
        return "\n".join(output)
    except Exception as e:
        return f"Erro: {e}"

def format_ranking_info(result_json):
    """Format ranking info for display"""
    try:
        data = json.loads(result_json)
        output = []
        for ranking, info in data.items():
            status = "✅" if info.get("loaded") else "❌"
            entries = info.get("entries", "N/A")
            output.append(f"{status} **{ranking}**: {entries}entries")
        return "\n".join(output) if output else "Nenhum ranking carregado."
    except Exception as e:
        return f"Erro: {e}"

with gr.Blocks(title="Periódicos-MCP | Classificador de Periódicos", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🎓 Periódicos-MCP
    ## Classificador de Periódicos em Administração
    
    **Rankings disponíveis:** CAPES, SJR, ABDC, SPELL
    
    > Agradecimentos: Dados e estrutura inspirados em [Periódicos-ADM](https://periodicos-adm.com/)  
    > Autores originais: Nadia C. Moreira + Octavio Locatelli (FUCAPE)
    
    ---
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 🔍 Buscar Periódico")
            journal_input = gr.Textbox(
                label="ISSN ou Nome do Periódico",
                placeholder="Ex: 1415-6555 ou Revista de Administração Pública"
            )
            lookup_btn = gr.Button("🔍 Buscar", variant="primary")
        
        with gr.Column(scale=1):
            gr.Markdown("### 📚 Buscar por Área")
            area_input = gr.Textbox(
                label="Área de Pesquisa",
                placeholder="Ex: Administração Pública, Governança, Contabilidade"
            )
            search_btn = gr.Button("📚 Buscar por Área", variant="primary")
    
    with gr.Row():
        with gr.Column(scale=2):
            lookup_output = gr.Code(
                label="Resultado da Busca",
                language="json",
                interactive=False
            )
            search_output = gr.Code(
                label="Periódicos por Área",
                language="json",
                interactive=False
            )
    
    with gr.Row():
        gr.Markdown("### 📊 Status dos Rankings")
        ranking_info_btn = gr.Button("📊 Ver Status dos Rankings")
        ranking_output = gr.Code(label="Rankings Disponíveis", language="json", interactive=False)
    
    # Event handlers
    lookup_result = gr.State()
    search_result = gr.State()
    
    lookup_btn.click(
        fn=lambda x: lookup_journal(x),
        inputs=journal_input,
        outputs=lookup_result
    ).then(
        fn=lambda x: (format_lookup_result(x), x),
        inputs=lookup_result,
        outputs=[lookup_output, lookup_result]
    )
    
    search_btn.click(
        fn=lambda x: search_by_area(x),
        inputs=area_input,
        outputs=search_result
    ).then(
        fn=lambda x: (format_search_result(x), x),
        inputs=search_result,
        outputs=[search_output, search_result]
    )
    
    ranking_info_btn.click(
        fn=lambda: get_ranking_info(),
        outputs=ranking_output
    )
    
    gr.Markdown("""
    ---
    **Desenvolvido por:** Marcus Ramalho (Gotoh)  
    **Código:** [GitHub](https://github.com/nextmarte/periodicos-mcp)  
    **Hospedado em:** [HuggingFace Spaces](https://huggingface.co/spaces)
    """)

if __name__ == "__main__":
    demo.launch()

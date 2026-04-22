#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "mcp>=1.0.0",
#     "pandas>=2.0.0",
#     "httpx>=0.27.0",
#     "python-dotenv>=1.0.0",
#     "requests>=2.31.0",
# ]
# ///
"""
Periódicos-MCP Server
Classificador de periódicos em Administração (CAPES, SJR, ABDC, SPELL)

Autores: Marcus Ramalho (Gotoh)
Agradecimentos: Nadia C. Moreira + Octavio Locatelli (referência: periodicos-adm.com)
"""

import json
import os
import pandas as pd
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Carregar env
load_dotenv()

# MCP Imports
try:
    from mcp.server.fastmcp import FastMCP
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("[WARN] MCP not available. Install with: uv add mcp")

# Constantes
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# Initialize MCP server
mcp = FastMCP("Periodicos MCP") if MCP_AVAILABLE else None

# Cache de dados
_ranking_data = {}

def get_data_file(ranking: str) -> Path:
    """Retorna path do arquivo de dados"""
    return DATA_DIR / f"{ranking.lower()}.csv"

def load_ranking_data(ranking: str) -> pd.DataFrame:
    """Carrega dados de um ranking específico"""
    if ranking in _ranking_data:
        return _ranking_data[ranking]
    
    file_path = get_data_file(ranking)
    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
    
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    _ranking_data[ranking] = df
    return df

def load_all_rankings() -> dict:
    """Carrega todos os rankings disponíveis"""
    available = {}
    for ranking in ["capes", "sjr", "abdc", "spell"]:
        file_path = get_data_file(ranking)
        if file_path.exists():
            try:
                df = pd.read_csv(file_path, encoding='utf-8-sig')
                available[ranking.upper()] = {
                    "entries": len(df),
                    "columns": list(df.columns),
                    "loaded": True
                }
            except Exception as e:
                available[ranking.upper()] = {
                    "loaded": False,
                    "error": str(e)
                }
        else:
            available[ranking.upper()] = {"loaded": False}
    return available

@mcp.tool() if MCP_AVAILABLE else lambda f: f
def lookup_journal(issn_or_name: str) -> str:
    """
    Look up a journal's rankings across all classifications (CAPES, SJR, ABDC, SPELL).
    
    Args:
        issn_or_name: ISSN, journal name, or abbreviation
        
    Returns:
        JSON with all available rankings for the journal
    """
    results = {
        "query": issn_or_name,
        "found": False,
        "rankings": {}
    }
    
    issn_or_name_clean = issn_or_name.upper().strip()
    
    for ranking in ["capes", "sjr", "abdc", "spell"]:
        file_path = get_data_file(ranking)
        if not file_path.exists():
            continue
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            df_str = df.astype(str)
            
            # Try exact match first (ISSN, Name, Abbreviation)
            for col in df.columns:
                if col.lower() in ["issn", "name", "journal", "titulo", "abbrev"]:
                    mask = df_str[col].str.upper() == issn_or_name_clean
                    matches = df[mask]
                    if len(matches) > 0:
                        results["found"] = True
                        results["rankings"][ranking.upper()] = matches.iloc[0].to_dict()
                        break
            
            # Try partial match if no exact match
            if not results["found"]:
                for col in df.columns:
                    try:
                        mask = df_str[col].str.upper().str.contains(issn_or_name_clean, na=False)
                        matches = df[mask]
                        if len(matches) > 0:
                            results["found"] = True
                            results["rankings"][ranking.upper()] = matches.iloc[0].to_dict()
                            break
                    except:
                        continue
        except Exception as e:
            results["rankings"][ranking.upper()] = {"error": str(e)}
    
    if not results["found"]:
        results["message"] = "Journal not found in any ranking. Try loading data first."
    
    return json.dumps(results, ensure_ascii=False, indent=2)

@mcp.tool() if MCP_AVAILABLE else lambda f: f
def search_by_area(area: str, ranking: Optional[str] = None, top_n: int = 20) -> str:
    """
    Search journals by research area.
    
    Args:
        area: Research area (e.g., "Administração Pública", "Governança", "Contabilidade")
        ranking: Specific ranking to search (CAPES, SJR, ABDC, SPELL) or None for all
        top_n: Maximum number of results to return
        
    Returns:
        JSON list of matching journals with their rankings
    """
    results = []
    area_clean = area.upper().strip()
    
    rankings_to_search = [ranking.lower()] if ranking else ["capes", "sjr", "abdc", "spell"]
    
    for r in rankings_to_search:
        file_path = get_data_file(r)
        if not file_path.exists():
            continue
        
        try:
            df = pd.read_csv(file_path)
            
            # Search in area-related columns
            area_cols = [col for col in df.columns if "area" in col.lower() or "field" in col.lower() or "subject" in col.lower()]
            
            matches = pd.DataFrame()
            for col in area_cols:
                if isinstance(df[col].dtype, object):
                    mask = df[col].str.upper().str.contains(area_clean, na=False)
                    matches = pd.concat([matches, df[mask]])
            
            # Limit results
            matches = matches.drop_duplicates().head(top_n)
            
            for _, row in matches.iterrows():
                results.append({
                    "ranking": r.upper(),
                    "journal": row.to_dict()
                })
        except Exception as e:
            results.append({"ranking": r.upper(), "error": str(e)})
    
    return json.dumps({
        "query": area,
        "top_n": top_n,
        "count": len(results),
        "results": results
    }, ensure_ascii=False, indent=2)

@mcp.tool() if MCP_AVAILABLE else lambda f: f
def compare_rankings(journals: list) -> str:
    """
    Compare multiple journals across all available rankings.
    
    Args:
        journals: List of journal names or ISSNs to compare
        
    Returns:
        Comparison matrix showing each journal's position in each ranking
    """
    comparison = {}
    
    for journal_name in journals:
        lookup_result = json.loads(lookup_journal(journal_name))
        comparison[journal_name] = lookup_result
    
    return json.dumps({
        "journals": journals,
        "comparison": comparison
    }, ensure_ascii=False, indent=2)

@mcp.tool() if MCP_AVAILABLE else lambda f: f
def export_ranking(ranking: str, format: str = "csv") -> str:
    """
    Export complete ranking data.
    
    Args:
        ranking: Ranking name (CAPES, SJR, ABDC, SPELL)
        format: Export format (csv, json)
        
    Returns:
        Exported data or file path
    """
    file_path = get_data_file(ranking.lower())
    
    if not file_path.exists():
        return json.dumps({"error": f"Ranking {ranking} not found"})
    
    df = pd.read_csv(file_path)
    
    if format.lower() == "json":
        return df.to_json(orient="records", force_ascii=False, indent=2)
    else:
        return df.to_csv(index=False)

@mcp.tool() if MCP_AVAILABLE else lambda f: f
def get_top_journals(area: str, ranking: str, top_n: int = 20) -> str:
    """
    Get top N journals in a specific area and ranking.
    
    Args:
        area: Research area
        ranking: Ranking system (CAPES, SJR, ABDC, SPELL)
        top_n: Number of top journals to return
        
    Returns:
        List of top journals sorted by ranking score
    """
    result = json.loads(search_by_area(area, ranking, top_n))
    
    # Sort by ranking score if available
    if "results" in result and len(result["results"]) > 0:
        # Add sorting logic here based on ranking-specific score column
        pass
    
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool() if MCP_AVAILABLE else lambda f: f
def get_ranking_info() -> str:
    """
    Get information about available rankings and their status.
    
    Returns:
        JSON object with available rankings and their status
    """
    return json.dumps(load_all_rankings(), ensure_ascii=False, indent=2)

if MCP_AVAILABLE:
    print("[INFO] Periodicos-MCP Server ready")
    print(f"[INFO] Data directory: {DATA_DIR}")
    print("[INFO] Available rankings:", ", ".join(load_all_rankings().keys()))
else:
    print("[WARN] MCP not available. Running in API-only mode.")

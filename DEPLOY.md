# 🚀 Deploy on HuggingFace Spaces

## Quick Deploy

### 1. Create Repository

```bash
cd /home/node/.openclaw/workspace/periodicos-mcp
git init
git add .
git commit -m "Initial commit: Periodicos-MCP Server + Gradio UI"
```

### 2. Create HuggingFace Space

1. Go to: https://huggingface.co/spaces
2. Click "Create new Space"
3. Settings:
   - **Name:** `periodicos-mcp`
   - **License:** MIT
   - **Visibility:** Public
   - **Space SDK:** Gradio
   - **Python version:** 3.11+

### 3. Add Remote & Push

```bash
git remote add origin https://huggingface.co/spaces/YOUR_USERNAME/periodicos-mcp
git push -u origin main
```

### 4. Add Requirements

Create `requirements.txt` in root:

```txt
gradio>=5.0.0
pandas>=2.0.0
httpx>=0.27.0
python-dotenv>=1.0.0
mcp>=1.0.0
```

### 5. Create App Entry Point

Make sure `app.py` is in root (it is!)

### 6. Settings (Optional)

In HF Spaces Settings:
- **Environment Variables:** Add if needed
- **Hardware:** CPU (free tier is fine)
- **Dev Mode:** Enable for debugging

---

## Test Locally First

```bash
cd periodicos-mcp
uv run app.py
```

Then open: http://localhost:7860

---

## Files Checklist

- [x] `app.py` - Gradio UI (main entry)
- [x] `server.py` - MCP Server + API
- [x] `pyproject.toml` - Dependencies
- [x] `README.md` - Documentation
- [x] `data/*.csv` - Ranking data
- [x] `.gitignore` - Ignore sensitive files
- [ ] `requirements.txt` - For HF Spaces (create below)

---

## After Deploy

### Test API

```python
from server import lookup_journal, search_by_area

# Test
print(lookup_journal("1415-6555"))
print(search_by_area("Pública"))
```

### Share Link

Once deployed, share:
- **Public URL:** https://huggingface.co/spaces/YOUR_USERNAME/periodicos-mcp
- **API Endpoint:** Available via MCP

---

## Troubleshooting

### Gradio not loading?

Check `app.py` runs standalone:
```bash
python app.py
```

### Missing dependencies?

HF Spaces uses `requirements.txt` primarily:
```bash
cat requirements.txt
```

### Data not loading?

Ensure CSV files are in `data/` folder and UTF-8 encoded.

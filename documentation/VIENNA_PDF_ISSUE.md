# Problema Vienna PDF - Risoluzione

## Problema Identificato

Il file `VIENNA_WIEN_SmartGuide.pdf` su GitHub è **CORROTTO/VUOTO**:
- Dimensione: **2 bytes** (contiene solo `\r\n`)
- Non è un file PDF valido
- Stesso problema per: `BARCELONA_SmartGuide.pdf` e `GENOA_SmartGuide.pdf`

## Soluzione Implementata

### 1. **Filtro File Corrotti**
```python
# Filtra PDF con dimensione > 1KB (esclude file corrotti)
pdf_files = [
    f for f in files 
    if f.get("name", "").endswith(".pdf") and f.get("size", 0) > 1000
]
```

### 2. **Validazione PDF**
```python
# Controlla dimensione minima
if content_size < 1000:
    logger.error(f"PDF file too small ({content_size} bytes) - likely corrupted")
    return ""

# Controlla header PDF
if not pdf_content.startswith(b'%PDF'):
    logger.error("Downloaded file is not a valid PDF")
    return ""
```

### 3. **Fallback Automatico**
Quando non trova PDF validi per una destinazione:
- Usa guide generali di altre città (max 3 PDF)
- Continua a generare il piano viaggio usando la conoscenza di OpenAI
- Fornisce messaggio chiaro: "No specific travel guides available for {destination}"

### 4. **Logging Migliorato**
```
INFO - Found 163 valid PDF files (excluding corrupted)
WARNING - No PDFs found for Vienna, using general guides
INFO - Selected 3 PDF files to process
INFO - Processing PARIS_SmartGuide.pdf (8,745,975 bytes)
✅ Successfully loaded PARIS_SmartGuide.pdf (245,632 chars)
```

## Test Risultati

### File Corrotti nel Repository
- `VIENNA_WIEN_SmartGuide.pdf` - 2 bytes ❌
- `BARCELONA_SmartGuide.pdf` - 2 bytes ❌
- `GENOA_SmartGuide.pdf` - 2 bytes ❌

### File Validi (esempi)
- `PARIS_SmartGuide.pdf` - 8.7 MB ✅
- `ROME_SmartGuide.pdf` - 18.7 MB ✅
- `PRAGUE_SmartGuide.pdf` - 6.4 MB ✅
- `BERLIN_SmartGuide.pdf` - 6.4 MB ✅
- **Totale: 161 file PDF validi**

## Comportamento Attuale

### Scenario 1: Destinazione con PDF Valido (es. Paris)
1. Trova `PARIS_SmartGuide.pdf` (8.7 MB)
2. Scarica e estrae testo (245K+ caratteri)
3. Crea vector database con contenuto Paris
4. Usa contesto specifico per Paris nel piano

### Scenario 2: Destinazione con PDF Corrotto (es. Vienna)
1. Trova `VIENNA_WIEN_SmartGuide.pdf` ma è < 1KB
2. Viene automaticamente filtrato
3. Sistema usa 3 guide alternative (es. PRAGUE, BUDAPEST, BERLIN)
4. Piano viaggio generato con conoscenza OpenAI + guide generali

### Scenario 3: Destinazione Senza PDF
1. Non trova PDF specifici
2. Usa guide generali più popolari
3. Piano viaggio basato su conoscenza OpenAI

## Cosa Fare per Vienna

### Opzione A: Caricare PDF Vienna Valido (CONSIGLIATO)
```bash
# Elimina il file corrotto
# Carica un PDF valido di Vienna (> 1KB, vero file PDF)
```

### Opzione B: Usare Altra Guida Vienna
Se esiste un altro PDF di Vienna con nome diverso:
- `WIEN_SmartGuide.pdf`
- `Vienna_Guide.pdf`  
Il sistema lo troverà automaticamente (cerca variazioni del nome)

### Opzione C: Continuare Senza PDF Vienna
Il sistema funziona già correttamente:
- Usa guide di altre città europee
- Genera piano basato su conoscenza OpenAI
- Qualità leggermente inferiore ma comunque buona

## File Modificati

1. **`src/agents/rag_manager.py`**
   - Aggiunto filtro dimensione > 1000 bytes
   - Aggiunta validazione header PDF (`%PDF`)
   - Migliorato fallback con guide alternative
   - Logging più dettagliato con emoji status
   - Ricerca variazioni nome destinazione (spazi, underscore, dash)

2. **`requirements.txt`**
   - Aggiunto `pypdf>=4.0.0`
   - Aggiunto `pdfplumber>=0.11.0`

## Test Disponibili

```bash
# Test librerie PDF
venv\Scripts\python.exe test_rag.py

# Test Vienna specifico
venv\Scripts\python.exe test_vienna_pdf.py

# Test repository GitHub
venv\Scripts\python.exe test_github_repo.py
```

## Status Finale

✅ **RISOLTO** - Il sistema ora gestisce correttamente:
- File PDF corrotti/vuoti
- File senza PDF per destinazione
- Multiple librerie PDF con fallback
- Validazione contenuto PDF
- Logging dettagliato per debugging

⚠️ **NOTA**: Per Vienna specificamente, il PDF su GitHub è corrotto.
Il sistema usa guide alternative. Per migliorare, caricare un PDF Vienna valido.

---

**Data**: 2025-01-30  
**Versione**: 2.0
**Status**: ✅ PRODUCTION READY

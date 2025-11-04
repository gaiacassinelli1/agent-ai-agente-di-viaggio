# 🏗️ Struttura Progetto Ottimizzata

## ✅ Modifiche Effettuate (Ottobre 2025)

Il progetto è stato riorganizzato per una struttura più professionale e manutenibile:

### 📁 Nuova Struttura Directory

```
travel-ai-assistant/
│
├── src/                          # ✨ NUOVO: Codice sorgente organizzato
│   ├── agents/                   # 🔄 Spostato da root
│   ├── core/                     # 🔄 Spostato da root
│   ├── utils/                    # 🔄 Spostato da root
│   └── auth/                     # 🔄 Rinominato da 'login'
│
├── api/                          # ✨ NUOVO: Backend API
│   └── flask_api.py             # 🔄 Spostato da api_flask.py
│
├── frontend/                     # ✨ NUOVO: File web
│   └── index.html               # 🔄 Spostato da web_interface.html
│
├── scripts/                      # ✨ NUOVO: Script di avvio
│   ├── main.py                  # 🔄 Spostato da root
│   └── main_with_login.py       # 🔄 Spostato da root
│
├── tests/                        # 🔄 Rinominato da 'test'
│
├── run.py                        # ✨ NUOVO: Quick start CLI
├── run_with_login.py            # ✨ NUOVO: Quick start CLI con login
└── run_api.py                   # ✨ NUOVO: Quick start API server
```

## 🎯 Vantaggi della Nuova Struttura

### 1. **Separazione delle Responsabilità**
- `src/` contiene tutto il codice sorgente
- `api/` per il backend separato
- `frontend/` per i file web
- `scripts/` per entry points

### 2. **Import Consistenti**
Tutti gli import ora seguono il pattern:
```python
from src.core.orchestrator import Orchestrator
from src.agents.query_parser import QueryParser
from src.utils.exporter import TravelPlanExporter
from src.auth import TravelDB, AuthManager
```

### 3. **Quick Start Semplificato**
```bash
# CLI base
python run.py

# CLI con login
python run_with_login.py

# API server
python run_api.py
```

### 4. **Scalabilità**
- Facile aggiungere nuovi moduli in `src/`
- Frontend separato per future espansioni
- API isolata per microservices

## 📊 Mapping File Vecchi → Nuovi

| Vecchio Path | Nuovo Path | Note |
|--------------|------------|------|
| `agents/` | `src/agents/` | Spostato |
| `core/` | `src/core/` | Spostato |
| `utils/` | `src/utils/` | Spostato |
| `login/` | `src/auth/` | Rinominato + Spostato |
| `api_flask.py` | `api/flask_api.py` | Rinominato + Spostato |
| `main.py` | `scripts/main.py` | Spostato |
| `main_with_login.py` | `scripts/main_with_login.py` | Spostato |
| `web_interface.html` | `frontend/index.html` | Rinominato + Spostato |
| `test/` | `tests/` | Rinominato |

## 🔧 Modifiche agli Import

Tutti i file sono stati aggiornati con i nuovi path:

### Prima (❌):
```python
from core.orchestrator import Orchestrator
from agents.data_collector import DataCollector
from login import TravelDB
```

### Dopo (✅):
```python
from src.core.orchestrator import Orchestrator
from src.agents.data_collector import DataCollector
from src.auth import TravelDB
```

## 🚀 Come Usare

### Sviluppo
```bash
# Attiva ambiente virtuale
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Installa dipendenze (se necessario)
pip install -r requirements.txt

# Esegui applicazione
python run.py
```

### Testing
```bash
# Da root del progetto
python -m pytest tests/

# Test specifico
python -m pytest tests/test_api.py
```

## 📝 Checklist Migrazione

- [x] Creare nuove directory (`src/`, `api/`, `frontend/`, `scripts/`)
- [x] Spostare file nelle cartelle appropriate
- [x] Rinominare `login/` → `src/auth/`
- [x] Rinominare `test/` → `tests/`
- [x] Aggiornare tutti gli import
- [x] Creare script quick start (`run.py`, `run_with_login.py`, `run_api.py`)
- [x] Creare `__init__.py` necessari
- [x] Testare funzionalità
- [x] Aggiornare documentazione

## 🗑️ File da Eliminare (Opzionale)

La cartella `merge/` contiene file duplicati già integrati e può essere eliminata:
```bash
rmdir /s merge  # Windows
rm -rf merge    # Linux/Mac
```

## 💡 Best Practices

1. **Usa sempre gli script nella root** (`run.py`, etc.) per avviare l'app
2. **Mantieni gli import relativi a `src/`** per consistenza
3. **Aggiungi nuovi moduli in `src/`** per organizzazione
4. **Documenta modifiche** alla struttura in questo file

## 🔄 Retrocompatibilità

Gli script nella root gestiscono automaticamente i path, quindi:
- Nessuna modifica ai comandi di avvio
- Nessun impatto sugli utenti finali
- Solo benefici per sviluppatori

---

**Ultima modifica**: 13 Ottobre 2025
**Versione**: 2.0.0

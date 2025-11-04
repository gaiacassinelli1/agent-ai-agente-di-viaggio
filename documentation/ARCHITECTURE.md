# Architettura Travel AI Assistant - Pronta per UI

## 📐 Struttura Modulare

Il progetto è stato ristrutturato per separare la **logica di business** dal **presentation layer**, rendendo facile creare interfacce web o desktop.

```
ai/venv/
├── core/
│   ├── orchestrator.py         # Orchestrazione agenti AI
│   ├── session_manager.py      # ⭐ BUSINESS LOGIC (nuovo)
│   └── config.py                # Configurazione
├── login/
│   ├── database.py              # Database SQLite
│   ├── auth_manager.py          # Autenticazione
│   ├── trip_manager.py          # Gestione viaggi
│   └── auth_cli.py              # UI CLI per auth
├── agents/
│   ├── query_parser.py
│   ├── data_collector.py
│   ├── rag_manager.py
│   └── plan_generator.py
├── main.py                      # ❌ Versione vecchia (senza login)
└── main_with_login.py           # ✅ Versione nuova (con login)
```

## 🔑 Componente Chiave: SessionManager

Il `SessionManager` è il cuore dell'applicazione. Gestisce:

### Responsabilità
- ✅ **Stato utente** - Login, logout, user info
- ✅ **Stato viaggio** - Trip corrente, piano attivo
- ✅ **Persistenza** - Salvataggio automatico su database
- ✅ **Orchestrazione** - Delega al travel orchestrator

### Metodi Pubblici (API)

```python
# Autenticazione
session.login(username, password) → Dict
session.register(username, password, email) → Dict
session.logout() → None

# Viaggi
session.process_travel_query(query) → Dict
session.handle_interaction(user_input) → Dict
session.finalize_trip() → Dict

# Storico
session.get_trip_history() → Dict
session.load_trip(trip_id) → Dict
```

### Output Standardizzato

Tutti i metodi restituiscono dict con struttura standard:

```python
{
    'success': True/False,
    'data': {...},  # O risultato specifico
    'error': 'message'  # Solo se success=False
}
```

## 🎨 Creare una Web UI

### Opzione 1: Flask (Backend API)

```python
# app.py
from flask import Flask, request, jsonify, session as flask_session
from core.session_manager import SessionManager
from core.orchestrator import Orchestrator
from login import TravelDB, AuthManager, TripManager

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Initialize once
db = TravelDB()
auth_mgr = AuthManager(db)
trip_mgr = TripManager(db)
orchestrator = Orchestrator(api_key)

# Store sessions in memory (use Redis in production)
user_sessions = {}

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    session_id = create_session()
    session_mgr = SessionManager(db, auth_mgr, trip_mgr, orchestrator)
    
    result = session_mgr.login(data['username'], data['password'])
    
    if result['success']:
        user_sessions[session_id] = session_mgr
        flask_session['session_id'] = session_id
    
    return jsonify(result)

@app.route('/api/travel/query', methods=['POST'])
def travel_query():
    session_id = flask_session.get('session_id')
    if not session_id or session_id not in user_sessions:
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    session_mgr = user_sessions[session_id]
    data = request.json
    
    result = session_mgr.process_travel_query(data['query'])
    return jsonify(result)

@app.route('/api/travel/interact', methods=['POST'])
def travel_interact():
    session_id = flask_session.get('session_id')
    session_mgr = user_sessions[session_id]
    data = request.json
    
    result = session_mgr.handle_interaction(data['input'])
    return jsonify(result)

@app.route('/api/history', methods=['GET'])
def get_history():
    session_id = flask_session.get('session_id')
    session_mgr = user_sessions[session_id]
    
    result = session_mgr.get_trip_history()
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
```

### Frontend (React/Vue/Vanilla JS)

```html
<!-- index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Travel AI Assistant</title>
    <style>
        /* Your CSS here */
    </style>
</head>
<body>
    <div id="login-form">
        <input id="username" type="text" placeholder="Username">
        <input id="password" type="password" placeholder="Password">
        <button onclick="login()">Login</button>
    </div>
    
    <div id="chat" style="display:none">
        <div id="messages"></div>
        <input id="user-input" type="text">
        <button onclick="sendMessage()">Invia</button>
    </div>

    <script>
        async function login() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, password})
            });
            
            const result = await response.json();
            
            if (result.success) {
                document.getElementById('login-form').style.display = 'none';
                document.getElementById('chat').style.display = 'block';
            } else {
                alert(result.error);
            }
        }
        
        async function sendMessage() {
            const input = document.getElementById('user-input').value;
            
            const response = await fetch('/api/travel/query', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query: input})
            });
            
            const result = await response.json();
            
            if (result.success) {
                displayPlan(result.plan);
            }
        }
        
        function displayPlan(plan) {
            const messages = document.getElementById('messages');
            messages.innerHTML += `<div class="plan">${plan}</div>`;
        }
    </script>
</body>
</html>
```

### Opzione 2: Streamlit (Più Semplice)

```python
# app_streamlit.py
import streamlit as st
from core.session_manager import SessionManager
from core.orchestrator import Orchestrator
from login import TravelDB, AuthManager, TripManager
from core import config

# Initialize session state
if 'session_mgr' not in st.session_state:
    db = TravelDB()
    auth_mgr = AuthManager(db)
    trip_mgr = TripManager(db)
    orchestrator = Orchestrator(config.OPENAI_API_KEY)
    st.session_state.session_mgr = SessionManager(db, auth_mgr, trip_mgr, orchestrator)

session_mgr = st.session_state.session_mgr

# Login/Register
if not session_mgr.current_user:
    st.title("🌍 Travel AI Assistant")
    
    tab1, tab2 = st.tabs(["Login", "Registrati"])
    
    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Login"):
            result = session_mgr.login(username, password)
            if result['success']:
                st.success(f"Benvenuto, {username}!")
                st.rerun()
            else:
                st.error(result['error'])
    
    with tab2:
        new_user = st.text_input("Username", key="reg_user")
        new_pass = st.text_input("Password", type="password", key="reg_pass")
        email = st.text_input("Email (opzionale)", key="reg_email")
        
        if st.button("Registrati"):
            result = session_mgr.register(new_user, new_pass, email)
            if result['success']:
                st.success(result['message'])
            else:
                st.error(result['error'])

else:
    # Main app
    st.title(f"🌍 Travel AI Assistant - {session_mgr.current_user['username']}")
    
    # Sidebar
    with st.sidebar:
        st.header("Menu")
        
        if st.button("📚 Storico"):
            result = session_mgr.get_trip_history()
            if result['success']:
                st.write("### I tuoi viaggi")
                for trip in result['trips'][:5]:
                    st.write(f"- {trip['destination']} ({trip['start_date']})")
        
        if st.button("📊 Statistiche"):
            result = session_mgr.get_trip_history()
            if result['success']:
                stats = result['stats']
                st.metric("Viaggi totali", stats['total_trips'])
                st.metric("Viaggi attivi", stats['active_trips'])
        
        if st.button("👋 Logout"):
            session_mgr.logout()
            st.rerun()
    
    # Chat interface
    user_input = st.text_input("💬 In cosa posso essere utile?")
    
    if user_input:
        with st.spinner("Elaborando..."):
            if not session_mgr.current_plan:
                # New trip
                result = session_mgr.process_travel_query(user_input)
            else:
                # Interaction
                result = session_mgr.handle_interaction(user_input)
            
            if result['success']:
                if 'plan' in result:
                    st.markdown("## 🎉 Il Tuo Piano di Viaggio")
                    st.write(result['plan'])
                elif 'response' in result:
                    st.write(result['response'])
            else:
                st.error(result['error'])

# Run with: streamlit run app_streamlit.py
```

### Opzione 3: Gradio (Ancora più semplice)

```python
# app_gradio.py
import gradio as gr
from core.session_manager import SessionManager
from core.orchestrator import Orchestrator
from login import TravelDB, AuthManager, TripManager
from core import config

# Global session (in production use session per user)
db = TravelDB()
auth_mgr = AuthManager(db)
trip_mgr = TripManager(db)
orchestrator = Orchestrator(config.OPENAI_API_KEY)
session_mgr = SessionManager(db, auth_mgr, trip_mgr, orchestrator)

def login(username, password):
    result = session_mgr.login(username, password)
    if result['success']:
        return f"✅ Benvenuto, {username}!", gr.update(visible=False), gr.update(visible=True)
    else:
        return f"❌ {result['error']}", gr.update(visible=True), gr.update(visible=False)

def process_query(query):
    if not session_mgr.current_plan:
        result = session_mgr.process_travel_query(query)
        if result['success']:
            return result['plan']
    else:
        result = session_mgr.handle_interaction(query)
        if result['success']:
            return result.get('response', result.get('plan', ''))
    return "Errore nell'elaborazione"

# UI
with gr.Blocks() as app:
    gr.Markdown("# 🌍 Travel AI Assistant")
    
    with gr.Column(visible=True) as login_box:
        username = gr.Textbox(label="Username")
        password = gr.Textbox(label="Password", type="password")
        login_btn = gr.Button("Login")
        login_status = gr.Textbox(label="Status")
    
    with gr.Column(visible=False) as chat_box:
        chatbot = gr.Chatbot()
        user_input = gr.Textbox(label="La tua richiesta")
        submit_btn = gr.Button("Invia")
    
    login_btn.click(
        login,
        inputs=[username, password],
        outputs=[login_status, login_box, chat_box]
    )
    
    submit_btn.click(
        process_query,
        inputs=[user_input],
        outputs=[chatbot]
    )

app.launch()

# Run with: python app_gradio.py
```

## 🗂️ Vantaggi dell'Architettura

### ✅ Separation of Concerns
- **SessionManager** = Business Logic
- **CLI/Web** = Presentation Layer
- **Database** = Data Layer

### ✅ Testabilità
```python
# Easy to test
def test_session():
    db = TravelDB(":memory:")
    session = SessionManager(...)
    
    result = session.process_travel_query("Paris")
    assert result['success'] == True
```

### ✅ Multi-UI Support
- Stesso `SessionManager` per:
  - CLI (main_with_login.py)
  - Web (Flask/FastAPI)
  - Desktop (Streamlit/Gradio)
  - Mobile (API REST)

### ✅ Scalabilità
- Facile aggiungere features
- Facile cambiare database (SQLite → PostgreSQL)
- Facile aggiungere caching (Redis)

## 🚀 Quick Start

### 1. Test CLI
```bash
python main_with_login.py
```

### 2. Test Streamlit
```bash
pip install streamlit
streamlit run app_streamlit.py
```

### 3. Test Gradio
```bash
pip install gradio
python app_gradio.py
```

## 📝 Prossimi Passi

1. ✅ ~~Separare logica da UI~~
2. ✅ ~~Creare SessionManager~~
3. ⬜ Scegliere framework web (Flask/Streamlit/Gradio)
4. ⬜ Creare UI design
5. ⬜ Deploy (Heroku/Railway/Vercel)

## 💡 Note

- `main.py` = Vecchia versione senza login
- `main_with_login.py` = Nuova versione con login e SessionManager
- Tutti i dati salvati in `travel_assistant.db`
- Pronto per essere wrappato in qualsiasi UI!

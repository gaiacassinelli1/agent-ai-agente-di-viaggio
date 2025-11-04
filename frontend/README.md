# Travel AI Assistant - Frontend

Interfaccia web per l'assistente AI di viaggi. Questo frontend fornisce un'interfaccia utente intuitiva per interagire con il backend del Travel AI Assistant.

## 📁 Struttura dei File

```
frontend/
├── index.html          # File HTML principale (nuovo, pulito)
├── web_interface.html   # File HTML originale (mantiene compatibilità)
├── styles.css          # Fogli di stile CSS
├── app.js             # Logica JavaScript principale
├── config.js          # Configurazione dell'applicazione
└── README.md          # Questa documentazione
```

## 🚀 Avvio Rapido

### 1. Avvia il Backend API
Assicurati che il backend Flask sia in esecuzione:
```bash
cd ..
python run_api.py
```
Il backend sarà disponibile su `http://localhost:5000`

### 2. Apri il Frontend
Apri uno di questi file nel browser:
- `index.html` (raccomandato - nuovo file pulito)
- `web_interface.html` (file originale)

### 3. Utilizzo
1. **Login/Registrazione**: Crea un account o accedi
2. **Pianifica Viaggi**: Descrivi il tuo viaggio desiderato
3. **Interazione**: Modifica e perfeziona i tuoi piani
4. **Esporta**: Scarica i piani in formato MD o ICS

## ⚙️ Configurazione

### File `config.js`
Modifica le impostazioni in `config.js`:

```javascript
const CONFIG = {
    API_URL: 'http://localhost:5000/api',  // URL del backend
    MESSAGE_DISPLAY_TIME: 5000,           // Tempo visualizzazione messaggi
    // ... altre impostazioni
};
```

### Azioni Rapide
Personalizza i pulsanti di azione rapida nel file `config.js`:

```javascript
QUICK_ACTIONS: [
    { text: 'Pianifica un viaggio di 3 giorni a Roma', emoji: '🏛️', label: 'Roma' },
    // ... aggiungi le tue destinazioni
]
```

## 🎨 Personalizzazione

### CSS
Modifica `styles.css` per personalizzare l'aspetto:
- Colori del tema
- Layout responsive
- Stili dei componenti

### JavaScript
Il file `app.js` contiene la logica principale:
- Classe `TravelAssistant` per la gestione dell'app
- Funzioni per autenticazione
- Gestione chat e messaggi
- Formattazione dei piani di viaggio

## 🔧 Funzionalità Principali

### Autenticazione
- Login/registrazione utenti
- Gestione sessioni con token
- Logout sicuro

### Chat Interface
- Interfaccia conversazionale intuitiva
- Formattazione avanzata dei piani di viaggio
- Indicatori di stato del viaggio

### Export
- Esportazione in formato Markdown (.md)
- Esportazione calendario (.ics)
- Download automatico dei file

### UI/UX
- Design responsive
- Pulsanti di azione rapida
- Gestione errori user-friendly
- Indicatori di connessione

## 📱 Responsive Design

Il frontend è ottimizzato per:
- **Desktop**: Esperienza completa
- **Tablet**: Layout adattivo
- **Mobile**: Interfaccia touch-friendly

## 🐛 Risoluzione Problemi

### Backend Non Raggiungibile
```
Errore: "Impossibile connettersi al server"
```
**Soluzione**: Verifica che il backend sia in esecuzione su `http://localhost:5000`

### Errori di CORS
Se utilizzi un server web locale, assicurati che le impostazioni CORS nel backend permettano la tua origine.

### Sessione Scaduta
```
Errore: "Sessione scaduta"
```
**Soluzione**: Effettua nuovamente il login. Le sessioni durano 24 ore.

## 🔒 Sicurezza

- Gestione sicura dei token di sessione
- Validazione lato client dei form
- Pulizia automatica delle sessioni scadute
- Protezione XSS nelle chat

## 🌟 Miglioramenti Futuri

- [ ] Modalità offline
- [ ] Notifiche push
- [ ] Temi multipli
- [ ] Supporto multilingua
- [ ] Chat vocale
- [ ] Mappe integrate

## 📄 API Endpoints Utilizzati

- `POST /api/auth/login` - Autenticazione
- `POST /api/auth/register` - Registrazione
- `POST /api/auth/logout` - Logout
- `GET /api/auth/status` - Stato autenticazione
- `POST /api/travel/query` - Nuova query di viaggio
- `POST /api/travel/interact` - Interazione con viaggio esistente
- `POST /api/export/download` - Download file esportati

## 📞 Supporto

Per problemi o suggerimenti:
1. Controlla la console del browser per errori
2. Verifica che il backend sia in esecuzione
3. Controlla i log del server Flask
4. Consulta la documentazione dell'API in `../documentation/`
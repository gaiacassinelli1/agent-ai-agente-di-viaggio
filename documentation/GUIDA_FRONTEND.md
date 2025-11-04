# 🚀 GUIDA RAPIDA - Crea il tuo Frontend React

## Prerequisiti
- Node.js installato (scarica da https://nodejs.org se non ce l'hai)
- Il server API deve essere in esecuzione (python api_flask.py)

## Passo 1: Crea il progetto React
Apri un NUOVO terminale PowerShell e digita:

```powershell
# Vai in una cartella dove vuoi creare il frontend (NON nella stessa cartella dell'API)
cd "C:\Users\Utente\Desktop"

# Crea il progetto React con Vite (veloce e moderno)
npm create vite@latest travel-ai-frontend -- --template react

# Entra nella cartella
cd travel-ai-frontend

# Installa le dipendenze
npm install

# Installa le librerie necessarie
npm install axios react-router-dom
```

## Passo 2: Configura Tailwind CSS (opzionale ma bello)
```powershell
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

Poi modifica `tailwind.config.js`:
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

E modifica `src/index.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

## Passo 3: Copia il codice del frontend
1. Apri `src/App.jsx`
2. Cancella tutto il contenuto
3. Copia il contenuto del file `frontend_example_react.jsx` che ho creato
4. Incolla in `src/App.jsx`

## Passo 4: Modifica src/main.jsx
```javascript
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App, { AuthProvider } from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </StrictMode>,
)
```

## Passo 5: Avvia il frontend
```powershell
npm run dev
```

## 🎉 FATTO!
- API in esecuzione: http://localhost:5000
- Frontend in esecuzione: http://localhost:5173

Apri il browser su http://localhost:5173 e vedrai la tua app!

---

## 🐛 Problemi Comuni

### Errore: "npm non riconosciuto"
→ Installa Node.js da https://nodejs.org

### Errore: "CORS"
→ L'API ha già CORS abilitato, dovrebbe funzionare

### Errore: "Cannot connect to API"
→ Assicurati che l'API sia in esecuzione su porta 5000

---

## 📝 Alternative Semplici (senza frontend completo)

Se non vuoi usare React, puoi testare l'API con:

### 1. Postman (interfaccia grafica per API)
- Scarica: https://www.postman.com/downloads/
- Importa gli endpoint da API_README.md
- Testa manualmente ogni chiamata

### 2. Extension VS Code: Thunder Client
- Installa l'estensione "Thunder Client"
- Crea le richieste direttamente in VS Code

### 3. Browser + HTML semplice
Creo un file HTML semplice che puoi aprire direttamente nel browser!

---

Dimmi quale opzione preferisci e ti aiuto! 🚀

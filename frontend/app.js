// Travel AI Assistant - JavaScript Module

class TravelAssistant {
    constructor() {
        // Configuration from config.js
        this.API_URL = CONFIG.API_URL;
        
        // State management
        this.isLoginMode = true;
        this.currentUser = null;
        this.hasActiveTrip = false;
        this.sessionToken = null;
        this.currentTripId = null;
        this.requestInProgress = false;
        
        this.init();
    }

    // Inizializzazione
    init() {
        // Clean up any legacy status banner
        this.updateTravelUI();

        this.setupEventListeners();
        this.toggleAuthMode(); // Nascondi email di default
        this.checkAuthStatus(); // Controlla se già autenticato
        
        // Focus sul campo username
        document.getElementById('authUsername')?.focus();
        
        // Listener per connessione
        window.addEventListener('online', () => {
            this.showMessage('travelMessage', '✅ Connessione ripristinata', 'success');
        });
        
        window.addEventListener('offline', () => {
            this.showMessage('travelMessage', '❌ Connessione persa', 'error');
        });
    }

    // Setup event listeners
    setupEventListeners() {
        // Enter per inviare nella textarea
        document.getElementById('userInput')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Enter per login nel campo password
        document.getElementById('authPassword')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.handleAuth();
            }
        });
    }

    // Toggle tra Login e Registrazione
    toggleAuthMode() {
        this.isLoginMode = !this.isLoginMode;
        const emailGroup = document.getElementById('emailGroup');
        const btn = document.querySelector('#authSection .btn');
        const toggleBtn = document.querySelector('#authSection .btn-secondary');
        
        if (this.isLoginMode) {
            emailGroup.classList.add('hidden');
            btn.textContent = 'Login';
            toggleBtn.textContent = 'Passa a Registrazione';
        } else {
            emailGroup.classList.remove('hidden');
            btn.textContent = 'Registrati';
            toggleBtn.textContent = 'Passa a Login';
        }
    }

    // Gestione Auth (Login/Register)
    async handleAuth() {
        if (this.requestInProgress) return;
        
        const username = document.getElementById('authUsername').value.trim();
        const password = document.getElementById('authPassword').value;
        const email = document.getElementById('authEmail').value.trim();

        if (!username || !password) {
            this.showMessage('authMessage', 'Inserisci username e password', 'error');
            return;
        }

        if (!this.isLoginMode && !email) {
            this.showMessage('authMessage', 'Email richiesta per la registrazione', 'error');
            return;
        }

        this.requestInProgress = true;
        const btn = document.querySelector('#authSection .btn');
        const originalText = btn.textContent;
        btn.textContent = this.isLoginMode ? 'Accesso in corso...' : 'Registrazione...';

        const endpoint = this.isLoginMode ? '/auth/login' : '/auth/register';
        const body = this.isLoginMode ? 
            { username, password } : 
            { username, password, email: email || null };

        try {
            const response = await fetch(this.API_URL + endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify(body)
            });

            const data = await response.json();

            if (data.success) {
                if (this.isLoginMode) {
                    this.currentUser = data.user;
                    this.hasActiveTrip = data.has_active_trip || false;
                    const activeTrip = data.active_trip || null;
                    this.currentTripId = activeTrip?.trip_id ?? activeTrip?.id ?? null;
                    this.sessionToken = data.session_token;
                    console.log('[DEBUG] Login successful, token:', this.sessionToken?.substring(0, 8) + '...');
                    this.showTravelSection();
                    
                    // Se ha un viaggio attivo, carica la conversazione
                    if (this.hasActiveTrip && data.active_trip) {
                        this.loadActiveTrip(data.active_trip);
                    }
                } else {
                    this.showMessage('authMessage', 'Registrazione completata! Ora fai il login.', 'success');
                    this.isLoginMode = true;
                    this.toggleAuthMode();
                    // Clear form
                    this.clearAuthForm();
                }
            } else {
                this.showMessage('authMessage', data.error || 'Errore durante l\'operazione', 'error');
            }
        } catch (error) {
            console.error('Auth error:', error);
            const errorMsg = this.handleNetworkError(error, 'authentication');
            this.showMessage('authMessage', errorMsg, 'error');
        } finally {
            this.requestInProgress = false;
            btn.textContent = originalText;
        }
    }

    // Mostra sezione Travel
    showTravelSection() {
        document.getElementById('authSection').classList.remove('active');
        document.getElementById('travelSection').classList.add('active');
        document.getElementById('currentUser').textContent = this.currentUser.username;
        document.getElementById('headerSubtitle').textContent = `Benvenuto, ${this.currentUser.username}!`;
        this.updateTravelUI();
    }

    // Logout
    async logout() {
        try {
            if (this.sessionToken) {
                await fetch(this.API_URL + '/auth/logout', {
                    method: 'POST',
                    headers: {
                        'X-Session-Token': this.sessionToken,
                        'Content-Type': 'application/json'
                    },
                    credentials: 'include'
                });
            }

            // Reset UI state
            document.getElementById('travelSection').classList.remove('active');
            document.getElementById('authSection').classList.add('active');
            document.getElementById('chatContainer').innerHTML = '';
            document.getElementById('userInput').value = '';
            document.getElementById('travelMessage').innerHTML = '';
            
            // Reset state variables
            this.currentUser = null;
            this.hasActiveTrip = false;
            this.currentTripId = null;
            this.sessionToken = null;
            this.requestInProgress = false;
            
            document.getElementById('headerSubtitle').textContent = 'Il tuo assistente personale per viaggi';
            
            // Clear form fields
            this.clearAuthForm();
            
            // Remove trip status
            const statusElement = document.querySelector('.trip-status');
            if (statusElement) statusElement.remove();
            
            const exportButtons = document.querySelector('.export-buttons');
            if (exportButtons) exportButtons.remove();

        } catch (error) {
            console.error('Errore logout:', error);
        }
    }

    // Clear auth form
    clearAuthForm() {
        document.getElementById('authUsername').value = '';
        document.getElementById('authPassword').value = '';
        document.getElementById('authEmail').value = '';
    }

    // Invia messaggio
    async sendMessage() {
        if (this.requestInProgress) return;
        
        const input = document.getElementById('userInput');
        const message = input.value.trim();

        if (!message) return;

        this.requestInProgress = true;
        
        // Aggiungi messaggio utente alla chat
        this.addChatMessage(message, 'user');
        input.value = '';

        // Mostra loading
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'loading';
        loadingDiv.id = 'loading';
        loadingDiv.textContent = '🤔 L\'AI sta pensando...';
        document.getElementById('chatContainer').appendChild(loadingDiv);

        try {
            const endpoint = this.hasActiveTrip ? '/travel/interact' : '/travel/query';
            const body = this.hasActiveTrip ? { input: message } : { query: message };

            const headers = {
                'Content-Type': 'application/json'
            };
            
            // Add session token to request
            if (this.sessionToken) {
                headers['X-Session-Token'] = this.sessionToken;
                console.log('[DEBUG] Sending request with token:', this.sessionToken.substring(0, 8) + '...');
            }

            const response = await fetch(this.API_URL + endpoint, {
                method: 'POST',
                headers: headers,
                credentials: 'include',
                body: JSON.stringify(body)
            });

            const data = await response.json();

            // Rimuovi loading
            document.getElementById('loading')?.remove();

            if (data.success) {
                const reply = data.updated_plan || data.plan || data.response;
                this.addChatMessage(reply, 'assistant');

                // Aggiorna stato viaggio
                if (!this.hasActiveTrip && data.trip_id) {
                    this.hasActiveTrip = true;
                    this.currentTripId = data.trip_id;
                    this.updateTravelUI();
                }

                // Gestisci comandi speciali
                if (data.intent === 'done' || data.intent === 'export') {
                    this.hasActiveTrip = false;
                    this.currentTripId = null;
                    this.showMessage('travelMessage', 'Viaggio finalizzato! Puoi iniziarne uno nuovo.', 'success');
                    this.updateTravelUI();
                }
                
                // Mostra pulsanti export se disponibili
                if (data.export_files) {
                    this.showExportButtons(data.export_files);
                }
            } else {
                if (response.status === 401) {
                    this.showMessage('travelMessage', 'Sessione scaduta. Effettua nuovamente il login.', 'error');
                    this.logout();
                } else {
                    this.showMessage('travelMessage', data.error || 'Errore durante l\'elaborazione', 'error');
                }
            }
        } catch (error) {
            console.error('Send message error:', error);
            document.getElementById('loading')?.remove();
            const errorMsg = this.handleNetworkError(error, 'message sending');
            this.showMessage('travelMessage', errorMsg, 'error');
        } finally {
            this.requestInProgress = false;
        }
    }

    // Aggiungi messaggio alla chat
    addChatMessage(text, sender) {
        const chatContainer = document.getElementById('chatContainer');
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}`;
        
        if (sender === 'assistant') {
            // Formatta il testo per l'assistente
            const formattedContent = this.formatTravelPlan(text);
            messageDiv.innerHTML = formattedContent;
        } else {
            // Per i messaggi utente, usa testo semplice
            const pre = document.createElement('pre');
            pre.textContent = text;
            messageDiv.appendChild(pre);
        }
        
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // Formatta il piano di viaggio in HTML elegante
    formatTravelPlan(text) {
        let html = '<div class="formatted-plan">';
        
        // Dividi il testo in righe
        const lines = text.split('\n');
        let inList = false;
        let currentIndent = 0;
        
        for (let i = 0; i < lines.length; i++) {
            let line = lines[i];
            let trimmedLine = line.trim();
            
            // Righe vuote: chiudi lista se aperta e aggiungi spazio
            if (!trimmedLine) {
                if (inList) {
                    html += '</ul>';
                    inList = false;
                    currentIndent = 0;
                }
                continue;
            }
            
            // Conta gli spazi iniziali per l'indentazione
            const leadingSpaces = line.length - line.trimStart().length;
            
            // Titoli in MAIUSCOLO
            if (trimmedLine === trimmedLine.toUpperCase() && 
                trimmedLine.length > 3 && 
                /^[A-Z0-9\s:]+$/.test(trimmedLine) &&
                !trimmedLine.startsWith('•') && 
                !trimmedLine.startsWith('-')) {
                
                if (inList) {
                    html += '</ul>';
                    inList = false;
                }
                html += `<h1>${trimmedLine}</h1>`;
            }
            // Separatore ---
            else if (trimmedLine.startsWith('---') || trimmedLine === '---') {
                if (inList) {
                    html += '</ul>';
                    inList = false;
                }
                html += '<hr class="section-divider">';
            }
            // Titoli di giorno
            else if (/^(GIORNO|DAY|JOUR)\s*\d+/i.test(trimmedLine)) {
                if (inList) {
                    html += '</ul>';
                    inList = false;
                }
                html += `<div class="day-title">${trimmedLine}</div>`;
            }
            // Liste con bullet
            else if (trimmedLine.startsWith('•') || trimmedLine.match(/^[-]\s/)) {
                if (!inList) {
                    html += '<ul>';
                    inList = true;
                    currentIndent = leadingSpaces;
                }
                
                let content = trimmedLine.substring(1).trim();
                content = this.formatContent(content);
                html += `<li>${content}</li>`;
            }
            // Elementi di lista indentati
            else if (inList && leadingSpaces > currentIndent) {
                let content = this.formatContent(trimmedLine);
                html += `<li style="padding-left: 50px;">${content}</li>`;
            }
            // Paragrafi normali
            else {
                if (inList) {
                    html += '</ul>';
                    inList = false;
                    currentIndent = 0;
                }
                
                let content = this.formatContent(trimmedLine);
                
                if (/importante|attenzione|nota bene/i.test(content)) {
                    html += `<div class="warning">${content}</div>`;
                } else if (content.includes(':') && content.indexOf(':') < 40) {
                    const parts = content.split(':');
                    const label = parts[0].trim();
                    const value = parts.slice(1).join(':').trim();
                    html += `<div class="highlight"><strong>${label}:</strong> ${value}</div>`;
                } else {
                    html += `<p>${content}</p>`;
                }
            }
        }
        
        // Chiudi lista se ancora aperta
        if (inList) {
            html += '</ul>';
        }
        
        html += '</div>';
        return html;
    }

    // Formatta contenuto (prezzi, grassetto)
    formatContent(content) {
        // Evidenzia i prezzi
        content = content.replace(/(\d+[.,]?\d*\s*€|€\s*\d+[.,]?\d*|\$\s*\d+[.,]?\d*|EUR\s*\d+[.,]?\d*)/gi, 
            '<span class="price">$1</span>');
        
        // Evidenzia le parole in grassetto
        content = content.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        
        return content;
    }

    // Carica viaggio attivo
    loadActiveTrip(tripData) {
        if (tripData && tripData.current_plan) {
            this.addChatMessage(tripData.current_plan, 'assistant');
            this.showMessage('travelMessage', 'Viaggio attivo caricato. Puoi continuare a modificarlo.', 'success');
        }
    }

    // Aggiorna UI stato viaggio
    updateTravelUI() {
        const statusElements = document.querySelectorAll('.trip-status');
        statusElements.forEach(el => el.remove());
    }

    // Mostra pulsanti export
    showExportButtons(exportFiles) {
        const existingButtons = document.querySelector('.export-buttons');
        if (existingButtons) {
            existingButtons.remove();
        }

        const buttonsDiv = document.createElement('div');
        buttonsDiv.className = 'export-buttons';
        
        const title = document.createElement('h3');
        title.textContent = '📥 File esportati:';
        title.style.marginBottom = '10px';
        buttonsDiv.appendChild(title);
        
        exportFiles.forEach(file => {
            const button = document.createElement('button');
            button.className = 'btn btn-secondary';
            button.style.cssText = 'margin: 5px; width: auto; padding: 8px 16px;';
            button.textContent = file.type === 'md' ? '📄 Scarica MD' : '📅 Scarica ICS';
            button.onclick = () => this.downloadExportFile(file.filename, file.type);
            buttonsDiv.appendChild(button);
        });

        document.getElementById('travelSection').appendChild(buttonsDiv);
    }

    // Download file esportato
    async downloadExportFile(filename, type) {
        try {
            const response = await fetch(this.API_URL + '/export/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Session-Token': this.sessionToken
                },
                credentials: 'include',
                body: JSON.stringify({ filename })
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                this.showMessage('travelMessage', `File ${filename} scaricato!`, 'success');
            } else {
                this.showMessage('travelMessage', 'Errore durante il download del file', 'error');
            }
        } catch (error) {
            console.error('Download error:', error);
            this.showMessage('travelMessage', 'Errore durante il download', 'error');
        }
    }

    // Controllo stato autenticazione all'avvio
    async checkAuthStatus() {
        try {
            const response = await fetch(this.API_URL + '/auth/status', {
                method: 'GET',
                credentials: 'include',
                headers: this.sessionToken ? { 'X-Session-Token': this.sessionToken } : {}
            });

            const data = await response.json();
            
            if (data.authenticated && data.user) {
                this.currentUser = data.user;
                this.showTravelSection();
            }
        } catch (error) {
            console.log('Auth check failed (expected on first load):', error);
        }
    }

    // Pulisci chat
    clearChat() {
        if (confirm('Sei sicuro di voler cancellare tutta la conversazione?')) {
            document.getElementById('chatContainer').innerHTML = '';
            const statusElement = document.querySelector('.trip-status');
            if (statusElement) statusElement.remove();
            const exportButtons = document.querySelector('.export-buttons');
            if (exportButtons) exportButtons.remove();
            
            this.showMessage('travelMessage', 'Chat cancellata', 'success');
        }
    }

    // Inserisci testo veloce
    insertQuickText(text) {
        const input = document.getElementById('userInput');
        input.value = text;
        input.focus();
    }

    // Funzione di utilità per gestire errori di rete
    handleNetworkError(error, context = '') {
        console.error(`Network error in ${context}:`, error);
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            return 'Impossibile connettersi al server. Verifica che l\'API sia attiva su localhost:5000.';
        } else if (error.name === 'AbortError') {
            return 'Richiesta interrotta. Riprova.';
        } else {
            return 'Errore di rete. Controlla la tua connessione.';
        }
    }

    // Mostra messaggio di sistema
    showMessage(elementId, text, type) {
        const element = document.getElementById(elementId);
        element.innerHTML = `<div class="message ${type}">${text}</div>`;
        setTimeout(() => {
            element.innerHTML = '';
        }, CONFIG.MESSAGE_DISPLAY_TIME);
    }
}

// Istanza globale
let travelApp;

// Inizializzazione quando il DOM è caricato
document.addEventListener('DOMContentLoaded', () => {
    travelApp = new TravelAssistant();
});

// Esporta funzioni globali per compatibilità con HTML
window.toggleAuthMode = () => travelApp?.toggleAuthMode();
window.handleAuth = () => travelApp?.handleAuth();
window.logout = () => travelApp?.logout();
window.sendMessage = () => travelApp?.sendMessage();
window.clearChat = () => travelApp?.clearChat();
window.insertQuickText = (text) => travelApp?.insertQuickText(text);
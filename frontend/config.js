// Configuration file for Travel AI Assistant Frontend
const CONFIG = {
    // API Settings
    API_URL: '/api',
    
    // UI Settings
    MESSAGE_DISPLAY_TIME: 5000, // ms
    CHAT_MAX_HEIGHT: '500px',
    
    // Quick Actions
    QUICK_ACTIONS: [
        { text: 'Pianifica un viaggio di 3 giorni a Roma', emoji: '🏛️', label: 'Roma' },
        { text: 'Suggerisci un weekend a Parigi', emoji: '🗼', label: 'Parigi' },
        { text: 'Viaggio di lavoro a Milano', emoji: '💼', label: 'Milano' },
        { text: 'Vacanza al mare in Grecia', emoji: '🏖️', label: 'Grecia' },
        { text: 'Itinerario culturale a Firenze', emoji: '🎨', label: 'Firenze' },
        { text: 'Avventura nelle Dolomiti', emoji: '🏔️', label: 'Dolomiti' }
    ],
    
    // Export Settings
    EXPORT_FORMATS: {
        MD: { type: 'md', icon: '📄', label: 'Markdown' },
        ICS: { type: 'ics', icon: '📅', label: 'Calendar' }
    },
    
    // Network Settings
    REQUEST_TIMEOUT: 30000, // 30 seconds
    RETRY_ATTEMPTS: 3,
    
    // Local Storage Keys
    STORAGE_KEYS: {
        SESSION_TOKEN: 'travel_session_token',
        USER_PREFERENCES: 'travel_user_preferences',
        LAST_TRIP_ID: 'travel_last_trip_id'
    },
    
    // Messages
    MESSAGES: {
        AUTH: {
            LOGIN_SUCCESS: 'Accesso effettuato con successo!',
            LOGOUT_SUCCESS: 'Logout effettuato',
            REGISTER_SUCCESS: 'Registrazione completata! Ora fai il login.',
            INVALID_CREDENTIALS: 'Username o password non validi',
            SESSION_EXPIRED: 'Sessione scaduta. Effettua nuovamente il login.',
            NETWORK_ERROR: 'Impossibile connettersi al server. Verifica che l\'API sia attiva su localhost:5000.'
        },
        TRAVEL: {
            TRIP_ACTIVE: '✈️ Viaggio attivo - Puoi modificarlo',
            NO_TRIP: '🌍 Nessun viaggio attivo - Descrivine uno nuovo',
            TRIP_FINALIZED: 'Viaggio finalizzato! Puoi iniziarne uno nuovo.',
            CHAT_CLEARED: 'Chat cancellata',
            PROCESSING: '🤔 L\'AI sta pensando...',
            FILE_DOWNLOADED: 'File scaricato con successo!'
        },
        CONNECTION: {
            ONLINE: '✅ Connessione ripristinata',
            OFFLINE: '❌ Connessione persa'
        }
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
} else if (typeof window !== 'undefined') {
    window.CONFIG = CONFIG;
}
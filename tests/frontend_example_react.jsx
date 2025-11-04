/**
 * React Frontend Example for Travel AI Assistant
 * 
 * This is a complete example showing how to integrate with the Flask API.
 * You can use this with Vite, Create React App, or Next.js.
 * 
 * Installation:
 * npm create vite@latest travel-ai-frontend -- --template react
 * cd travel-ai-frontend
 * npm install axios react-router-dom
 * 
 * Then copy these components into src/
 */

import { useState, useEffect, createContext, useContext } from 'react';
import axios from 'axios';

// Configure axios
const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Auth Context
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await api.get('/auth/status');
      if (response.data.authenticated) {
        setUser(response.data.user);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    const response = await api.post('/auth/login', { username, password });
    if (response.data.success) {
      setUser(response.data.user);
    }
    return response.data;
  };

  const register = async (username, password, email) => {
    const response = await api.post('/auth/register', { username, password, email });
    return response.data;
  };

  const logout = async () => {
    await api.post('/auth/logout');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);

// Login Component
export function LoginPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        const result = await login(username, password);
        if (!result.success) {
          setError(result.error || 'Login fallito');
        }
      } else {
        const result = await register(username, password, email);
        if (result.success) {
          setIsLogin(true);
          setPassword('');
          alert('Registrazione completata! Ora puoi fare il login.');
        } else {
          setError(result.error || 'Registrazione fallita');
        }
      }
    } catch (error) {
      setError(error.response?.data?.error || 'Errore di connessione');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-500 to-purple-600">
      <div className="bg-white p-8 rounded-lg shadow-2xl w-full max-w-md">
        <h1 className="text-3xl font-bold text-center mb-6 text-gray-800">
          🌍 Travel AI Assistant
        </h1>

        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setIsLogin(true)}
            className={`flex-1 py-2 px-4 rounded ${
              isLogin ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'
            }`}
          >
            Login
          </button>
          <button
            onClick={() => setIsLogin(false)}
            className={`flex-1 py-2 px-4 rounded ${
              !isLogin ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'
            }`}
          >
            Registrati
          </button>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 mb-2">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
              minLength={3}
            />
          </div>

          {!isLogin && (
            <div className="mb-4">
              <label className="block text-gray-700 mb-2">Email (opzionale)</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          )}

          <div className="mb-6">
            <label className="block text-gray-700 mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
              minLength={6}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 disabled:bg-gray-400"
          >
            {loading ? 'Attendere...' : isLogin ? 'Accedi' : 'Registrati'}
          </button>
        </form>
      </div>
    </div>
  );
}

// Main Travel Assistant Component
export function TravelAssistant() {
  const { user, logout } = useAuth();
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentTrip, setCurrentTrip] = useState(null);
  const [showHistory, setShowHistory] = useState(false);

  const handleNewQuery = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setMessages([...messages, { role: 'user', content: query }]);
    
    try {
      const response = await api.post('/travel/query', { query });
      
      if (response.data.success) {
        setCurrentTrip(response.data);
        setMessages([
          ...messages,
          { role: 'user', content: query },
          { role: 'assistant', content: response.data.plan }
        ]);
        setQuery('');
      } else {
        alert(response.data.error);
      }
    } catch (error) {
      alert(error.response?.data?.error || 'Errore di connessione');
    } finally {
      setLoading(false);
    }
  };

  const handleInteraction = async (input) => {
    setLoading(true);
    setMessages([...messages, { role: 'user', content: input }]);

    try {
      const response = await api.post('/travel/interact', { input });
      
      if (response.data.success) {
        const { intent, response: aiResponse, updated_plan } = response.data;
        
        setMessages([
          ...messages,
          { role: 'user', content: input },
          { role: 'assistant', content: updated_plan || aiResponse }
        ]);

        if (intent === 'done') {
          await api.post('/travel/finalize');
          setCurrentTrip(null);
          alert('Viaggio finalizzato! Puoi trovarlo nella cronologia.');
        } else if (intent === 'new_trip') {
          setCurrentTrip(null);
          setMessages([]);
        }
      }
    } catch (error) {
      alert(error.response?.data?.error || 'Errore di connessione');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-800">🌍 Travel AI Assistant</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-600">Ciao, {user?.username}!</span>
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Cronologia
            </button>
            <button
              onClick={logout}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {showHistory ? (
          <HistoryView onClose={() => setShowHistory(false)} />
        ) : (
          <>
            {/* Chat Messages */}
            <div className="bg-white rounded-lg shadow-lg p-6 mb-4" style={{ minHeight: '400px', maxHeight: '600px', overflowY: 'auto' }}>
              {messages.length === 0 ? (
                <div className="text-center text-gray-500 mt-20">
                  <p className="text-xl mb-4">👋 Benvenuto!</p>
                  <p>Descrivi il tuo viaggio ideale e ti aiuterò a pianificarlo.</p>
                  <p className="text-sm mt-2">Esempio: "Voglio andare a Parigi per 5 giorni con un budget di 1000€"</p>
                </div>
              ) : (
                messages.map((msg, idx) => (
                  <div
                    key={idx}
                    className={`mb-4 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}
                  >
                    <div
                      className={`inline-block p-4 rounded-lg ${
                        msg.role === 'user'
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-200 text-gray-800'
                      }`}
                      style={{ maxWidth: '80%' }}
                    >
                      <pre className="whitespace-pre-wrap font-sans">{msg.content}</pre>
                    </div>
                  </div>
                ))
              )}
              {loading && (
                <div className="text-center text-gray-500">
                  <div className="inline-block animate-pulse">Generando risposta...</div>
                </div>
              )}
            </div>

            {/* Input Area */}
            <div className="bg-white rounded-lg shadow-lg p-4">
              {currentTrip ? (
                <InteractionInput onSubmit={handleInteraction} disabled={loading} />
              ) : (
                <form onSubmit={handleNewQuery} className="flex gap-2">
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Descrivi il tuo viaggio..."
                    className="flex-1 px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                    disabled={loading}
                  />
                  <button
                    type="submit"
                    disabled={loading}
                    className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
                  >
                    Inizia
                  </button>
                </form>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

// Interaction Input Component
function InteractionInput({ onSubmit, disabled }) {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    onSubmit(input);
    setInput('');
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Modifica il piano, chiedi informazioni, o scrivi 'done' per finalizzare..."
        className="flex-1 px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
        disabled={disabled}
      />
      <button
        type="submit"
        disabled={disabled}
        className="px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-400"
      >
        Invia
      </button>
    </form>
  );
}

// History View Component
function HistoryView({ onClose }) {
  const [trips, setTrips] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const response = await api.get('/history');
      if (response.data.success) {
        setTrips(response.data.trips);
        setStats(response.data.stats);
      }
    } catch (error) {
      alert('Errore caricamento cronologia');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center">Caricamento...</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Cronologia Viaggi</h2>
        <button
          onClick={onClose}
          className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
        >
          Chiudi
        </button>
      </div>

      {stats && (
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-blue-100 p-4 rounded text-center">
            <div className="text-3xl font-bold text-blue-600">{stats.total_trips}</div>
            <div className="text-gray-600">Viaggi Totali</div>
          </div>
          <div className="bg-green-100 p-4 rounded text-center">
            <div className="text-3xl font-bold text-green-600">{stats.completed_trips}</div>
            <div className="text-gray-600">Completati</div>
          </div>
          <div className="bg-purple-100 p-4 rounded text-center">
            <div className="text-3xl font-bold text-purple-600">{stats.total_interactions}</div>
            <div className="text-gray-600">Interazioni</div>
          </div>
        </div>
      )}

      <div className="space-y-4">
        {trips.map((trip) => (
          <div key={trip.id} className="border rounded p-4 hover:bg-gray-50">
            <div className="flex justify-between items-start mb-2">
              <h3 className="font-bold text-lg">{trip.destination}</h3>
              <span className={`px-3 py-1 rounded text-sm ${
                trip.status === 'completed' ? 'bg-green-200 text-green-800' : 'bg-yellow-200 text-yellow-800'
              }`}>
                {trip.status === 'completed' ? 'Completato' : 'In corso'}
              </span>
            </div>
            <div className="text-sm text-gray-600 mb-2">
              {new Date(trip.created_at).toLocaleDateString('it-IT')}
            </div>
            {trip.latest_plan && (
              <details className="mt-2">
                <summary className="cursor-pointer text-blue-600 hover:text-blue-800">
                  Mostra piano
                </summary>
                <pre className="mt-2 p-3 bg-gray-100 rounded text-sm whitespace-pre-wrap">
                  {trip.latest_plan}
                </pre>
              </details>
            )}
          </div>
        ))}
      </div>

      {trips.length === 0 && (
        <div className="text-center text-gray-500 py-8">
          Nessun viaggio ancora. Inizia a pianificare!
        </div>
      )}
    </div>
  );
}

// Main App Component
export default function App() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Caricamento...</div>
      </div>
    );
  }

  return user ? <TravelAssistant /> : <LoginPage />;
}

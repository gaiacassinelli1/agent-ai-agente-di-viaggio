# Travel AI Assistant - Web API

## 🚀 Quick Start

### Backend Setup (Flask API)

1. **Installa le dipendenze:**
```bash
pip install -r requirements_api.txt
```

2. **Configura le variabili d'ambiente:**
Aggiungi al file `.env`:
```
FLASK_SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-key
```

3. **Avvia il server:**
```bash
# Development
python venv/api_flask.py

# Production
gunicorn -w 4 -b 0.0.0.0:5000 venv.api_flask:app
```

Il server sarà disponibile su `http://localhost:5000`

### Frontend Setup (React)

1. **Crea il progetto React:**
```bash
npm create vite@latest travel-ai-frontend -- --template react
cd travel-ai-frontend
npm install axios react-router-dom
```

2. **Installa Tailwind CSS (opzionale ma consigliato):**
```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

3. **Copia il codice:**
- Copia il contenuto di `frontend_example_react.jsx` in `src/App.jsx`
- Avvolgi l'app con `<AuthProvider>` in `src/main.jsx`

4. **Avvia il frontend:**
```bash
npm run dev
```

Il frontend sarà disponibile su `http://localhost:5173`

## 📡 API Endpoints

### Authentication

#### Register
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "string",
  "password": "string",
  "email": "string" (optional)
}

Response:
{
  "success": true/false,
  "message": "string"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}

Response:
{
  "success": true,
  "user": {
    "id": number,
    "username": "string",
    "email": "string"
  },
  "has_active_trip": boolean,
  "active_trip": {...} (if exists)
}
```

#### Logout
```http
POST /api/auth/logout

Response:
{
  "success": true,
  "message": "Logout effettuato con successo"
}
```

#### Check Auth Status
```http
GET /api/auth/status

Response:
{
  "authenticated": true/false,
  "user": {...} (if authenticated)
}
```

### Travel Planning

#### New Travel Query
```http
POST /api/travel/query
Content-Type: application/json

{
  "query": "Voglio andare a Parigi per 5 giorni con 1000€"
}

Response:
{
  "success": true,
  "plan": "string (piano di viaggio generato)",
  "trip_id": number,
  "travel_info": {
    "destination": "string",
    "start_date": "string",
    "end_date": "string",
    "budget": number
  }
}
```

#### Interact with Plan
```http
POST /api/travel/interact
Content-Type: application/json

{
  "input": "Voglio aggiungere una visita al Louvre"
}

Response:
{
  "success": true,
  "intent": "modification|information|new_trip|done",
  "response": "string",
  "updated_plan": "string" (if modification)
}
```

#### Finalize Trip
```http
POST /api/travel/finalize

Response:
{
  "success": true,
  "message": "Viaggio finalizzato",
  "trip_data": {...}
}
```

### History & Stats

#### Get Trip History
```http
GET /api/history

Response:
{
  "success": true,
  "trips": [
    {
      "id": number,
      "destination": "string",
      "status": "active|completed",
      "created_at": "timestamp",
      "latest_plan": "string"
    }
  ],
  "stats": {
    "total_trips": number,
    "completed_trips": number,
    "total_interactions": number
  }
}
```

#### Load Specific Trip
```http
GET /api/trip/{trip_id}

Response:
{
  "success": true,
  "trip": {...},
  "plan": {...}
}
```

## 🔒 Security Features

- **Password Hashing:** SHA-256 (upgradable to bcrypt)
- **Session Management:** HTTP-only cookies
- **CORS Protection:** Configured for specific origins
- **Input Validation:** All inputs validated server-side
- **SQL Injection Protection:** Parameterized queries

## 🏗️ Architecture

```
┌─────────────────┐
│  React Frontend │
│   (Port 5173)   │
└────────┬────────┘
         │ HTTP/REST
         ↓
┌─────────────────┐
│   Flask API     │
│   (Port 5000)   │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ SessionManager  │
│  (Business Logic)│
└────────┬────────┘
         │
    ┌────┴────┬────────────┬──────────┐
    ↓         ↓            ↓          ↓
┌────────┐┌──────────┐┌─────────┐┌──────────┐
│TravelDB││AuthMgr  ││TripMgr  ││Orchestr. │
└────────┘└──────────┘└─────────┘└──────────┘
    │
    ↓
┌─────────────────┐
│  SQLite DB      │
│ (travel_assistant│
│     .db)        │
└─────────────────┘
```

## 📦 Deployment

### Docker (Recommended)

1. **Create Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements_api.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements_api.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "venv.api_flask:app"]
```

2. **Build and run:**
```bash
docker build -t travel-ai-api .
docker run -p 5000:5000 --env-file .env travel-ai-api
```

### Heroku

```bash
# Create Procfile
echo "web: gunicorn venv.api_flask:app" > Procfile

# Deploy
heroku create travel-ai-api
heroku config:set FLASK_SECRET_KEY=xxx OPENAI_API_KEY=xxx
git push heroku main
```

### Vercel (Frontend)

```bash
cd travel-ai-frontend
npm run build
vercel --prod
```

## 🧪 Testing

### Test API with curl

```bash
# Health check
curl http://localhost:5000/api/health

# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}' \
  -c cookies.txt

# New trip (requires login cookie)
curl -X POST http://localhost:5000/api/travel/query \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"query":"Voglio andare a Roma per 3 giorni"}'
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...
FLASK_SECRET_KEY=random-secret-key

# Optional
FLASK_ENV=production
DATABASE_PATH=travel_assistant.db
MAX_CONTENT_LENGTH=16777216  # 16MB
SESSION_COOKIE_SECURE=True   # For HTTPS
```

### CORS Configuration

In `api_flask.py`, modify for production:
```python
CORS(app, 
     origins=['https://yourdomain.com'],
     supports_credentials=True)
```

## 📊 Monitoring

### Add logging
```python
import logging

logging.basicConfig(
    filename='api.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

### Performance metrics
```bash
# Install
pip install flask-monitor

# Use
from flask_monitor import Monitor
Monitor(app)
```

## 🐛 Troubleshooting

### CORS Errors
- Ensure `withCredentials: true` in axios
- Check CORS origin configuration
- Verify cookies are being sent

### Database Locked
- SQLite doesn't handle concurrent writes well
- Consider PostgreSQL for production
- Or use connection pooling

### Session Lost
- Check cookie settings
- Verify session timeout
- Use Redis for distributed sessions

## 📝 Next Steps

1. ✅ Test the API locally
2. ⏳ Add rate limiting (Flask-Limiter)
3. ⏳ Implement refresh tokens
4. ⏳ Add email verification
5. ⏳ Create admin dashboard
6. ⏳ Add payment integration
7. ⏳ Deploy to production

## 🤝 Contributing

Feel free to extend this API with:
- WebSocket support for real-time chat
- Multi-language support
- PDF export for travel plans
- Calendar integration
- Weather API integration
- Flight/hotel booking APIs

## 📄 License

MIT License - Feel free to use in your projects!

# Login System for Travel AI Assistant

Sistema completo di autenticazione e persistenza dati per Travel AI Assistant.

## 📁 Struttura

```
login/
├── __init__.py              # Package initialization
├── database.py              # SQLite database manager
├── auth_manager.py          # User authentication
├── trip_manager.py          # Trip and plan management
├── auth_cli.py              # CLI authentication interface
├── example_integration.py   # Integration example
└── README.md               # This file
```

## 🗄️ Database Schema

### Tables

#### **users**
- `id` - Primary key
- `username` - Unique username
- `password_hash` - SHA-256 hashed password
- `email` - Optional email
- `created_at` - Registration timestamp
- `last_login` - Last login timestamp

#### **trips**
- `id` - Primary key
- `user_id` - Foreign key to users
- `destination` - Destination city
- `country` - Destination country
- `start_date` - Trip start date
- `end_date` - Trip end date
- `departure_city` - Departure city
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp
- `is_active` - Active status

#### **plans**
- `id` - Primary key
- `trip_id` - Foreign key to trips
- `plan_content` - Full plan text
- `version` - Version number (auto-incremented)
- `created_at` - Creation timestamp

#### **interactions**
- `id` - Primary key
- `trip_id` - Foreign key to trips
- `user_input` - User's input
- `intent` - Detected intent (modification/information/new_trip/done)
- `response` - System response
- `created_at` - Creation timestamp

## 🚀 Quick Start

### 1. Basic Usage

```python
from login import TravelDB, AuthManager, TripManager
from login.auth_cli import AuthCLI

# Initialize
db = TravelDB("travel_assistant.db")
auth_manager = AuthManager(db)
trip_manager = TripManager(db)
auth_cli = AuthCLI(db, auth_manager)

# Authenticate user
user = auth_cli.run()

if user:
    print(f"Welcome, {user['username']}!")
    
    # Create a trip
    trip_id = trip_manager.create_trip(
        user_id=user['id'],
        destination="Paris",
        country="France",
        start_date="2025-11-15",
        end_date="2025-11-19"
    )
    
    # Save a plan
    plan_id = trip_manager.save_plan(
        trip_id=trip_id,
        plan_content="Your travel plan here..."
    )
```

### 2. Running the Example

```bash
cd login
python example_integration.py
```

## 🔌 Integration with Main App

### Step 1: Add to main.py imports

```python
from login import TravelDB, AuthManager, TripManager
from login.auth_cli import AuthCLI
```

### Step 2: Initialize before main loop

```python
def main():
    # Initialize login system
    db = TravelDB("travel_assistant.db")
    auth_manager = AuthManager(db)
    trip_manager = TripManager(db)
    auth_cli = AuthCLI(db, auth_manager)
    
    # Authenticate
    user = auth_cli.run()
    if not user:
        return
    
    user_id = user['id']
    
    # Rest of your main() code...
```

### Step 3: Save trips and plans

```python
# After process_travel_request()
trip_id = trip_manager.create_trip(
    user_id=user_id,
    destination=travel_info['destination'],
    country=travel_info['country'],
    start_date=travel_info['start_date'],
    end_date=travel_info['end_date']
)

# Save the generated plan
trip_manager.save_plan(trip_id, travel_plan)

# Save user interactions
trip_manager.save_interaction(
    trip_id=trip_id,
    user_input=user_input,
    intent=intent,
    response=response
)
```

## 📊 Features

### Authentication
- ✅ User registration with password hashing
- ✅ Secure login
- ✅ Password change
- ✅ User deletion

### Trip Management
- ✅ Create trips with details
- ✅ Track active trips
- ✅ Trip history
- ✅ Deactivate/delete trips

### Plan Versioning
- ✅ Save multiple versions of plans
- ✅ Retrieve latest or all versions
- ✅ Automatic version numbering

### Interaction History
- ✅ Save all user interactions
- ✅ Track intents and responses
- ✅ Full conversation history

### Analytics
- ✅ User statistics
- ✅ Trip count
- ✅ Favorite destinations
- ✅ Visit frequency

## 🔒 Security Notes

⚠️ **Current Implementation:**
- Uses SHA-256 for password hashing
- Suitable for personal/demo use

🔐 **For Production:**
- Use `bcrypt` or `argon2` instead of SHA-256
- Add salt to passwords
- Implement session tokens
- Add rate limiting
- Use environment variables for sensitive data

### Upgrading Security

```bash
pip install bcrypt
```

```python
import bcrypt

def hash_password(self, password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(self, password: str, hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), hash.encode())
```

## 🧪 Testing

### Manual Testing

```python
from login import TravelDB, AuthManager

db = TravelDB(":memory:")  # In-memory database for testing
auth = AuthManager(db)

# Test registration
assert auth.register("testuser", "password123") == True
assert auth.register("testuser", "password456") == False  # Duplicate

# Test login
user = auth.login("testuser", "password123")
assert user is not None
assert user['username'] == "testuser"

# Test wrong password
assert auth.login("testuser", "wrongpass") is None
```

## 📈 Future Enhancements

- [ ] Email verification
- [ ] Password reset via email
- [ ] Social login (Google, GitHub)
- [ ] Trip sharing between users
- [ ] Export trips to PDF/JSON
- [ ] Calendar integration
- [ ] Budget tracking
- [ ] Photo gallery per trip
- [ ] Multi-language support
- [ ] Web dashboard

## 🐛 Troubleshooting

### Database locked error
- Ensure only one connection is active
- Use `check_same_thread=False` in SQLite connection

### Password not hiding in terminal
- `getpass` might not work in some IDEs
- Fallback to regular input is provided

### Permission errors
- Check write permissions for database file
- Database file will be created in current directory

## 📝 License

Part of Travel AI Assistant project.

## 👥 Contributing

To add new features:
1. Add methods to appropriate manager class
2. Update database schema if needed
3. Add to example_integration.py
4. Update this README

## 🆘 Support

For issues or questions, check:
- Database schema in `database.py`
- Integration example in `example_integration.py`
- Main app integration guide above

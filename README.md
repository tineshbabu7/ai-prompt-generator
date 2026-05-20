# AI Prompt Generator

Turn rough ideas into powerful, structured AI prompts instantly. Built with **FastAPI** (backend) + **Vanilla HTML/JS** (frontend).

---

## Features

- 🔐 JWT-based authentication (login & register)
- 🤖 Real OpenAI GPT-3.5 prompt enhancement
- 🗄️ SQLite database with SQLAlchemy ORM
- 🔑 Secure password hashing with bcrypt
- 📚 Prompt library — save & manage your best prompts
- 🕘 Prompt history — every generated prompt is automatically recorded

---

## Project Structure

```
ai-prompt-generator/
├── backend/
│   ├── main.py           # FastAPI app & routes
│   ├── auth.py           # JWT & password hashing
│   ├── database.py       # SQLAlchemy setup
│   ├── models.py         # DB models (User, Prompt, PromptHistory)
│   ├── schemas.py        # Pydantic schemas
│   ├── prompt_engine.py  # OpenAI integration
│   ├── create_tables.py  # DB table creation script
│   ├── requirements.txt
│   └── .env              # ← your secrets (never commit this)
└── frontend/
    ├── index.html        # Login page
    ├── signup.html       # Registration page
    ├── home.html         # Landing / marketing page
    ├── prompt.html       # Main app
    ├── css/styles.css
    └── js/
        ├── app.js
        ├── login.js
        ├── signup.js
        ├── forgot-password.js
        └── live-background.js
```

---

## Setup

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 2. Configure `.env`

```env
SECRET_KEY=your-super-secret-jwt-key
DATABASE_URL=sqlite:///./app.db
OPENAI_API_KEY=sk-...
```

### 3. Create the database & a test user

```bash
python create_tables.py
python create_user.py
```

### 4. Run the backend

```bash
uvicorn main:app --reload
```

API will be live at: `http://127.0.0.1:8000`  
Docs at: `http://127.0.0.1:8000/docs`

### 5. Open the frontend

Open `frontend/index.html` in your browser (or use VS Code **Live Server**).

---

## API Endpoints

| Method | Endpoint              | Auth | Description                |
|--------|-----------------------|------|----------------------------|
| GET    | `/`                   | No   | Health check               |
| POST   | `/register`           | No   | Create account             |
| POST   | `/login`              | No   | Get JWT token              |
| POST   | `/reset-password`     | No   | Reset password             |
| POST   | `/auth/google`        | No   | Google OAuth login         |
| POST   | `/enhance-prompt`     | Yes  | Enhance a prompt (auto-saves to history) |
| POST   | `/suggest-questions`  | Yes  | Get improvement questions  |
| POST   | `/library/save`       | Yes  | Save prompt to library     |
| GET    | `/library`            | Yes  | Get all saved prompts      |
| DELETE | `/library/{id}`       | Yes  | Delete a saved prompt      |
| GET    | `/history`            | Yes  | Get prompt history         |
| DELETE | `/history/{id}`       | Yes  | Delete a history entry     |
| DELETE | `/history`            | Yes  | Clear all history          |

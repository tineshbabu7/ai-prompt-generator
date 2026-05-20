# AI Prompt Generator

Turn rough ideas into powerful, structured AI prompts instantly using OpenAI GPT models.  
Built with FastAPI (backend) and Vanilla HTML/CSS/JavaScript (frontend).

---

## Features

- JWT-based authentication system
- Secure login & registration
- OpenAI GPT-powered prompt enhancement
- Prompt improvement suggestions
- Prompt history tracking
- Save prompts to personal library
- SQLite database integration
- Password hashing with bcrypt
- REST API built using FastAPI
- Responsive frontend UI

---

## Tech Stack

### Backend
- Python
- FastAPI
- SQLAlchemy
- SQLite
- JWT Authentication
- Passlib / bcrypt
- OpenAI API

### Frontend
- HTML5
- CSS3
- Vanilla JavaScript

---

## Project Structure

```bash
ai-prompt-generator/
│
├── backend/
│   ├── main.py
│   ├── auth.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── prompt_engine.py
│   ├── create_tables.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── index.html
│   ├── signup.html
│   ├── home.html
│   ├── prompt.html
│   ├── forgot-password.html
│   │
│   ├── css/
│   │   └── styles.css
│   │
│   └── js/
│       ├── app.js
│       ├── login.js
│       ├── signup.js
│       ├── forgot-password.js
│       └── live-background.js
│
├── .gitignore
└── README.md
```

---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-prompt-generator.git
cd ai-prompt-generator
```

---

### 2. Create Virtual Environment

```bash
cd backend

python -m venv venv
```

Activate virtual environment:

#### Windows

```bash
venv\Scripts\activate
```

#### Mac/Linux

```bash
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Create a `.env` file inside the `backend/` folder:

```env
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///./app.db
OPENAI_API_KEY=your-openai-api-key
```

Important:
- Never upload `.env`
- Never expose API keys publicly

---

### 5. Create Database Tables

```bash
python create_tables.py
```

(Optional)

```bash
python create_user.py
```

---

### 6. Run the Backend Server

```bash
uvicorn main:app --reload
```

Backend will run at:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

---

### 7. Run the Frontend

Open:

```text
frontend/index.html
```

Recommended:
- VS Code Live Server extension

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/register` | Register new user |
| POST | `/login` | User login |
| POST | `/reset-password` | Reset password |
| POST | `/enhance-prompt` | Enhance AI prompt |
| POST | `/suggest-questions` | Generate improvement questions |
| GET | `/library` | Get saved prompts |
| POST | `/library/save` | Save prompt |
| DELETE | `/library/{id}` | Delete saved prompt |
| GET | `/history` | Get prompt history |
| DELETE | `/history/{id}` | Delete history item |

---

![Login Page](assets/screenshots/login.png)

![Prompt Generator](assets/screenshots/prompt.png)

![Prompt History](assets/screenshots/history.png)

---

## Security Features

- JWT token authentication
- Password hashing using bcrypt
- Protected API routes
- Environment variable protection
- Input validation using Pydantic

---

## Future Improvements

- Google OAuth integration
- Dark mode support
- Export prompts as PDF
- Multi-language support
- Cloud database deployment
- User profile customization

---

## Author

**Tinesh Babu**

GitHub:  
https://github.com/tineshbabu7

---

## License

This project is for educational and portfolio purposes.
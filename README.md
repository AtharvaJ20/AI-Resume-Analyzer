# AI Resume Analyser

Ever wondered why you're not getting callbacks? This app takes your resume, looks at your target role, and tells you exactly what's missing — no fluff, no generic advice. It uses Google Gemini under the hood to give you matched skills, real skill gaps, a learning roadmap, and the interview questions you should probably be preparing for.

---

## What it does

You paste your resume (or upload a PDF/DOCX), type in the role you're going for, and hit analyse. Within seconds you get:

- **What you already have** — skills that match the role
- **What's holding you back** — the gaps a hiring manager would notice
- **How to close those gaps** — a step-by-step roadmap, not just a list of buzzwords
- **What they'll ask you** — interview questions tailored to your specific target role

Everything gets saved to your account, so you can track how your resume evolves over time.

---

## Built with

- **Flask** for the backend
- **Google Gemini** (`gemini-3.6-flash`) for the AI analysis
- **TiDB Cloud** as the database (MySQL-compatible, serverless)
- **SQLAlchemy** to talk to the database
- **PyPDF2 + python-docx** to read uploaded files
- **Werkzeug** for password hashing
- Plain HTML/CSS with a light and dark theme

---

## Project structure

```
AI_Resume_Analyser/
├── app.py           # All the routes live here
├── ai.py            # The Gemini prompt and retry logic
├── db.py            # Database connection setup
├── models.py        # User and Report tables
├── templates/       # HTML pages (login, signup, dashboard, history)
├── static/
│   └── style.css    # Styling with light/dark theme support
├── .env             # Your secrets — never commit this
└── .gitignore
```

---

## Getting it running

### Step 1 — Clone and set up a virtual environment

```bash
git clone <your-repo-url>
cd AI_Resume_Analyser
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
```

### Step 2 — Install the dependencies

```bash
pip install flask sqlalchemy pymysql python-dotenv werkzeug PyPDF2 python-docx google-genai
```

### Step 3 — Create your `.env` file

Make a file called `.env` in the root folder and add these three things:

```
DATABASE_URL=mysql+pymysql://<username>:<password>@<host>:4000/<database>
SECRET_KEY=some-long-random-string
GOOGLE_API_KEY=your-gemini-api-key
```

A couple of things worth noting here:
- Get your Gemini API key from [ai.google.dev](https://ai.google.dev) — it's free to start
- If you're using TiDB Cloud, the username looks like `abc123.root` (not just `root`) — you'll find the exact format in the Connect dialog

### Step 4 — Create the database tables

Open your TiDB Cloud SQL editor and run this — **users first, then reports**, otherwise the foreign key will fail:

```sql
USE your_database;

CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(256) NOT NULL
);

CREATE TABLE IF NOT EXISTS reports (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    resume_text TEXT,
    result TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Step 5 — Run it

```bash
python app.py
```

Go to `http://localhost:5002` and you're in.

---

## How to use it

1. Sign up with your email and a password
2. Log in — you'll land on the dashboard
3. Paste your resume into the text box, or upload a `.pdf` / `.docx`
4. Type the role you're targeting (be specific — "Backend Engineer" gives better results than "developer")
5. Hit **Analyse Resume** and wait a few seconds
6. Check the **History** page anytime to look back at previous analyses

---

## A few things to know

- **Scanned PDFs won't work** — the app can only read text-based PDFs, not images of documents
- **If Gemini is slow**, the app will retry up to 3 times automatically before giving up
- **Don't commit your `.env` file** — it's in `.gitignore` already, but worth saying out loud
- The more specific your target role, the more useful the output. "Senior Backend Engineer at a fintech company" beats "engineer"

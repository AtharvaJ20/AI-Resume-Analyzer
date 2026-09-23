from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, redirect, session
from db import Base, engine, SessionLocal
import models
import PyPDF2
import json
import docx
import os
from werkzeug.security import generate_password_hash, check_password_hash
from ai import analyze_resume

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-in-production")

try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"[WARNING] Could not auto-create tables: {e}")

#Home
@app.route("/")
def home():
    if "user" in session:
        return redirect("/dashboard")
    return redirect("/login")

#----SIGNUP
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        db = SessionLocal()
        try:
            existing_user = db.query(models.User).filter_by(email=email).first()
            if existing_user:
                return "User already exists"

            user = models.User(email=email, password=generate_password_hash(password))
            db.add(user)
            db.commit()
        finally:
            db.close()

        return redirect("/login")

    return render_template("signup.html")

#----LOGIN
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        db = SessionLocal()
        try:
            user = db.query(models.User).filter_by(email=email).first()
            if user and check_password_hash(user.password, password):
                session["user"] = email
                return redirect("/dashboard")
        finally:
            db.close()

        return "Invalid Credentials"

    return render_template("login.html")

#DASHBOARD
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/login")

    result = None

    if request.method == "POST":
        user_goal = request.form.get("role")
        resume_text = request.form.get("resume")

        file = request.files.get("file")

        #FILE HANDLING
        if file and file.filename != "":
            if file.filename.endswith(".pdf"):
                try:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() or ""
                    resume_text = text
                except Exception as e:
                    result = {"error": f"PDF error: {str(e)}"}

            elif file.filename.endswith(".docx"):
                try:
                    doc = docx.Document(file)
                    text = ""
                    for para in doc.paragraphs:
                        text += para.text + "\n"
                    resume_text = text
                except Exception as e:
                    result = {"error": f"Docx error: {str(e)}"}

            else:
                result = {"error": "Unsupported file type. Please upload a .pdf or .docx file."}

        if not result and resume_text and user_goal:
            try:
                result = analyze_resume(resume_text, user_goal)

                db = SessionLocal()
                try:
                    user = db.query(models.User).filter_by(email=session["user"]).first()
                    report = models.Report(
                        user_id=user.id,
                        resume_text=resume_text,
                        result=json.dumps(result)
                    )
                    db.add(report)
                    db.commit()
                finally:
                    db.close()

            except Exception as e:
                result = {"error": f"AI error: {str(e)}"}

    return render_template(
        "dashboard.html",
        user=session["user"],
        result=result
    )

#History
@app.route("/history")
def history():
    if "user" not in session:
        return redirect("/login")

    db = SessionLocal()
    try:
        user = db.query(models.User).filter_by(email=session["user"]).first()
        reports = db.query(models.Report).filter_by(user_id=user.id).all()

        parsed_reports = []
        for r in reports:
            try:
                parsed_result = json.loads(r.result)
            except:
                parsed_result = {}

            parsed_reports.append({
                "resume": r.resume_text,
                "result": parsed_result
            })
    finally:
        db.close()

    return render_template("history.html", reports=parsed_reports)

#logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True, port=5002)

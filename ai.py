from google import genai
from google.genai import types
import json
import time

def analyze_resume(resume_text, user_goal):
    client = genai.Client()

    prompt = f"""
You are a senior software engineer and hiring manager.

Evaluate resume based on user's goal

User goal : "{user_goal}"

STRICT RULES:
-Extract only relevant skill for this goal
-Remove irrelevant tools [excel for backend, etc]
-Identify real gaps
-Generate roadmaps only for missing fields
-Make output DIFFERENT based on goal

Return only JSON:
{{
"skills":[],
"missing_skills": [],
"roadmap":[],
"interview_questions":[]
}}

Resume:
{resume_text}

"""

    last_error = None
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction="You are a strict hiring manager.",
                    temperature=0.3,
                )
            )

            content = response.text.strip()
            start = content.find("{")
            end = content.rfind("}") + 1
            return json.loads(content[start:end])

        except Exception as e:
            last_error = e
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                time.sleep(3 * (attempt + 1))
                continue
            break

    return {
        "skills": [],
        "missing_skills": [],
        "roadmap": [],
        "interview_questions": [],
        "error": str(last_error)
    }

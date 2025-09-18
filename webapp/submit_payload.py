import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from webapp.app import app, generate_email

payload = {
    "role": "Data Scientist",
    "experience": "2+ years",
    "skills": "Python, Machine Learning, NLP, Data Analysis",
    "description": "We need someone to build ML models, analyze data, and deliver insights to stakeholders. Experience with feature engineering and deploying models is a plus.",
}

if __name__ == "__main__":
    # Print brief env info for sanity
    print("LLM_PROVIDER:", os.getenv("LLM_PROVIDER"))
    print("Has GEMINI_API_KEY:", bool(os.getenv("GEMINI_API_KEY")))

    with app.test_request_context("/generate-email", method="POST", json=payload):
        res = generate_email()
        status = getattr(res, "status_code", None)
        data = None
        if hasattr(res, "get_json"):
            data = res.get_json(silent=True)
        elif isinstance(res, tuple) and hasattr(res[0], "get_json"):
            data = res[0].get_json(silent=True)
            if len(res) > 1 and isinstance(res[1], int):
                status = res[1]
        print("STATUS:", status)
        if isinstance(data, dict) and "email" in data:
            print("\n=== GENERATED EMAIL ===\n")
            print(data["email"]) 
            print("\n=== END EMAIL ===\n")
        else:
            print("Response:", res)

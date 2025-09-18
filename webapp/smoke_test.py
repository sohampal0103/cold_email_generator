import os
import sys

# Ensure project root is on sys.path so `webapp` package can be imported
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from webapp.app import app, home, generate_email


def main():
    # Basic checks
    # GET /
    with app.test_request_context("/", method="GET"):
        result = home()
        if hasattr(result, "status_code"):
            print("GET / ->", result.status_code)
        else:
            # Rendered HTML string
            html = str(result)
            print("GET / -> 200 (rendered)")
            print("Index bytes:", len(html.encode("utf-8")))

    # POST /generate-email
    payload = {
        "role": "Data Scientist",
        "experience": "2+ years",
        "skills": "Python, Machine Learning, Data Analysis, NLP",
        "description": "We need someone to build ML models, do data analysis, and ship insights.",
    }
    with app.test_request_context("/generate-email", method="POST", json=payload):
        result2 = generate_email()
        status = getattr(result2, "status_code", None)
        data = None
        if hasattr(result2, "get_json"):
            data = result2.get_json(silent=True)
        elif isinstance(result2, tuple) and hasattr(result2[0], "get_json"):
            data = result2[0].get_json(silent=True)
            if len(result2) > 1 and isinstance(result2[1], int):
                status = result2[1]
        print("POST /generate-email ->", status or "unknown")
        if isinstance(data, dict):
            print("JSON keys:", list(data.keys()))
            preview = (data.get("email") or "")[:400]
            print("Email preview:\n", preview)
        else:
            print("Non-JSON or error response:", str(result2)[:400])


if __name__ == "__main__":
    # Ensure provider info is visible
    print("LLM_PROVIDER:", os.getenv("LLM_PROVIDER"))
    print("Has GEMINI_API_KEY:", bool(os.getenv("GEMINI_API_KEY")))
    main()

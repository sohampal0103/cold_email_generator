from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import pandas as pd
import uuid
import chromadb
from chromadb.config import Settings
from typing import Dict, Any, List

app = Flask(__name__)
load_dotenv()

# Quiet noisy logs/telemetry
os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')
os.environ.setdefault('CHROMA_TELEMETRY_DISABLED', 'true')
os.environ.setdefault('CHROMA_ANONYMIZED_TELEMETRY', 'false')
os.environ.setdefault('PYTHONWARNINGS', 'ignore')
import logging
logging.getLogger("chromadb").setLevel(logging.ERROR)
logging.getLogger("opentelemetry").setLevel(logging.ERROR)

# Get the absolute path to the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def initialize_llm():
    """Initialize an LLM: prefer provider from LLM_PROVIDER env; supports OpenAI and Gemini."""
    preferred = os.getenv("LLM_PROVIDER", "openai").lower()
    openai_key = os.getenv('OPENAI_API_KEY')
    google_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')

    def build_openai():
        if not openai_key:
            raise ValueError("OPENAI_API_KEY not found")
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        return ChatOpenAI(temperature=0.7, openai_api_key=openai_key, model_name=model)

    def build_gemini():
        if not google_key:
            raise ValueError("GOOGLE_API_KEY/GEMINI_API_KEY not found")
        model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        return ChatGoogleGenerativeAI(temperature=0.7, google_api_key=google_key, model=model)

    builders = [build_openai, build_gemini] if preferred == "openai" else [build_gemini, build_openai]
    last_err = None
    for builder in builders:
        try:
            return builder()
        except Exception as e:
            print(f"LLM init failed for {builder.__name__}: {e}")
            last_err = e
            continue
    raise last_err or RuntimeError("No LLM could be initialized")

def initialize_chroma_collection() -> chromadb.Collection:
    try:
        path = os.path.join(PROJECT_ROOT, 'vectorstore')
        client = chromadb.PersistentClient(path=path, settings=Settings(anonymized_telemetry=False, allow_reset=True))
        collection = client.get_or_create_collection(name="portfolio")
        try:
            _ = collection.count()
        except Exception as inner:
            print(f"Chroma store at {path} incompatible ({inner}); using a fresh store...")
            fresh = f"{path}_fresh"
            os.makedirs(fresh, exist_ok=True)
            client = chromadb.PersistentClient(path=fresh, settings=Settings(anonymized_telemetry=False, allow_reset=True))
            collection = client.get_or_create_collection(name="portfolio")
        return collection
    except Exception as e:
        print(f"Error initializing ChromaDB collection: {e}")
        raise

def populate_portfolio(collection: chromadb.Collection, df: pd.DataFrame) -> None:
    try:
        if not collection.count():
            for _, row in df.iterrows():
                collection.add(
                    documents=[row["Techstack"]],
                    metadatas=[{"links": row["Links"]}],
                    ids=[str(uuid.uuid4())]
                )
    except Exception as e:
        print(f"Error populating portfolio: {e}")
        raise

def get_relevant_links(collection: chromadb.Collection, skills: List[str], n_results: int = 2) -> List[Dict[str, Any]]:
    try:
        skills_text = ", ".join(skills)
        results = collection.query(query_texts=[skills_text], n_results=n_results)
        return results.get('metadatas', [[]])[0]
    except Exception as e:
        print(f"Error getting relevant links: {e}")
        raise

def generate_cold_email(job: Dict[str, Any], links: List[Dict[str, Any]], llm: ChatOpenAI) -> str:
    try:
        prompt_email = PromptTemplate.from_template(
            """
            Write a professional cold email for the following job opportunity. Be concise and direct.
            
            Job Details:
            - Role: {role}
            - Experience Required: {experience}
            - Required Skills: {skills}
            - Description: {description}
            
            Company Context:
            You are Anu, a business development executive at AtliQ. AtliQ is an AI & Software Consulting company 
            that helps businesses automate and optimize their processes. We have extensive experience in delivering 
            scalable solutions that reduce costs and improve efficiency.
            
            Portfolio Links to Include:
            {links}
            
            Instructions:
            1. Write a brief, professional cold email
            2. Focus on how AtliQ can help with their specific needs
            3. Include relevant portfolio links
            4. Keep it under 200 words
            5. Include a clear call to action
            
            Email Format:
            Subject: [Write a compelling subject]
            
            [Write the email body]
            
            Best regards,
            Anu
            Business Development Executive | AtliQ
            """
        )
        
        email_vars = {
            "role": job["role"],
            "experience": job["experience"],
            "skills": ", ".join(job["skills"]),
            "description": job["description"],
            "links": "\n".join([f"- {link['links']}" for link in links])
        }
        
        res = prompt_email | llm
        email = res.invoke(email_vars)
        return email.content
    except Exception as e:
        print(f"Error generating cold email: {e}")
        raise

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate-email', methods=['POST'])
def generate_email():
    try:
        data = request.json
        job = {
            "role": data['role'],
            "experience": data['experience'],
            "skills": data['skills'].split(','),
            "description": data['description']
        }
        llm = initialize_llm()
        collection = initialize_chroma_collection()
        df = pd.read_csv(os.path.join(PROJECT_ROOT, 'my_portfolio.csv'))
        populate_portfolio(collection, df)
        
        links = get_relevant_links(collection, job['skills'])
        email = generate_cold_email(job, links, llm)
        
        return jsonify({"email": email})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 
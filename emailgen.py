import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import pandas as pd
import uuid
import chromadb
from chromadb.config import Settings
import shutil
from typing import Dict, Any, List


load_dotenv()


os.environ.setdefault('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')
# Chroma/telemetry quieting
os.environ.setdefault('CHROMA_TELEMETRY_DISABLED', 'true')
os.environ.setdefault('CHROMA_ANONYMIZED_TELEMETRY', 'false')
os.environ.setdefault('PYTHONWARNINGS', 'ignore')
os.environ.setdefault('POSTHOG_DISABLED', 'true')

import logging
logging.getLogger("chromadb").setLevel(logging.ERROR)
logging.getLogger("opentelemetry").setLevel(logging.ERROR)

def initialize_llm():
    """Initialize an LLM. Try OpenAI first; if unavailable or quota exceeded, fallback to Gemini."""
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

    # Try preferred provider first
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

def load_webpage(url: str) -> str:
    """Load and extract content from a webpage."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        loader = WebBaseLoader(url, header_template=headers)
        return loader.load().pop().page_content
    except Exception as e:
        print(f"Error loading webpage: {e}")
        raise

def extract_job_details(page_data: str, llm: ChatOpenAI) -> Dict[str, Any]:
    """Extract job details from webpage content."""
    try:
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of a website.
            Your job is to extract the job postings and return them in JSON format containing the 
            following keys: `role`, `experience`, `skills` and `description`.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):    
            """
        )
        
        chain_extract = prompt_extract | llm
        res = chain_extract.invoke(input={'page_data': page_data})
        json_parser = JsonOutputParser()
        return json_parser.parse(res.content)
    except Exception as e:
        print(f"Error extracting job details: {e}")
        raise

def initialize_chroma_collection(path: str = './vectorstore') -> chromadb.Collection:
    """Initialize ChromaDB collection for portfolio with validation and fallback.

    - Disables anonymized telemetry to reduce noisy warnings.
    - Validates the collection by calling count(); on failure, falls back to a fresh store.
    """
    try:
        client = chromadb.PersistentClient(path=path, settings=Settings(anonymized_telemetry=False, allow_reset=True))
        collection = client.get_or_create_collection(name="portfolio")
        # Validate the store is compatible/healthy
        try:
            _ = collection.count()
        except Exception as inner:
            print(f"Chroma store at {path} seems incompatible ({inner}). Using a fresh store...")
            fresh_path = f"{path}_fresh"
            try:
                os.makedirs(fresh_path, exist_ok=True)
            except Exception:
                pass
            client = chromadb.PersistentClient(path=fresh_path, settings=Settings(anonymized_telemetry=False, allow_reset=True))
            collection = client.get_or_create_collection(name="portfolio")
        return collection
    except Exception as e:
        print(f"Error initializing ChromaDB collection: {e}")
        raise

def populate_portfolio(collection: chromadb.Collection, df: pd.DataFrame) -> None:
    """Populate the portfolio collection with data from DataFrame."""
    try:
        if not collection.count():
            for _, row in df.iterrows():
                collection.add(
                    documents=[row["Techstack"]],
                    metadatas=[{"links": row["Links"]}],
                    ids=[str(uuid.uuid4())]
                )
            print("Portfolio collection populated successfully")
    except Exception as e:
        print(f"Error populating portfolio: {e}")
        raise

def get_relevant_links(collection: chromadb.Collection, skills: List[str], n_results: int = 2) -> List[Dict[str, Any]]:
    """Get relevant portfolio links based on job skills."""
    try:
        skills_text = ", ".join(skills)
        results = collection.query(query_texts=[skills_text], n_results=n_results)
        return results.get('metadatas', [[]])[0]
    except Exception as e:
        print(f"Error getting relevant links: {e}")
        raise

def generate_cold_email(job: Dict[str, Any], links: List[Dict[str, Any]], llm: ChatOpenAI) -> str:
    """Generate a cold email based on job description and portfolio links."""
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
        
        chain_email = prompt_email | llm
        email = chain_email.invoke(email_vars)
        return email.content
    except Exception as e:
        print(f"Error generating cold email: {e}")
        raise

def main():
    """Main function to orchestrate the email generation process."""
    try:
        print("Initializing LLM (OpenAI or Gemini)...")
        llm = initialize_llm()
        
        print("\nUsing sample job description for testing...")
        sample_job = {
            "role": "Senior Software Engineer",
            "experience": "5+ years",
            "skills": ["Python", "React", "Node.js", "MongoDB"],
            "description": "We are looking for a Senior Software Engineer to join our team. The ideal candidate will have strong experience in full-stack development, with expertise in Python, React, Node.js, and MongoDB. They will be responsible for designing and implementing scalable solutions, mentoring junior developers, and contributing to architectural decisions."
        }
        
        print("\nInitializing ChromaDB collection...")
        collection = initialize_chroma_collection()
        
        print("\nReading portfolio data...")
        df = pd.read_csv("my_portfolio.csv")
        
        print("\nPopulating portfolio collection...")
        populate_portfolio(collection, df)
        
        print("\nGetting relevant links...")
        links = get_relevant_links(collection, sample_job['skills'])
        print(f"Found {len(links)} relevant portfolio links")
        
        print("\nGenerating cold email...")
        email = generate_cold_email(sample_job, links, llm)
        print("\nGenerated Cold Email:")
        print("-" * 80)
        print(email)
        print("-" * 80)
        
    except Exception as e:
        print(f"\nAn error occurred in main: {str(e)}")
        import traceback
        print("\nFull traceback:")
        print(traceback.format_exc())

if __name__ == "__main__":
    main()
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()


llm = ChatOpenAI(
    temperature=0, 
    openai_api_key=os.getenv('OPENAI_API_KEY'), 
    model_name="gpt-4o-mini"  
)


response = llm.invoke("Tell me about VIT University, Vellore...")
print(response.content)
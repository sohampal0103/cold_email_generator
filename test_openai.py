import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

def test_openai_connection():
    """Test the OpenAI connection and model."""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ OPENAI_API_KEY not found in environment variables")
            print("Please set your OpenAI API key in the .env file")
            return False
        
        print("🔑 OpenAI API key found")
        
        llm = ChatOpenAI(
            temperature=0.7,
            openai_api_key=api_key,
            model_name="gpt-4o-mini"
        )
        
        print("🤖 Testing OpenAI model...")
        response = llm.invoke("Hello! Please respond with 'OpenAI integration successful!'")
        print(f"✅ Response: {response.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing OpenAI: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing OpenAI Integration...")
    success = test_openai_connection()
    
    if success:
        print("\n🎉 OpenAI integration is working!")
        print("You can now use the cold email generator with OpenAI models.")
    else:
        print("\n💡 Please check your OpenAI API key and try again.")

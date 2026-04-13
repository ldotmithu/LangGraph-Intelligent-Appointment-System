from dotenv import load_dotenv
import os
load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("GROQ_API_KEY")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT")

LLM_MODEL = "openai/gpt-oss-120b"
TEMPERATURE = 0.9

BACKEND_URL = ""
    

    
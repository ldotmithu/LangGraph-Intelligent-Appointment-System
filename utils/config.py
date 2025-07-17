from dotenv import load_dotenv
import os
load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("GROQ_API_KEY")

LLM_MODEL = "qwen/qwen3-32b"
TEMPERATURE = 0.6

BACKEND_URL = ""
    

    
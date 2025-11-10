import os 
from dotenv import load_dotenv, find_dotenv

def load_env():
    """ Load environment variables from .env file"""
    _ = load_dotenv(find_dotenv())
    
def get_ollama_api_url():
    """ Get the Ollama API URL from environment variables or use default"""
    load_env()
    ollama_api_url = os.environ("OLLAMA_API_URL", "http://localhost:11434")

def get_model_name():
    """ Get the model name from the environment varibales or use default"""
    load_env()
    model_name = os.environ('OLLAMA_MODEL', 'llama3.2:b')
    return model_name

def get_serper_api_key():
    """Get the serper api key from environment variables"""
    load_env()
    serper_api_key = os.getenv('SERPER_API_KEY')
    return serper_api_key



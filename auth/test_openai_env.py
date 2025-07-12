import os
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
import openai # Needed for the specific error exception

# Find the .env file (it will search in the current directory and parent directories)
# You might need to adjust the path if your project structure is different
# For example, if auth/ is a subdirectory and config/ is in the root, it might be:
# dotenv_path = find_dotenv('.env') or dotenv_path = Path('../config/secrets.env')
# For this structure: auth/test_openai_env.py, config/secrets.env
# We need to go up one directory from auth/ to find the config/ directory
# and then specify the secrets.env file.
# Assuming the script is run from the project root or a sub-directory,
# and config/secrets.env is relative to the root.
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(project_root, 'config', 'secrets.env')


# Load environment variables from the specified .env file
load_dotenv(dotenv_path)

def test_openai_api_key():
    """
    Tests the OpenAI API key by attempting to list models.
    """
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables.")
        return False

    try:
        # Initialize the OpenAI client with the API key
        client = OpenAI(api_key=api_key)
        
        # Attempt to list models to verify the API key
        client.models.list()
        print("OpenAI API Key is valid and working!")
        return True
    except openai.AuthenticationError:
        print("OpenAI API Key is invalid or expired.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

if __name__ == "__main__":
    if test_openai_api_key():
        print("API key test passed!")
    else:
        print("API key test failed.")


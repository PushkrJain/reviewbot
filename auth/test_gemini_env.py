import cohere
import os
from dotenv import load_dotenv

load_dotenv("config/secrets.env")

co = cohere.Client(os.getenv("COHERE_API_KEY"))

response = co.chat(message="Summarize bubble sort in Java.")
print("✅ Cohere Response:\n", response.text)
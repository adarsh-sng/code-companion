import os
from google import genai
from dotenv import load_dotenv
from google.genai import errors

load_dotenv()
api_key=os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

try:
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents="give me a joke"
    )
    print(response.text)
except errors.ClientError as e:
    if e.code == 429:
        print("Rate limit hit! I need to slow down or wait a minute.")
    else:
        print(f"An API error occurred: {e}")

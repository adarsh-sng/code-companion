import os
import sys
from google import genai
from dotenv import load_dotenv
from google.genai import errors,types

def main()->None:
  load_dotenv()
  api_key=os.environ.get("GEMINI_API_KEY")
  client = genai.Client(api_key=api_key)
  verbose:bool=False
  if len(sys.argv)<2:
     print("No prompt given")
     sys.exit(1)
  if len(sys.argv)==3 and sys.argv[2]=="--verbose":
    verbose=True
  prompt=sys.argv[1]
  messages: list[types.Content] = [
    types.Content(role="user", parts=[types.Part(text=prompt)])
]
  try:
    response = client.models.generate_content(
      model="gemini-2.5-flash", 
      contents=messages,
    )
    print(response.text)
    if verbose:
      print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
      print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
  except errors.ClientError as e:
    if e.code == 429:
        print("Rate limit hit! I need to slow down or wait a minute.")
    else:
        print(f"An API error occurred: {e}")

main()
import os
import sys
from google import genai
from dotenv import load_dotenv
from google.genai import errors, types
from functions.get_file_info import schema_get_files_info
from functions.get_file_content import schema_get_files_content
from functions.run_python_file import schema_run_python_file
from functions.write_files import schema_write_files
from call_function import call_function


def main() -> None:
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    verbose: bool = False
    system_prompt = """
  You are a helpful AI coding agent.
  When a user asks a question or makes a request, make a function call plan. You can perform the following operations:
  - List files and directories
  - Read the content of a file
  - Write content to a file
  - Run a python file with optional CLI arguments and get the output
  All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
  """
    if len(sys.argv) < 2:
        print("No prompt given")
        sys.exit(1)
    if len(sys.argv) == 3 and sys.argv[2] == "--verbose":
        verbose = True
    prompt = sys.argv[1]
    messages: list[types.Content] = [
        types.Content(role="user", parts=[types.Part(text=prompt)])
    ]
    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_files_content,
            schema_run_python_file,
            schema_write_files,
        ],
    )
    try:
        for _ in range(20):
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=messages,
                config=types.GenerateContentConfig(
                    tools=[available_functions], system_instruction=system_prompt
                ),
            )
            if response.candidates:
                messages.append(response.candidates[0].content)
            if response is None or response.usage_metadata is None:
                print("response is malinformed")
                return
            if verbose:
                print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
                print(
                    f"Response tokens: {response.usage_metadata.candidates_token_count}"
                )
            if response.function_calls:
                for function_call_part in response.function_calls:
                    function_response = call_function(
                        function_call_part, verbose=verbose
                    )
                    if verbose:
                        print(
                            f"-> {function_response.parts[0].function_response.response}"
                        )  # these could be none so handle exception later
                    tool_message = types.Content(
                        role="tool",
                        parts=[
                            types.Part.from_function_response(
                                name=function_call_part.name, response=function_response.parts[0].function_response.response
                            )
                        ],
                    )
                    messages.append(tool_message)
            else:
                print(response.text)
                return

    except errors.ClientError as e:
        if e.code == 429:
            print("Rate limit hit! I need to slow down or wait a minute.")
        else:
            print(f"An API error occurred: {e}")


main()

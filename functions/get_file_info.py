import os
from google.genai import types

def get_files_info(working_directory: str, directory: str = ".") -> str:
    try:
        working_dir_abs = os.path.realpath(working_directory)
        target_dir = os.path.realpath(os.path.join(working_dir_abs, directory))
        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a valid directory'

        valid_target_dir = os.path.commonpath([working_dir_abs, target_dir]) == working_dir_abs
        if not valid_target_dir:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        print(f'Success: "{directory}" is within the working directory')
        file_info_list = []
        for file in os.listdir(target_dir):
          file_path = os.path.join(target_dir, file)
          is_dir: bool = os.path.isdir(file_path)
          size = os.path.getsize(file_path)
          file_info_list.append(f"Name: {file}, IsDir: {is_dir}, Size: {size} bytes")
        
    except Exception as e:
        return f"Error processing paths: {str(e)}"
    
schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in a specified directory relative to the working directory, providing file size and directory status",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory path to list files from, relative to the working directory (default is the working directory itself)",
            ),
        },
    ),
)
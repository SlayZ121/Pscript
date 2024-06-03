import os
import zipfile
import json
import google.generativeai as genai
from flask import Flask
from secretkey import secretkey


app = Flask(__name__)
app.secret_key = secretkey

genai.configure(api_key=secretkey)

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    },
]

system_instruction = "Friendly"

model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                              generation_config=generation_config,
                              system_instruction=system_instruction,
                              safety_settings=safety_settings)


def get_ai_response(prompt):
    convo = model.start_chat()

    convo.send_message(prompt)
    return convo.last.text


def generate_files(file_content, file_name):
    base_dir = "generated_app"
    os.makedirs(base_dir, exist_ok=True)
    full_path = os.path.join(base_dir, file_name)
    with open(full_path, 'w', encoding='utf-8') as f:  # Specify encoding as UTF-8
        f.write(file_content)
    return base_dir



def zip_directory(directory_path):
    zip_filename = directory_path + '.zip'
    with zipfile.ZipFile(zip_filename, 'w') as zipf:
        for root, _, files in os.walk(directory_path):
            for file in files:
                full_path = os.path.join(root, file)
                zipf.write(full_path, os.path.relpath(full_path, directory_path))
    return zip_filename


def generate_application(user_input):
    # Generate file content
    prompt = f"Generate the file structure and content for a {user_input} application."
    response = get_ai_response(prompt)
    print(response)

    # Parse the response to get the file content
    file_content = response.strip()  # Use the response directly

    # Generate file
    app_dir = generate_files(file_content, user_input + ".py")

    # Zip the generated file
    zip_path = zip_directory(app_dir)

    return zip_path



if __name__ == '__main__':
    user_input = input("Enter what you want to build/generate: ")
    zip_path = generate_application(user_input)
    if zip_path:
        print(f'Application generated successfully! Zip file saved at: {zip_path}')

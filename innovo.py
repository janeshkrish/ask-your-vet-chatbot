from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import json
import requests
import google.generativeai as genai
d
# Load environment variables
load_dotenv()

# Initialize Flask
app = Flask(__name__, template_folder="templates")

# Get API Key
api_key = os.getenv("GEMINI_API_KEY")
if api_key is None:
    raise ValueError("API Key not found. Check your environment variables or .env file.")

API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

genai.configure(api_key=api_key)

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-2.0-flash",
  generation_config=generation_config,
)

def GenerateResponse(input_text):
    response = model.generate_content([
        "consider yourself as a veterinary doctor. You are handling issues and queries and problems of the patients. Just answer according to it. Your name is Innovo.",
        "input: who are you",
        "output: Hello! I'm Innovo, a veterinary doctor here to help you with your animal companions. How can I assist you today?",
        f"input: {input_text}",
        "output: ",
    ])
    return response.text.strip()

def save_chat_history(user_input, response):
    history_file = "chat_history.json"
    try:
        with open(history_file, "r") as file:
            chat_history = json.load(file)
    except FileNotFoundError:
        chat_history = []

    chat_history.append({"user": user_input, "bot": response})

    with open(history_file, "w") as file:
        json.dump(chat_history, file, indent=4)

@app.route("/get_chat_history", methods=["GET"])
def get_chat_history():
    try:
        with open("chat_history.json", "r") as file:
            chat_history = json.load(file)
        return jsonify(chat_history)
    except FileNotFoundError:
        return jsonify([])

# Route for serving the frontend
@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/chat")
def chat_page():
    return render_template("index.html")

# API endpoint for handling chat requests
@app.route("/get_response", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")
    response = GenerateResponse(user_input)
    
    # Save the chat history
    save_chat_history(user_input, response)
    
    # Get the updated chat history
    try:
        with open("chat_history.json", "r") as file:
            chat_history = json.load(file)
    except FileNotFoundError:
        chat_history = []
    
    # Return the response along with the chat history
    return jsonify({"response": response, "chat_history": chat_history})

if __name__ == "__main__":
    app.run(debug=True)

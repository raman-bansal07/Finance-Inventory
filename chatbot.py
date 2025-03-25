import os
from openai import OpenAI
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify

# Load environment variables
load_dotenv()

# Define a Blueprint for the chatbot
chatbot_bp = Blueprint('chatbot', __name__)

# Retrieve API key
api_key = os.getenv("GITHUB_TOKEN")
if not api_key:
    raise ValueError("GitHub token not found. Please set GITHUB_TOKEN in the .env file.")

# Initialize OpenAI client
client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=api_key,
)


system_message = {
    "role": "system",
    "content": (
        "Ensure giving short replies, and give plain text."
        " without special characters, emojis, or profanity, plain-text. "
        "You are an expert financial advisor specializing in inventory management, finance, and market trends. "
        "You provide insightful advice on optimizing inventory levels, reducing costs, and maximizing profitability. "
        "You analyze market trends, offer investment strategies, and help users make informed financial decisions. "
        "You also provide updates on daily market movements, economic indicators, and industry news to keep users ahead. "
        "Ensure responses are clear, short, precise, data-driven, and actionable."
    ),
}

@chatbot_bp.route('/api/chatbot', methods=['POST'])
def process_chatbot_message():
    """Process user message and return AI response"""
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"response": "No message provided"}), 400

    user_message = {
        "role": "user",
        "content": data['message']
    }

    try:
        response = client.chat.completions.create(
            messages=[system_message, user_message],
            model="gpt-4o",
            temperature=0.7,
            max_tokens=1096,
            top_p=1
        )
        
        bot_reply = response.choices[0].message.content
        return jsonify({"response": bot_reply})
    except Exception as e:
        return jsonify({"response": f"Error: {str(e)}"}), 500

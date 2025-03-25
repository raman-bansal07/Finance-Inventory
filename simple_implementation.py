# If you prefer a simpler implementation without external API calls,
# you can use this file instead of chatbot_api.py

from flask import Blueprint, request, jsonify

# Create a Blueprint for the chatbot routes
chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/api/chatbot', methods=['POST'])
def process_chatbot_message():
    """
    Process a message sent to the chatbot and return a response
    """
    # Get the message from the request
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"response": "No message provided"}), 400
    
    user_message = data['message']
    
    # Generate a response based on the message content
    response = get_simple_response(user_message)
    
    return jsonify({"response": response})

def get_simple_response(message):
    """
    Generate a simple response based on keywords in the message
    """
    message_lower = message.lower()
    
    # Greeting responses
    if any(word in message_lower for word in ['hello', 'hi', 'hey']):
        return "Hello! How can I help you with your inventory today?"
    
    # Farewell responses
    elif any(word in message_lower for word in ['bye', 'goodbye']):
        return "Goodbye! Feel free to chat again if you need assistance."
    
    # Inventory-related responses
    elif 'low stock' in message_lower or 'running out' in message_lower:
        return "I can help you identify items with low stock. Would you like to see a report of items that need reordering?"
    
    elif 'out of stock' in message_lower:
        return "I can show you items that are currently out of stock. Would you like to create purchase orders for these items?"
    
    elif 'add item' in message_lower or 'new item' in message_lower:
        return "To add a new item to your inventory, go to the Items section and click on 'Add Item'. Would you like me to guide you through the process?"
    
    elif 'delete' in message_lower or 'remove' in message_lower:
        return "To remove an item from your inventory, find the item in the Items list and click the delete button. Please note that this action cannot be undone."
    
    elif 'update' in message_lower or 'edit' in message_lower:
        return "You can update item details by clicking on the edit button next to any item in your inventory list."
    
    elif 'search' in message_lower or 'find' in message_lower:
        return "You can search for items using the search bar at the top of the dashboard. You can search by name, SKU, or other properties."
    
    # Help responses
    elif any(word in message_lower for word in ['help', 'support', 'guide']):
        return "I'm here to help! You can ask me about inventory management, stock levels, or specific items. What would you like to know?"
    
    # General inventory questions
    elif 'inventory' in message_lower or 'stock' in message_lower:
        return "I can help you manage your inventory. You can ask about stock levels, item details, or how to add new items."
    
    # Value-related questions
    elif 'value' in message_lower or 'worth' in message_lower:
        return "Your inventory value is calculated based on the cost price of all items in stock. You can view the total value on your dashboard."
    
    # Default response
    else:
        return "I'm not sure I understand. Could you rephrase your question about inventory management? You can ask about stock levels, adding items, or generating reports."


import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import random

app = Flask(__name__)
CORS(app)  # allow frontend (Netlify) to reach this server

# Load chat history
if os.path.exists("chats.json"):
    with open("chats.json") as f:
        chats = json.load(f)
else:
    chats = []

# Load bot memory
if os.path.exists("bot_memory.json"):
    with open("bot_memory.json") as f:
        bot_memory = json.load(f)
        # Normalize keys to lowercase
        bot_memory = {k.lower(): v for k, v in bot_memory.items()}
else:
    bot_memory = {}

# Pending learning message
pending_learning = None

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/chat", methods=["POST"])
def chat():
    global pending_learning
    data = request.get_json()
    message = data.get("message", "").lower()

    # Save user message
    chats.append({"user": message})

    # If bot has a pending message to learn, save this message as the correct reply
    if pending_learning:
        prev_user = pending_learning
        bot_memory.setdefault(prev_user, [])
        if message not in bot_memory[prev_user]:
            bot_memory[prev_user].append(message)
        pending_learning = None

    # Bot reply logic
    if message in bot_memory:
        reply = random.choice(bot_memory[message])
    else:
        reply = "I don't know yet."
        pending_learning = message  # mark for learning next

    # Save bot reply
    chats.append({"bot": reply})

    # Save JSON files
    save_json("chats.json", chats)
    save_json("bot_memory.json", bot_memory)

    return jsonify({"reply": reply})

@app.route("/")
def index():
    return render_template("frontend.html")

if __name__ == "__main__":
    app.run(debug=True, port=8080)

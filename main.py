from flask import Flask, request
import requests
import google.generativeai as genai
import os

app = Flask(__name__)

# Your credentials
WHATSAPP_TOKEN = "EAANmHKM3fHMBRU3mDjZCsjyZAJw8OvtipmBnaZCwnD4NrqdEL6i1hZAH2dHZAag9HpET9vHvI2kAM1qZAiA1fRQZCbER8WmrvpdQOCiqU2PfDAkvmmNtqqFgeZCWZCVU0uOlRvZBNjTmckUiNycEQKWmDb1FmbbNMZAASMzH3FIYgvtfS5Tr5jSNoMf4KolZBl4pMLdaZCvmFAIH1hUNZAFNMGfZC81TuR1bSefRSZCNrJZCPfhPs42NIcic19fLRTPSJ4LGISc7EtGIwePnnCkDDKTqSBzQ65vwP"
PHONE_NUMBER_ID = "1071726452692866"
VERIFY_TOKEN = "smartbotng123"
GEMINI_API_KEY = "AIzaSyCz9jO-Iaj0j5J102joO2qekYDDj6RGOb0"

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="""You are SmartBotNG, a helpful WhatsApp assistant for online skills marketers in Nigeria.
    You help answer questions about digital skills courses, pricing, enrollment, and payments.
    Keep responses short, friendly and professional.
    Always respond in the same language the customer uses.""",
)


def send_whatsapp_message(to, message):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message},
    }
    requests.post(url, headers=headers, json=data)


def get_ai_response(user_message):
    response = model.generate_content(user_message)
    return response.text


@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        if "messages" in value:
            message = value["messages"][0]
            from_number = message["from"]
            if message["type"] == "text":
                user_text = message["text"]["body"]
                ai_reply = get_ai_response(user_text)
                send_whatsapp_message(from_number, ai_reply)
    except Exception as e:
        print(f"Error: {e}")
    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

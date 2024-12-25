import os
import json
from flask import Flask, request
from twilio.rest import Client
from telebot import TeleBot
from cryptography.fernet import Fernet
from pyngrok import ngrok

# Configuration
TWILIO_SID = "your_twilio_account_sid"
TWILIO_TOKEN = "your_twilio_auth_token"
TWILIO_NUMBER = "your_twilio_phone_number"
TELEGRAM_TOKEN = "your_telegram_bot_token"
PASSWORD = "error_404_ot"
SECRET_KEY = Fernet.generate_key()  # Clé de chiffrement
cipher_suite = Fernet(SECRET_KEY)

# Twilio Client
twilio_client = Client(TWILIO_SID, TWILIO_TOKEN)

# Telegram Bot
bot = TeleBot(TELEGRAM_TOKEN)

# Flask App
app = Flask(__name__)

# Vérification du mot de passe
def check_password(input_password):
    return input_password == PASSWORD

# Chiffrer les données
def encrypt_data(data):
    return cipher_suite.encrypt(data.encode()).decode()

# Déchiffrer les données
def decrypt_data(data):
    return cipher_suite.decrypt(data.encode()).decode()

# Endpoint pour traiter les demandes de Telegram
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Bienvenue dans le bot OTP. Veuillez entrer le mot de passe pour continuer.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if check_password(message.text):
        bot.reply_to(message, "Accès autorisé. Entrez le numéro de téléphone à appeler.")
        bot.register_next_step_handler(message, process_phone_number)
    else:
        bot.reply_to(message, "Mot de passe incorrect.")

def process_phone_number(message):
    phone_number = message.text
    bot.reply_to(message, f"Appel en cours pour {phone_number}. Attendez le SMS.")
    send_call(phone_number)
    # Simulation d'envoi d'un OTP
    otp = "123456"
    encrypted_otp = encrypt_data(otp)
    bot.send_message(message.chat.id, f"Code OTP chiffré : {encrypted_otp}")

# Appel Twilio pour récupérer l'OTP
def send_call(phone_number):
    twilio_client.calls.create(
        to=phone_number,
        from_=TWILIO_NUMBER,
        twiml=f"<Response><Say>Votre code OTP est 1-2-3-4-5-6.</Say></Response>"
    )

# Flask Webhook pour Telegram
@app.route(f"/{TELEGRAM_TOKEN}", methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = json.loads(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# Démarrer ngrok et définir le webhook Telegram
def start_ngrok():
    public_url = ngrok.connect(5000).public_url
    print(f"Webhook URL : {public_url}/{TELEGRAM_TOKEN}")
    bot.remove_webhook()
    bot.set_webhook(url=f"{public_url}/{TELEGRAM_TOKEN}")

if __name__ == "__main__":
    # Lancer ngrok et Flask
    start_ngrok()
    app.run(port=5000)

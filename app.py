from flask import Flask
import requests

app = Flask(__name__)

@app.route('/')
def home():
    ip = requests.get('https://api.ipify.org').text
    return f"SERVER IP: {ip}"

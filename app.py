from flask import Flask, request, jsonify, render_template
import base64
from io import BytesIO
from PIL import Image
import os
import re
import json
import google.generativeai as genai
from dotenv import load_dotenv
import random

words = ["CANETA", "LIVRO", "TELEFONE", "COMPUTADOR", "BICICLETA", "MESA", "CADEIRA", "RELÓGIO", "ÓCULOS", "BALÃO", "CHAVE", "BOLSA", "SAPATO", "CHAPÉU", 
         "GUARDA-CHUVA", "ESPONJA", "TESOURA", "ESCOVA", "FACA", "MARTELO", "OLHO", "NARIZ", "BOCA", "MÃO", "PÉ", "ORELHA", "BRAÇO", "PERNA", "CABELO",
         "LÁBIO", "DENTE", "UNHA", "SOBRANCELHA", "MAÇÃ", "BANANA", "PIZZA", "BOLO", "SORVETE", "CHOCOLATE", "HAMBÚRGUER", "BATATA", "GATO",  "CACHORRO", 
         "PÁSSARO", "PEIXE", "BORBOLETA", "ABELHA", "SAPO", "COBRA", "ELEFANTE", "GIRAFA", "LEÃO", "TIGRE", "MACACO", "PANDA", "GOLFINHO", "RATO", "CORUJA", 
         "CAVALO", "URSO", "CAMISETA", "CALÇA", "VESTIDO", "SAIA", "SHORTS", "CASACO", "BLUSA", "MEIA", "JAQUETA", "TERNO"];

app = Flask(__name__)

load_dotenv()

gemini_api_key = os.getenv('GEMINI_API_KEY')
if not gemini_api_key:
    raise ValueError("A chave de API GEMINI_API_KEY não foi configurada.")

genai.configure(api_key=gemini_api_key)

model = genai.GenerativeModel("gemini-pro-vision")

@app.route('/generate_word')
def generate_random_word():
    random_word = random.choice(words)
    return jsonify(word=random_word)

def check_with_model(image):
    image_path = "imagem.png"
    image.save(image_path, format="PNG")

    buffered = BytesIO()
    image.save(buffered, format="PNG")
    image_content = buffered.getvalue()

    response = model.generate_content(
        ["""Adivinhe o que está desenhado nesta imagem e caso não houver nada ainda no desenho responda '...'. 
         Responda só a palavra com suas acentuações e em maiúsculo, sem colocar ponto final 
         por exemplo, se achar que é um gato responda somente 'GATO'""", image],
        stream=True
    )
    response.resolve()

    if not response.candidates:
        return "Resposta Inválida"
    
    prediction = response.text.strip()
    return prediction

def decode_image(data_url):
    header, encoded = data_url.split(',', 1)
    data = base64.b64decode(encoded)
    image = Image.open(BytesIO(data))
    return image

@app.route('/check_drawing', methods=['POST'])
def check_drawing():
    data = request.get_json()
    image_data = data['image']
    guessed_word = data['guessed_word']
    image = decode_image(image_data)

    prediction = check_with_model(image)

    correct = prediction.upper() == guessed_word.upper()

    return jsonify(prediction=prediction, correct=correct)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
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

words = ["LÁPIS", "LIVRO", "TELEFONE", "COMPUTADOR", "BICICLETA", "MESA", "CADEIRA", "RELÓGIO", "ÓCULOS", "BALÃO", "CHAVE", "BOLSA", "SAPATO", "CHAPÉU", 
         "GUARDA-CHUVA", "TESOURA", "ESCOVA", "GARFO", "MARTELO", "OLHO", "NARIZ", "BOCA", "MÃO", "PÉ", "ORELHA", "BRAÇO", "PERNA", "CABELO",
         "DENTE", "SOBRANCELHA", "MAÇÃ", "BANANA", "PIZZA", "BOLO", "SORVETE", "CHOCOLATE", "HAMBÚRGUER", "BATATA", "GATO",  "CACHORRO", 
         "PÁSSARO", "PEIXE", "BORBOLETA", "ABELHA", "SAPO", "COBRA", "ELEFANTE", "GIRAFA", "LEÃO", "TIGRE", "MACACO", "PANDA", "GOLFINHO", "RATO", 
         "CAVALO", "URSO", "CAMISETA", "CALÇA", "VESTIDO", "SAIA", "CASACO", "BLUSA", "MEIA", "TERNO"]

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

safe = [
    {
        "category": "HARM_CATEGORY_DANGEROUS",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    }
]

app = Flask(__name__)

load_dotenv()

gemini_api_key = os.getenv('GEMINI_API_KEY')
if not gemini_api_key:
    raise ValueError("A chave de API GEMINI_API_KEY não foi configurada.")

genai.configure(api_key=gemini_api_key)

model = genai.GenerativeModel(
    model_name="gemini-pro-vision", 
    generation_config=generation_config,
    safety_settings=safe)

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
         Responda só a palavra com suas acentuações e SEMPRE em maiúsculo, sem colocar ponto final 
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
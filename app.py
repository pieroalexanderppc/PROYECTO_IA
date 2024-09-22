from flask import Flask, jsonify, request, render_template
from logic import *

app = Flask(__name__)

# Base de conocimiento inicial
knowledge = And(regla_rojo, regla_negro, regla_par, regla_impar)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/preguntas')
def preguntas():
    return render_template('preguntas.html')

@app.route('/adivina', methods=['POST'])
def adivina():
    global knowledge

    data = request.json
    pregunta = data['pregunta']
    respuesta = data['respuesta']

    # Actualizar el conocimiento con la respuesta
    knowledge = actualizar_conocimiento(knowledge, pregunta, respuesta)

    # Intentar deducir la carta solo si ya se han hecho todas las preguntas
    resultado = deducir_carta(knowledge)

    return jsonify({"resultado": resultado})

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, jsonify, request, render_template
from logic import *  # Importa tu lógica
from game import check_knowledge  # Importa la función de verificación

app = Flask(__name__)

# Define tu conocimiento inicial
knowledge = And()  # Aquí podrías definir tu conocimiento inicial como lo hiciste antes

@app.route('/')
def index():
    return render_template('home.html')  # Asegúrate de que este archivo existe

@app.route('/preguntas')
def preguntas():
    return render_template('preguntas.html')  # Asegúrate de que este archivo existe

# Ruta para procesar la adivinanza
@app.route('/adivina', methods=['POST'])
def adivina():
    data = request.json
    answer = data['answer']
    
    # Aquí debes incluir tu lógica de juego y devolver la respuesta
    possible_cards = check_knowledge(knowledge)  # Obtener cartas posibles
    return jsonify(possible_cards)  # Devuelve las cartas posibles

if __name__ == '__main__':
    app.run(debug=True)

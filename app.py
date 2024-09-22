from flask import Flask, jsonify, request, render_template
from logic import *  # Asegúrate de que `logic.py` tiene la lógica necesaria

suits = ["Corazones", "Diamantes", "Tréboles", "Picas"]
values = ["As", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

knowledge = And()

def initialize_knowledge():
    global knowledge
    knowledge = And()
    for value in values:
        knowledge.add(Or(*(Symbol(f"{value}{suit}") for suit in suits)))

    for value in values:
        for s1 in suits:
            for s2 in suits:
                if s1 != s2:
                    knowledge.add(Implication(Symbol(f"{value}{s1}"), Not(Symbol(f"{value}{s2}"))))

    for suit in suits: 
        for v1 in values:
            for v2 in values:
                if v1 != v2:
                    knowledge.add(Implication(Symbol(f"{v1}{suit}"), Not(Symbol(f"{v2}{suit}"))))

initialize_knowledge()

def check_knowledge(knowledge):
    possible_cards = []
    for value in values:
        for suit in suits:
            symbol = Symbol(f"{value}{suit}")
            if model_check(knowledge, symbol):
                possible_cards.append(f"{value} de {suit}")
    return possible_cards

def add_question_knowledge(question, answer):
    global knowledge
    print(f"Pregunta recibida: {question}, Respuesta: {answer}")

    if answer.lower() not in ["sí", "no"]:
        print("Respuesta inválida. Debe ser 'sí' o 'no'.")
        return

    possible_before = check_knowledge(knowledge)
    print("Cartas posibles antes de la pregunta:", possible_before)

    if "trébol" in question:
        if answer == "sí":
            knowledge.add(Or(*(Symbol(f"{value}Tréboles") for value in values)))
        else:
            knowledge.add(Not(Or(*(Symbol(f"{value}Tréboles") for value in values))))

    elif "diamante" in question:
        if answer == "sí":
            knowledge.add(Or(*(Symbol(f"{value}Diamantes") for value in values)))
        else:
            knowledge.add(Not(Or(*(Symbol(f"{value}Diamantes") for value in values))))

    elif "corazón" in question:
        if answer == "sí":
            knowledge.add(Or(*(Symbol(f"{value}Corazones") for value in values)))
        else:
            knowledge.add(Not(Or(*(Symbol(f"{value}Corazones") for value in values))))

    elif "pica" in question:
        if answer == "sí":
            knowledge.add(Or(*(Symbol(f"{value}Picas") for value in values)))
        else:
            knowledge.add(Not(Or(*(Symbol(f"{value}Picas") for value in values))))

    elif "menor o igual a 5" in question:
        if answer == "sí":
            knowledge.add(Or(*(Symbol(value) for value in ["As", "2", "3", "4", "5"])))
        else:
            knowledge.add(Not(Or(*(Symbol(value) for value in ["As", "2", "3", "4", "5"]))))

    elif "rey" in question or "reina" in question or "jota" in question:
        if answer == "sí":
            knowledge.add(Or(Symbol("J"), Symbol("Q"), Symbol("K")))
        else:
            knowledge.add(Not(Or(Symbol("J"), Symbol("Q"), Symbol("K"))))

    elif "as" in question:
        if answer == "sí":
            knowledge.add(Symbol("As"))
        else:
            knowledge.add(Not(Symbol("As")))

    elif "entre 6 y 10" in question:
        if answer == "sí":
            knowledge.add(Or(*(Symbol(f"{value}{suit}") for value in ["6", "7", "8", "9", "10"] for suit in suits)))
        else:
            knowledge.add(Not(Or(*(Symbol(f"{value}{suit}") for value in ["6", "7", "8", "9", "10"] for suit in suits))))

    elif "carta roja" in question:
        if answer == "sí":
            knowledge.add(Or(*(Symbol(f"{value}Diamantes") for value in values) +
                              [Symbol(f"{value}Corazones") for value in values]))
        else:
            knowledge.add(Not(Or(*(Symbol(f"{value}Diamantes") for value in values) +
                                   [Symbol(f"{value}Corazones") for value in values])))

    elif "carta negra" in question:
        if answer == "sí":
            knowledge.add(Or(*(Symbol(f"{value}Picas") for value in values) +
                              [Symbol(f"{value}Tréboles") for value in values]))
        else:
            knowledge.add(Not(Or(*(Symbol(f"{value}Picas") for value in values) +
                                   [Symbol(f"{value}Tréboles") for value in values])))

    elif "carta de figura" in question:
        if answer == "sí":
            knowledge.add(Or(Symbol("J"), Symbol("Q"), Symbol("K")))
        else:
            knowledge.add(Not(Or(Symbol("J"), Symbol("Q"), Symbol("K"))))

    possible_after = check_knowledge(knowledge)
    print("Cartas posibles después de la pregunta:", possible_after)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/preguntas')
def preguntas():
    return render_template('preguntas.html')

@app.route('/adivina', methods=['POST'])
def adivina():
    data = request.json
    question = data.get('question')
    answer = data.get('answer')

    if not question or answer not in ["sí", "no"]:
        return jsonify({'error': 'Pregunta o respuesta inválida'}), 400

    add_question_knowledge(question, answer)

    possible_cards = check_knowledge(knowledge)
    return jsonify({'possible_cards': possible_cards})

@app.route('/reiniciar', methods=['POST'])
def reiniciar():
    initialize_knowledge()
    return jsonify({'message': 'Juego reiniciado'})

if __name__ == '__main__':
    app.run(debug=True)

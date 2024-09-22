from logic import *

# Definición de palos y valores en español
suits = ["Corazones", "Diamantes", "Tréboles", "Picas"]
values = ["As", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]  # Valores del As al Rey

# Crear símbolos para cada carta
symbols = []
for suit in suits:
    for value in values:
        symbols.append(Symbol(f"{value}{suit}"))

# Conocimientos sobre las cartas
knowledge = And()

# Cada carta pertenece a un palo y tiene un valor
for value in values:
    knowledge.add(Or(
        Symbol(f"{value}Corazones"),
        Symbol(f"{value}Diamantes"),
        Symbol(f"{value}Tréboles"),
        Symbol(f"{value}Picas")
    ))

# Solo una carta por valor y palo
for value in values:
    for s1 in suits:
        for s2 in suits:
            if s1 != s2:
                knowledge.add(
                    Implication(Symbol(f"{value}{s1}"), Not(Symbol(f"{value}{s2}")))
                )

# Solo un valor por carta en cada palo
for suit in suits: 
    for v1 in values:
        for v2 in values:
            if v1 != v2:
                knowledge.add(
                    Implication(Symbol(f"{v1}{suit}"), Not(Symbol(f"{v2}{suit}")))
                )

def check_knowledge(knowledge):
    possible_cards = []
    for value in values:
        for suit in suits:
            symbol = Symbol(f"{value}{suit}")
            if model_check(knowledge, symbol):
                possible_cards.append(f"{value} de {suit}")
    return possible_cards



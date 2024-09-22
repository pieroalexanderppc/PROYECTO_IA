import itertools

class Sentence():
    def evaluate(self, model):
        raise Exception("nothing to evaluate")

    def formula(self):
        return ""

    def symbols(self):
        return set()

    @classmethod
    def validate(cls, sentence):
        if not isinstance(sentence, Sentence):
            raise TypeError("must be a logical sentence")

    @classmethod
    def parenthesize(cls, s):
        def balanced(s):
            count = 0
            for c in s:
                if c == "(":
                    count += 1
                elif c == ")":
                    if count <= 0:
                        return False
                    count -= 1
            return count == 0
        if not len(s) or s.isalpha() or (
            s[0] == "(" and s[-1] == ")" and balanced(s[1:-1])
        ):
            return s
        else:
            return f"({s})"

class Symbol(Sentence):
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return isinstance(other, Symbol) and self.name == other.name

    def __hash__(self):
        return hash(("symbol", self.name))

    def __repr__(self):
        return self.name

    def evaluate(self, model):
        try:
            return bool(model[self.name])
        except KeyError:
            raise EvaluationException(f"variable {self.name} not in model")

    def formula(self):
        return self.name

    def symbols(self):
        return {self.name}

class Not(Sentence):
    def __init__(self, operand):
        Sentence.validate(operand)
        self.operand = operand

    def __eq__(self, other):
        return isinstance(other, Not) and self.operand == other.operand

    def __hash__(self):
        return hash(("not", hash(self.operand)))

    def __repr__(self):
        return f"Not({self.operand})"

    def evaluate(self, model):
        return not self.operand.evaluate(model)

    def formula(self):
        return "¬" + Sentence.parenthesize(self.operand.formula())

    def symbols(self):
        return self.operand.symbols()

class And(Sentence):
    def __init__(self, *conjuncts):
        for conjunct in conjuncts:
            Sentence.validate(conjunct)
        self.conjuncts = list(conjuncts)

    def __eq__(self, other):
        return isinstance(other, And) and self.conjuncts == other.conjuncts

    def __hash__(self):
        return hash(
            ("and", tuple(hash(conjunct) for conjunct in self.conjuncts))
        )

    def __repr__(self):
        conjunctions = ", ".join(
            [str(conjunct) for conjunct in self.conjuncts]
        )
        return f"And({conjunctions})"

    def add(self, conjunct):
        Sentence.validate(conjunct)
        self.conjuncts.append(conjunct)

    def evaluate(self, model):
        return all(conjunct.evaluate(model) for conjunct in self.conjuncts)

    def formula(self):
        if len(self.conjuncts == 1):
            return self.conjuncts[0].formula()
        return " ∧ ".join([Sentence.parenthesize(conjunct.formula())
                           for conjunct in self.conjuncts])

    def symbols(self):
        return set.union(*[conjunct.symbols() for conjunct in self.conjuncts])

class Or(Sentence):
    def __init__(self, *disjuncts):
        for disjunct in disjuncts:
            Sentence.validate(disjunct)
        self.disjuncts = list(disjuncts)

    def __eq__(self, other):
        return isinstance(other, Or) and self.disjuncts == other.disjuncts

    def __hash__(self):
        return hash(
            ("or", tuple(hash(disjunct) for disjunct in self.disjuncts))
        )

    def __repr__(self):
        disjuncts = ", ".join([str(disjunct) for disjunct in self.disjuncts])
        return f"Or({disjuncts})"

    def evaluate(self, model):
        return any(disjunct.evaluate(model) for disjunct in self.disjuncts)

    def formula(self):
        if len(self.disjuncts == 1):
            return self.disjuncts[0].formula()
        return " ∨ ".join([Sentence.parenthesize(disjunct.formula())
                            for disjunct in self.disjuncts])

    def symbols(self):
        return set.union(*[disjunct.symbols() for disjunct in self.disjuncts])

class Implication(Sentence):
    def __init__(self, antecedent, consequent):
        Sentence.validate(antecedent)
        Sentence.validate(consequent)
        self.antecedent = antecedent
        self.consequent = consequent

    def __eq__(self, other):
        return (isinstance(other, Implication)
                and self.antecedent == other.antecedent
                and self.consequent == other.consequent)

    def __hash__(self):
        return hash(("implies", hash(self.antecedent), hash(self.consequent)))

    def __repr__(self):
        return f"Implication({self.antecedent}, {self.consequent})"

    def evaluate(self, model):
        return ((not self.antecedent.evaluate(model))
                or self.consequent.evaluate(model))

    def formula(self):
        antecedent = Sentence.parenthesize(self.antecedent.formula())
        consequent = Sentence.parenthesize(self.consequent.formula())
        return f"{antecedent} => {consequent}"

    def symbols(self):
        return set.union(self.antecedent.symbols(), self.consequent.symbols())

class Biconditional(Sentence):
    def __init__(self, left, right):
        Sentence.validate(left)
        Sentence.validate(right)
        self.left = left
        self.right = right

    def __eq__(self, other):
        return (isinstance(other, Biconditional)
                and self.left == other.left
                and self.right == other.right)

    def __hash__(self):
        return hash(("biconditional", hash(self.left), hash(self.right)))

    def __repr__(self):
        return f"Biconditional({self.left}, {self.right})"

    def evaluate(self, model):
        return ((self.left.evaluate(model)
                 and self.right.evaluate(model))
                or (not self.left.evaluate(model)
                    and not self.right.evaluate(model)))

    def formula(self):
        left = Sentence.parenthesize(str(self.left))
        right = Sentence.parenthesize(str(self.right))
        return f"{left} <=> {right}"

    def symbols(self):
        return set.union(self.left.symbols(), self.right.symbols())

def model_check(knowledge, query):
    """Checks if knowledge base entails query."""

    def check_all(knowledge, query, symbols, model):
        """Checks if knowledge base entails query, given a particular model."""

        if not symbols:
            if knowledge.evaluate(model):
                return query.evaluate(model)
            return True
        else:
            remaining = symbols.copy()
            p = remaining.pop()

            model_true = model.copy()
            model_true[p] = True

            model_false = model.copy()
            model_false[p] = False

            return (check_all(knowledge, query, remaining, model_true) and
                    check_all(knowledge, query, remaining, model_false))

    symbols = set.union(knowledge.symbols(), query.symbols())

    return check_all(knowledge, query, symbols, dict())

# Definir los símbolos para características de las cartas
rojo = Symbol("rojo")
negro = Symbol("negro")
corazones = Symbol("corazones")
diamantes = Symbol("diamantes")
treboles = Symbol("treboles")
picas = Symbol("picas")
par = Symbol("par")
impar = Symbol("impar")

# Definir símbolos para algunas cartas específicas
as_carta = Symbol("As")
dos = Symbol("2")
tres = Symbol("3")
cuatro = Symbol("4")
cinco = Symbol("5")
seis = Symbol("6")
siete = Symbol("7")
ocho = Symbol("8")
nueve = Symbol("9")
diez = Symbol("10")

# Crear las reglas lógicas que representan las relaciones entre símbolos
regla_rojo = Biconditional(rojo, Or(corazones, diamantes))
regla_negro = Biconditional(negro, Or(treboles, picas))
regla_par = Biconditional(par, Or(dos, cuatro, seis, ocho, diez))
regla_impar = Biconditional(impar, Or(as_carta, tres, cinco, siete, nueve))

# Base de conocimiento inicial
knowledge = And(regla_rojo, regla_negro, regla_par, regla_impar)

# Función para actualizar la base de conocimiento basada en las respuestas
def actualizar_conocimiento(knowledge, pregunta, respuesta):
    if pregunta == "¿Es roja?":
        if respuesta:
            knowledge.add(rojo)
        else:
            knowledge.add(negro)
    elif pregunta == "¿Es de corazones?":
        if respuesta:
            knowledge.add(corazones)
        else:
            knowledge.add(diamantes)
    elif pregunta == "¿Es de tréboles?":
        if respuesta:
            knowledge.add(treboles)
        else:
            knowledge.add(picas)
    elif pregunta == "¿Es par?":
        if respuesta:
            knowledge.add(par)
        else:
            knowledge.add(impar)
    elif pregunta == "¿Es el cinco?":
        if respuesta:
            knowledge.add(cinco)
        else:
            knowledge.add(Not(cinco))
    return knowledge

# Función para verificar si la carta puede ser deducida
def deducir_carta(knowledge):
    posibles_cartas = [as_carta, dos, tres, cuatro, cinco, seis, siete, ocho, nueve, diez]
    for carta in posibles_cartas:
        if model_check(knowledge, carta):
            return f"La carta es el {carta}"
    return "No se ha podido deducir la carta aún."

# Ejemplo de uso
knowledge = actualizar_conocimiento(knowledge, "¿Es roja?", False)
knowledge = actualizar_conocimiento(knowledge, "¿Es de tréboles?", True)
knowledge = actualizar_conocimiento(knowledge, "¿Es par?", False)
knowledge = actualizar_conocimiento(knowledge, "¿Es el cinco?", True)

resultado = deducir_carta(knowledge)
print(resultado)

# -*- coding: utf-8 -*-

"""
Interpréteur de mini langage (PLY Lex / Yacc).

Objectif : produire un AST dont la structure ressemble au schéma du cours :
- ('PROG', ('fonction', ...), ('main', ('inst', ... , 'empty')))
- Paramètres : chaîne de nœuds 'param'
- Appel avec paramètres : ('callParam', nom_fonction, exp_chain)
- Liste d'arguments : chaîne de nœuds 'exp'
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

try:
    from genereTreeGraphviz2 import printTreeGraph
except Exception:
    printTreeGraph = None


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PREFIXE_CONSOLE = "calc > "
AFFICHER_GRAPHVIZ = True  # Doit rester désactivé par défaut (sujet)


# ---------------------------------------------------------------------------
# Analyse lexicale
# ---------------------------------------------------------------------------

mots_reserves = {
    "print": "PRINT",
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    "for": "FOR",
    "fonction": "FUNCTION",   # IMPORTANT : le cours utilise "fonction"
    "function": "FUNCTION",   # on accepte aussi "function"
    "return": "RETURN",
}

tokens = [
    "NUMBER",
    "NAME",
    # multi-caractères avant mono-caractères
    "PLUSPLUS",
    "EGALEGAL",
    "INFEG",
    "PLUS",
    "MINUS",
    "TIMES",
    "DIVIDE",
    "INF",
    "SUP",
    "OR",
    "AND",
    "LPAREN",
    "RPAREN",
    "LACC",
    "RACC",
    "COMMA",
    "SEMI",
    "EGAL",
] + list(set(mots_reserves.values()))

t_PLUSPLUS = r"\+\+"
t_EGALEGAL = r"=="
t_INFEG = r"<="

t_PLUS = r"\+"
t_MINUS = r"-"
t_TIMES = r"\*"
t_DIVIDE = r"/"
t_INF = r"<"
t_SUP = r">"
t_OR = r"\|"
t_AND = r"\&"

t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LACC = r"\{"
t_RACC = r"\}"
t_COMMA = r","
t_SEMI = r";"
t_EGAL = r"="


def t_NAME(production):
    r"[a-zA-Z_][a-zA-Z_0-9]*"
    production.type = mots_reserves.get(production.value, "NAME")
    return production


def t_NUMBER(production):
    r"\d+"
    production.value = int(production.value)
    return production


t_ignore = " \t"


def t_newline(production):
    r"\n+"
    production.lexer.lineno += production.value.count("\n")


def t_error(production):
    print(f"Caractère illégal : {production.value[0]!r}")
    production.lexer.skip(1)


import ply.lex as lex

analyseur_lexical = lex.lex()


# ---------------------------------------------------------------------------
# Analyse syntaxique
# ---------------------------------------------------------------------------

precedence = (
    ("left", "OR"),
    ("left", "AND"),
    ("nonassoc", "INF", "INFEG", "EGALEGAL", "SUP"),
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE"),
)


def p_empty(production):
    "empty :"
    production[0] = "empty"


def p_start(production):
    "start : liste_instructions"
    liste_complete = production[1]

    arbre_fonctions, arbre_main = separer_fonctions_et_main(liste_complete)

    # Le schéma du cours montre toujours un nœud "fonction"
    if arbre_fonctions == "empty":
        arbre_fonctions = ("fonction", "empty", "empty")

    production[0] = ("PROG", arbre_fonctions, ("main", arbre_main))

    # AST visible en console
    print(production[0])

    # Graphviz optionnel (doit rester commenté / désactivé par défaut)
    if AFFICHER_GRAPHVIZ:
        if printTreeGraph is None:
            raise ImportError("genereTreeGraphviz2.py introuvable.")
        printTreeGraph(production[0])

    executer_instruction(production[0])


# -----------------------
# Listes d'instructions : 'inst' ... 'empty'
# -----------------------

def p_opt_semi(production):
    """opt_semi : SEMI
                | empty
    """
    production[0] = "empty"


def p_element(production):
    """element : instruction_simple SEMI
               | instruction_composee opt_semi
    """
    production[0] = production[1]


def p_liste_instructions(production):
    """liste_instructions : element liste_instructions
                          | empty
    """
    if len(production) == 3:
        production[0] = ("inst", production[1], production[2])
    else:
        production[0] = "empty"


def p_bloc(production):
    "bloc : LACC liste_instructions RACC"
    production[0] = production[2]


# -----------------------
# Instructions simples
# -----------------------

def p_instruction_simple_affectation(production):
    "instruction_simple : NAME EGAL expression"
    production[0] = ("assign", production[1], production[3])


def p_instruction_simple_affichage(production):
    "instruction_simple : PRINT LPAREN expression RPAREN"
    production[0] = ("print", production[3])


def p_instruction_simple_post_incrementation(production):
    "instruction_simple : NAME PLUSPLUS"
    production[0] = ("++", production[1])


def p_instruction_simple_appel_fonction_sans_parametres(production):
    "instruction_simple : NAME LPAREN RPAREN"
    production[0] = ("call", production[1])


def p_instruction_simple_appel_fonction_avec_parametres(production):
    "instruction_simple : NAME LPAREN liste_expressions RPAREN"
    production[0] = ("callParam", production[1], production[3])


def p_instruction_simple_return_expression(production):
    "instruction_simple : RETURN expression"
    production[0] = ("return", production[2])


def p_instruction_simple_return_vide(production):
    "instruction_simple : RETURN"
    production[0] = ("return", "empty")


# -----------------------
# Instructions composées
# -----------------------

def p_instruction_composee_if(production):
    "instruction_composee : IF LPAREN expression RPAREN bloc"
    production[0] = ("if", production[3], production[5], "empty")


def p_instruction_composee_if_else(production):
    "instruction_composee : IF LPAREN expression RPAREN bloc ELSE bloc"
    production[0] = ("if", production[3], production[5], production[7])


def p_instruction_composee_while(production):
    "instruction_composee : WHILE LPAREN expression RPAREN bloc"
    production[0] = ("while", production[3], production[5])


def p_instruction_for_interne_affectation(production):
    "instruction_for : NAME EGAL expression"
    production[0] = ("assign", production[1], production[3])


def p_instruction_composee_for(production):
    "instruction_composee : FOR LPAREN instruction_for SEMI expression SEMI instruction_for opt_semi RPAREN bloc"
    # ('for', init, condition, increment, corps_inst)
    production[0] = ("for", production[3], production[5], production[7], production[10])


def p_instruction_composee_definition_fonction_sans_parametres(production):
    "instruction_composee : FUNCTION NAME LPAREN RPAREN bloc"
    # ('nom_fonction', 'empty', corps_inst)
    production[0] = (production[2], "empty", production[5])


def p_instruction_composee_definition_fonction_avec_parametres(production):
    "instruction_composee : FUNCTION NAME LPAREN liste_parametres RPAREN bloc"
    # ('nom_fonction', param_chain, corps_inst)
    production[0] = (production[2], production[4], production[6])


# -----------------------
# Paramètres : nœuds 'param'
# param -> param , NAME | NAME
# Base : ('param', 'a')
# Récursif : ('param', ('param','a'), 'b')
# -----------------------

def p_liste_parametres_base(production):
    "liste_parametres : NAME"
    production[0] = ("param", production[1])


def p_liste_parametres_recursion(production):
    "liste_parametres : liste_parametres COMMA NAME"
    production[0] = ("param", production[1], production[3])


# -----------------------
# Liste d'expressions (arguments) : nœuds 'exp'
# Base : ('exp', expression)
# Récursif : ('exp', ('exp', expr1), expr2)
# -----------------------

def p_liste_expressions_base(production):
    "liste_expressions : expression"
    production[0] = ("exp", production[1])


def p_liste_expressions_recursion(production):
    "liste_expressions : liste_expressions COMMA expression"
    production[0] = ("exp", production[1], production[3])


# -----------------------
# Expressions
# -----------------------

def p_expression_nombre(production):
    "expression : NUMBER"
    production[0] = production[1]


def p_expression_nom_variable(production):
    "expression : NAME"
    production[0] = production[1]


def p_expression_parentheses(production):
    "expression : LPAREN expression RPAREN"
    production[0] = production[2]


def p_expression_binaire_plus(production):
    "expression : expression PLUS expression"
    production[0] = ("+", production[1], production[3])


def p_expression_binaire_moins(production):
    "expression : expression MINUS expression"
    production[0] = ("-", production[1], production[3])


def p_expression_binaire_fois(production):
    "expression : expression TIMES expression"
    production[0] = ("*", production[1], production[3])


def p_expression_binaire_division(production):
    "expression : expression DIVIDE expression"
    production[0] = ("/", production[1], production[3])


def p_expression_binaire_inf(production):
    "expression : expression INF expression"
    production[0] = ("<", production[1], production[3])


def p_expression_binaire_inf_egal(production):
    "expression : expression INFEG expression"
    production[0] = ("<=", production[1], production[3])


def p_expression_binaire_sup(production):
    "expression : expression SUP expression"
    production[0] = (">", production[1], production[3])


def p_expression_binaire_egal_egal(production):
    "expression : expression EGALEGAL expression"
    production[0] = ("==", production[1], production[3])


def p_expression_binaire_et(production):
    "expression : expression AND expression"
    production[0] = ("and", production[1], production[3])


def p_expression_binaire_ou(production):
    "expression : expression OR expression"
    production[0] = ("or", production[1], production[3])


def p_error(production):
    if production is None:
        print("Erreur de syntaxe : fin de saisie inattendue.")
    else:
        print(f"Erreur de syntaxe près de {production.value!r} (type {production.type}).")


import ply.yacc as yacc

analyseur_syntaxique = yacc.yacc(start="start", debug=False, write_tables=False)


# ---------------------------------------------------------------------------
# Interpréteur : pile de contextes, fonctions, return coupe-circuit
# ---------------------------------------------------------------------------

class SignalRetour(Exception):
    def __init__(self, valeur: Any):
        super().__init__("Retour de fonction")
        self.valeur = valeur


pile_des_contextes: List[Dict[str, Any]] = [{}]
fonctions: Dict[str, Tuple[Any, Any]] = {}


def lire_variable(nom: str) -> Any:
    for contexte in reversed(pile_des_contextes):
        if nom in contexte:
            return contexte[nom]
    raise NameError(f"Variable non initialisée : {nom!r}")


def ecrire_variable(nom: str, valeur: Any) -> None:
    for contexte in reversed(pile_des_contextes):
        if nom in contexte:
            contexte[nom] = valeur
            return
    pile_des_contextes[-1][nom] = valeur


def est_definition_fonction(instruction: Any) -> bool:
    # Définition : (nom, param_chain ou 'empty', corps_inst)
    if not isinstance(instruction, tuple) or len(instruction) != 3:
        return False
    if not isinstance(instruction[0], str):
        return False
    corps = instruction[2]
    return corps == "empty" or (isinstance(corps, tuple) and corps[0] == "inst")


def liste_instructions_vers_liste_python(liste_instructions: Any) -> List[Any]:
    resultat: List[Any] = []
    courant = liste_instructions
    while courant != "empty":
        if not (isinstance(courant, tuple) and courant[0] == "inst"):
            raise TypeError(f"Liste d'instructions invalide : {courant!r}")
        resultat.append(courant[1])
        courant = courant[2]
    return resultat


def separer_fonctions_et_main(liste_instructions: Any) -> Tuple[Any, Any]:
    instructions = liste_instructions_vers_liste_python(liste_instructions)

    definitions_fonctions: List[Any] = []
    instructions_main: List[Any] = []

    for instruction in instructions:
        if est_definition_fonction(instruction):
            definitions_fonctions.append(instruction)
        else:
            instructions_main.append(instruction)

    # Chaîne "fonction" : ('fonction', precedent, definition)
    arbre_fonctions: Any = "empty"
    for definition in definitions_fonctions:
        arbre_fonctions = ("fonction", arbre_fonctions, definition)

    # Chaîne "inst" pour main
    arbre_main: Any = "empty"
    for instruction in reversed(instructions_main):
        arbre_main = ("inst", instruction, arbre_main)

    return arbre_fonctions, arbre_main


def extraire_parametres_depuis_param_chain(noeud_parametres: Any) -> List[str]:
    if noeud_parametres == "empty":
        return []
    if not isinstance(noeud_parametres, tuple) or noeud_parametres[0] != "param":
        raise TypeError(f"Noeud paramètres invalide : {noeud_parametres!r}")

    if len(noeud_parametres) == 2:
        if not isinstance(noeud_parametres[1], str):
            raise TypeError("Nom de paramètre invalide")
        return [noeud_parametres[1]]

    if len(noeud_parametres) == 3:
        return extraire_parametres_depuis_param_chain(noeud_parametres[1]) + [noeud_parametres[2]]

    raise TypeError("Structure de paramètres invalide")


def extraire_arguments_depuis_exp_chain(noeud_expressions: Any) -> List[Any]:
    if not isinstance(noeud_expressions, tuple) or noeud_expressions[0] != "exp":
        raise TypeError(f"Noeud arguments invalide : {noeud_expressions!r}")

    if len(noeud_expressions) == 2:
        return [noeud_expressions[1]]

    if len(noeud_expressions) == 3:
        return extraire_arguments_depuis_exp_chain(noeud_expressions[1]) + [noeud_expressions[2]]

    raise TypeError("Structure d'arguments invalide")


def enregistrer_fonctions(arbre_fonctions: Any) -> None:
    if arbre_fonctions == "empty":
        return
    if not isinstance(arbre_fonctions, tuple) or arbre_fonctions[0] != "fonction":
        return

    enregistrer_fonctions(arbre_fonctions[1])

    definition = arbre_fonctions[2]
    if definition == "empty":
        return
    if not est_definition_fonction(definition):
        return

    nom_fonction, noeud_parametres, corps = definition
    fonctions[nom_fonction] = (noeud_parametres, corps)


def executer_instruction(arbre: Any) -> None:
    if arbre == "empty":
        return

    if not isinstance(arbre, tuple):
        raise TypeError(f"Instruction invalide : {arbre!r}")

    etiquette = arbre[0]

    if etiquette == "PROG":
        enregistrer_fonctions(arbre[1])
        executer_instruction(arbre[2])
        return

    if etiquette == "main":
        executer_instruction(arbre[1])
        return

    if etiquette == "inst":
        executer_instruction(arbre[1])
        executer_instruction(arbre[2])
        return

    if etiquette == "print":
        valeur = evaluer_expression(arbre[1])
        print(f"{PREFIXE_CONSOLE}{valeur}")
        return

    if etiquette == "assign":
        ecrire_variable(arbre[1], evaluer_expression(arbre[2]))
        return

    if etiquette == "if":
        if evaluer_expression(arbre[1]):
            executer_instruction(arbre[2])
        else:
            executer_instruction(arbre[3])
        return

    if etiquette == "while":
        while evaluer_expression(arbre[1]):
            executer_instruction(arbre[2])
        return

    if etiquette == "for":
        executer_instruction(arbre[1])
        while evaluer_expression(arbre[2]):
            executer_instruction(arbre[4])
            executer_instruction(arbre[3])
        return

    if etiquette == "call":
        evaluer_expression(arbre)
        return

    if etiquette == "callParam":
        evaluer_expression(arbre)
        return

    if etiquette == "return":
        if arbre[1] == "empty":
            raise SignalRetour(None)
        raise SignalRetour(evaluer_expression(arbre[1]))

    if etiquette == "++":
        nom_variable = arbre[1]
        ancienne_valeur = lire_variable(nom_variable)
        ecrire_variable(nom_variable, ancienne_valeur + 1)
        return

    # Une définition de fonction dans main ne s'exécute pas ici (elles sont enregistrées au départ)
    if est_definition_fonction(arbre):
        return

    raise ValueError(f"Instruction inconnue : {etiquette!r}")


def evaluer_expression(arbre: Any) -> Any:
    if isinstance(arbre, int):
        return arbre
    if isinstance(arbre, bool):
        return arbre
    if isinstance(arbre, str):
        return lire_variable(arbre)

    if not isinstance(arbre, tuple):
        raise TypeError(f"Expression invalide : {arbre!r}")

    etiquette = arbre[0]

    if etiquette == "+":
        return evaluer_expression(arbre[1]) + evaluer_expression(arbre[2])
    if etiquette == "-":
        return evaluer_expression(arbre[1]) - evaluer_expression(arbre[2])
    if etiquette == "*":
        return evaluer_expression(arbre[1]) * evaluer_expression(arbre[2])
    if etiquette == "/":
        return evaluer_expression(arbre[1]) / evaluer_expression(arbre[2])

    if etiquette == "and":
        return bool(evaluer_expression(arbre[1])) and bool(evaluer_expression(arbre[2]))
    if etiquette == "or":
        return bool(evaluer_expression(arbre[1])) or bool(evaluer_expression(arbre[2]))

    if etiquette == "<":
        return evaluer_expression(arbre[1]) < evaluer_expression(arbre[2])
    if etiquette == "<=":
        return evaluer_expression(arbre[1]) <= evaluer_expression(arbre[2])
    if etiquette == "==":
        return evaluer_expression(arbre[1]) == evaluer_expression(arbre[2])
    if etiquette == ">":
        return evaluer_expression(arbre[1]) > evaluer_expression(arbre[2])

    if etiquette == "call":
        nom_fonction = arbre[1]
        if nom_fonction not in fonctions:
            raise NameError(f"Fonction non définie : {nom_fonction!r}")
        noeud_parametres, corps = fonctions[nom_fonction]

        # appel sans arguments
        liste_parametres = extraire_parametres_depuis_param_chain(noeud_parametres)
        if len(liste_parametres) != 0:
            raise TypeError(f"Fonction {nom_fonction!r} attend des paramètres.")
        pile_des_contextes.append({})
        try:
            executer_instruction(corps)
        except SignalRetour as signal:
            return signal.valeur
        finally:
            pile_des_contextes.pop()
        return None

    if etiquette == "callParam":
        nom_fonction = arbre[1]
        noeud_expressions = arbre[2]

        if nom_fonction not in fonctions:
            raise NameError(f"Fonction non définie : {nom_fonction!r}")

        noeud_parametres, corps = fonctions[nom_fonction]
        liste_parametres = extraire_parametres_depuis_param_chain(noeud_parametres)
        liste_arguments_expressions = extraire_arguments_depuis_exp_chain(noeud_expressions)
        valeurs_arguments = [evaluer_expression(expression) for expression in liste_arguments_expressions]

        if len(liste_parametres) != len(valeurs_arguments):
            raise TypeError(
                f"Nombre d'arguments incorrect pour {nom_fonction!r} : "
                f"attendu {len(liste_parametres)}, reçu {len(valeurs_arguments)}."
            )

        contexte_local: Dict[str, Any] = {}
        for nom_parametre, valeur in zip(liste_parametres, valeurs_arguments):
            contexte_local[nom_parametre] = valeur

        pile_des_contextes.append(contexte_local)
        try:
            executer_instruction(corps)
        except SignalRetour as signal:
            return signal.valeur
        finally:
            pile_des_contextes.pop()

        return None

    raise ValueError(f"Expression inconnue : {etiquette!r}")


# ---------------------------------------------------------------------------
# Exécution
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    saisie = input(PREFIXE_CONSOLE)
    analyseur_syntaxique.parse(saisie, lexer=analyseur_lexical)
import random

def decidir_jogada(meu_stack, pote_atual, minhas_cartas, cartas_mesa):
    """
    Estratégia: Aposta valores completamente imprevisíveis.
    """
    # Escolhe um número aleatório entre 0 e 20% do próprio dinheiro
    porcentagem = random.uniform(0.0, 0.20)
    aposta = meu_stack * porcentagem
    return float(aposta)
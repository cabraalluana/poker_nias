def decidir_jogada(meu_stack, pote_atual, minhas_cartas, cartas_mesa):
    """
    Estratégia: Joga de forma extremamente segura. Paga o blind ou dá Check.
    """
    # Aposta apenas 1% do próprio stack (simulando um call mínimo)
    aposta = meu_stack * 0.01
    return float(aposta)
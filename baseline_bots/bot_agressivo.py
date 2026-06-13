def decidir_jogada(meu_stack, pote_atual, minhas_cartas, cartas_mesa):
    """
    Estratégia: Pressiona a mesa. Aposta sempre uma fração considerável do pote.
    """
    # Aposta o equivalente a 50% do que já tem no pote, mas limitado ao seu próprio stack
    aposta = min(pote_atual * 0.5, meu_stack)
    return float(aposta)
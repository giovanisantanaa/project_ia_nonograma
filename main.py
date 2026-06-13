import sys

sys.path.append("src")


if __name__ == "__main__":
    from agente_regras import AgenteRegras
    from agente_csp import AgenteCSP
    from agente_probabilistico import AgenteProbabilistico
    from puzzles import puzzles_5x5

    agentes = [AgenteRegras(), AgenteCSP(), AgenteProbabilistico()]

    for puzzle in puzzles_5x5():
        print("=== " + puzzle.nome + " ===")
        for agente in agentes:
            resultado = agente.resolver(puzzle)
            print(resultado)
        print()
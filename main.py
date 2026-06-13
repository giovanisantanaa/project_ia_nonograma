import sys

sys.path.append("src")


if __name__ == "__main__":
    from ambiente import Nonograma
    from agente_regras import AgenteRegras
    from agente_csp import AgenteCSP
    from agente_probabilistico import AgenteProbabilistico

    pistas_linha = [[1], [1], [5], [1], [1]]
    pistas_coluna = [[1], [1], [5], [1], [1]]

    p1 = Nonograma(pistas_linha, pistas_coluna, nome="cruz")
    agente_regras = AgenteRegras()
    resultado_regras = agente_regras.resolver(p1)
    print("regras:", resultado_regras)
    print(p1)

    p2 = Nonograma(pistas_linha, pistas_coluna, nome="cruz")
    agente_csp = AgenteCSP()
    resultado_csp = agente_csp.resolver(p2)
    print("csp:", resultado_csp)
    print(p2)
    
    p3 = Nonograma(pistas_linha, pistas_coluna, nome="cruz")
    agente_prob = AgenteProbabilistico()
    resultado_prob = agente_prob.resolver(p3)
    print("probabilistico:", resultado_prob)
    print(p3)
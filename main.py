import sys

sys.path.append("src")


if __name__ == "__main__":
    from ambiente import Nonograma
    from agente_regras import AgenteRegras

    pistas_linha = [[1], [1], [5], [1], [1]]
    pistas_coluna = [[1], [1], [5], [1], [1]]

    p = Nonograma(pistas_linha, pistas_coluna, nome="cruz")
    print("antes:")
    print(p)

    agente = AgenteRegras()
    resultado = agente.resolver(p)

    print("depois:")
    print(p)
    # print(p.esta_resolvido())
    print(resultado)
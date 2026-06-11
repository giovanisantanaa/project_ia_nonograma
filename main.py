import sys

sys.path.append("src")


if __name__ == "__main__":
    from base_ia import Problem, Node
    from ambiente import Nonograma
    
    print("estruturas de busca importadas com sucesso")
    print(Problem)
    print(Node)
    
    print()
    print("teste do tabuleiro:")
    p = Nonograma([[2], [1]], [[1], [1], [1]], nome="teste")
    print(p)
    print("resolvido?", p.esta_resolvido())
import sys

sys.path.append("src")


if __name__ == "__main__":
    from benchmark import rodar_benchmark, imprimir_tabela

    print("Usando puzzles gerados por puzzles2.py")
    resultados = rodar_benchmark()
    imprimir_tabela(resultados)

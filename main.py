import sys

sys.path.append("src")


if __name__ == "__main__":
    from benchmark import rodar_benchmark, imprimir_tabela

    resultados = rodar_benchmark()
    imprimir_tabela(resultados)
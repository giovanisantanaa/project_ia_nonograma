import sys

sys.path.append("src")


if __name__ == "__main__":
    from benchmark import rodar_benchmark, imprimir_tabela
    from interface import Janela
    import tkinter as tk

    resultados = rodar_benchmark()
    imprimir_tabela(resultados)

    raiz = tk.Tk()
    janela = Janela(raiz)
    raiz.mainloop()
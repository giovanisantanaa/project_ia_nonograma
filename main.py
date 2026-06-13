import sys

sys.path.append("src")


if __name__ == "__main__":
    from interface import Janela
    import tkinter as tk
    
    raiz = tk.Tk()
    janela = Janela(raiz)
    raiz.mainloop()
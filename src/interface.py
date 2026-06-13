import tkinter as tk
from tkinter import ttk

import sys
sys.path.append("src")


from ambiente import DESCONHECIDO, PINTADA, VAZIA
from agente_regras import AgenteRegras
from agente_csp import AgenteCSP
from agente_probabilistico import AgenteProbabilistico
from puzzles import puzzles_5x5, puzzles_10x10

class Janela:
    
    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.title("IA de Nonograma")
        
        self.puzzles = puzzles_5x5() + puzzles_10x10()
        self.agentes = [AgenteRegras(), AgenteCSP(), AgenteProbabilistico()]
        
        self.montar_widgets()
        
        
    def montar_widgets(self):
        frame_topo = ttk.Frame(self.raiz)
        frame_topo.pack(padx=10, pady=10)
        
        tk.Label(frame_topo, text="Puzzle:").grid(row=0, column=0, sticky="w")
        # nomes_puzzles = []
        # for p in self.puzzles:
        #     nomes_puzzles.append(p.nome)
        
        nomes_puzzles = [p.nome for p in self.puzzles]
        
        self.combo_puzzle = ttk.Combobox(frame_topo, values=nomes_puzzles, state="readonly", width=20)
        self.combo_puzzle.current(0)
        self.combo_puzzle.grid(row=0, column=1, padx=5)
        
        tk.Label(frame_topo, text="Agente:").grid(row=1, column=0, sticky="w")
        nomes_agentes = [a.nome for a in self.agentes]
        
        self.combo_agente = ttk.Combobox(frame_topo, values=nomes_agentes, state="readonly", width=20)
        self.combo_agente.current(0)
        self.combo_agente.grid(row=1, column=1, padx=5)
        
        botao = tk.Button(frame_topo, text="Resolver", command=self.resolver)
        botao.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.label_resultado = tk.Label(self.raiz, text="")
        self.label_resultado.pack(pady=5)
        
        self.frame_tabuleiro = ttk.Frame(self.raiz)
        self.frame_tabuleiro.pack(padx=10, pady=10)
        
    
    
    def resolver(self):
        nome_puzzle = self.combo_puzzle.get()
        nome_agente = self.combo_agente.get()
        
        puzzle_escolhido = None
        for p in self.puzzles:
            if p.nome == nome_puzzle:
                puzzle_escolhido = p

        agente_escolhido = None
        for a in self.agentes:
            if a.nome == nome_agente:
                agente_escolhido = a
                
        
        p = puzzle_escolhido.copiar()
        resultado = agente_escolhido.resolver(p)
        
        texto = "resolvido:" + str(resultado['resolvido'])
        texto += " | tempo: "+ "{:.3f}".format(resultado['tempo'] * 1000) + " ms"
        texto += " | passos: " + str(resultado['passos'])
        
        self.label_resultado.config(text=texto)
        self.desenhar_tabuleiro(p)
        
        
    def desenhar_tabuleiro(self, puzzle):
        for widget in self.frame_tabuleiro.winfo_children():
            widget.destroy()
            
        tamanho_celula = 25
        
        for i in range(puzzle.linhas):
            for j in range(puzzle.colunas):
                valor = puzzle.tabuleiro[i][j]
                
                if valor == PINTADA:
                    cor = "black"
                elif valor == VAZIA:
                    cor = "white"
                else:
                    cor = "gray"
                    
                celula = tk.Label(self.frame_tabuleiro, bg=cor, width=2, height=1, relief="solid", borderwidth=1)
                celula.grid(row=i, column=j)
                

if __name__ == "__main__":
    raiz = tk.Tk()
    janela = Janela(raiz)
    raiz.mainloop()
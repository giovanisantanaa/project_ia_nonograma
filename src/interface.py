# interface grafica completa do projeto
#
# abas:
# 1. Individual    - escolhe puzzle (ou aleatorio) e um agente, anima a solucao
# 2. Comparativo   - escolhe puzzle (ou aleatorio) e os 4 agentes resolvem
#                     o mesmo puzzle, lado a lado
# 3. Benchmark     - roda o benchmark completo (banco de puzzles) ou um
#                     puzzle aleatorio (todos os agentes resolvem o mesmo)
# 4. Graficos      - gera e mostra os graficos comparativos
#
# os tabuleiros sao desenhados como um nonograma de verdade, com os
# numeros das pistas nas margens de cima e da esquerda

import tkinter as tk
from tkinter import ttk

import sys
sys.path.append("src")

from ambiente import DESCONHECIDO, PINTADA, VAZIA
from agente_regras import AgenteRegras
from agente_csp import AgenteCSP
from agente_probabilistico import AgenteProbabilistico
from agente_local import AgenteBuscaLocal
from puzzles import puzzles_todos, gerar_puzzle_aleatorio, TAMANHOS
from benchmark import rodar_benchmark
from graph_gen import gerar_graficos


class Janela:

    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.title("Nonograma - IA")

        self.puzzles = puzzles_todos()
        self.agentes = [
            AgenteRegras(),
            AgenteCSP(),
            AgenteProbabilistico(),
            AgenteBuscaLocal(),
        ]

        # estado da aba individual
        self.puzzle_individual = None
        self.resultado_individual = None
        self.historico_individual = []
        self.indice_individual = 0
        self.rodando_individual = False

        # estado da aba comparativo
        self.puzzle_comparativo = None
        self.resultados_comparativo = []
        self.historicos_comparativo = []
        self.indice_comparativo = 0
        self.rodando_comparativo = False

        # referencias das imagens dos graficos (precisa manter, senao o
        # tkinter descarta a imagem)
        self.imagens_graficos = []

        self.montar_interface()

    # ---------------------------------------------------------------
    # montagem geral
    # ---------------------------------------------------------------

    def montar_interface(self):
        notebook = ttk.Notebook(self.raiz)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        aba_individual = tk.Frame(notebook)
        aba_comparativo = tk.Frame(notebook)
        aba_benchmark = tk.Frame(notebook)
        aba_graficos = tk.Frame(notebook)

        notebook.add(aba_individual, text="Individual")
        notebook.add(aba_comparativo, text="Comparativo")
        notebook.add(aba_benchmark, text="Benchmark")
        notebook.add(aba_graficos, text="Graficos")

        self.montar_aba_individual(aba_individual)
        self.montar_aba_comparativo(aba_comparativo)
        self.montar_aba_benchmark(aba_benchmark)
        self.montar_aba_graficos(aba_graficos)

    def pegar_puzzle(self, combo):
        nome_puzzle = combo.get()
        for p in self.puzzles:
            if p.nome == nome_puzzle:
                return p
        return self.puzzles[0]

    def pegar_historico(self, resultado, modo_animacao):
        if modo_animacao.get() == "celulas":
            return resultado["historico_celulas"]
        return resultado["historico_passos"]

    # ---------------------------------------------------------------
    # desenho do nonograma (tabuleiro + pistas nas margens)
    # ---------------------------------------------------------------

    def desenhar_nonograma(self, canvas, puzzle, tabuleiro, tamanho_total):
        canvas.delete("all")

        maior_pistas_linha = 0
        for pistas in puzzle.pistas_linha:
            if len(pistas) > maior_pistas_linha:
                maior_pistas_linha = len(pistas)

        maior_pistas_coluna = 0
        for pistas in puzzle.pistas_coluna:
            if len(pistas) > maior_pistas_coluna:
                maior_pistas_coluna = len(pistas)

        total_colunas = puzzle.colunas + maior_pistas_linha
        total_linhas = puzzle.linhas + maior_pistas_coluna

        maior_lado = total_colunas
        if total_linhas > maior_lado:
            maior_lado = total_linhas

        cel = tamanho_total / maior_lado

        largura = total_colunas * cel
        altura = total_linhas * cel

        canvas.config(width=int(largura), height=int(altura))

        margem_esq = maior_pistas_linha * cel
        margem_topo = maior_pistas_coluna * cel

        tamanho_fonte = int(cel * 0.45)
        if tamanho_fonte < 6:
            tamanho_fonte = 6
        fonte = ("Arial", tamanho_fonte)

        # pistas das colunas, alinhadas na base da margem de cima
        for j in range(puzzle.colunas):
            pistas = puzzle.pistas_coluna[j]
            n = len(pistas)

            for k in range(n):
                valor = pistas[k]
                if valor == 0:
                    continue

                x = margem_esq + j * cel + cel / 2
                pos = maior_pistas_coluna - n + k
                y = pos * cel + cel / 2
                canvas.create_text(x, y, text=str(valor), font=fonte)

        # pistas das linhas, alinhadas na direita da margem esquerda
        for i in range(puzzle.linhas):
            pistas = puzzle.pistas_linha[i]
            n = len(pistas)

            for k in range(n):
                valor = pistas[k]
                if valor == 0:
                    continue

                pos = maior_pistas_linha - n + k
                x = pos * cel + cel / 2
                y = margem_topo + i * cel + cel / 2
                canvas.create_text(x, y, text=str(valor), font=fonte)

        # grade de celulas do tabuleiro
        for i in range(puzzle.linhas):
            for j in range(puzzle.colunas):
                valor = tabuleiro[i][j]

                if valor == PINTADA:
                    cor = "black"
                elif valor == VAZIA:
                    cor = "white"
                else:
                    cor = "#dddddd"

                x0 = margem_esq + j * cel
                y0 = margem_topo + i * cel
                x1 = x0 + cel
                y1 = y0 + cel

                canvas.create_rectangle(x0, y0, x1, y1, fill=cor, outline="gray")

        # linhas separando as pistas do tabuleiro
        canvas.create_line(margem_esq, 0, margem_esq, altura, fill="black", width=2)
        canvas.create_line(0, margem_topo, largura, margem_topo, fill="black", width=2)

    # ---------------------------------------------------------------
    # aba 1: individual
    # ---------------------------------------------------------------

    def montar_aba_individual(self, aba):
        frame_opcoes = tk.LabelFrame(aba, text="Opcoes")
        frame_opcoes.pack(padx=10, pady=10, fill="x")

        tk.Label(frame_opcoes, text="Puzzle:").grid(row=0, column=0, sticky="w")
        nomes_puzzles = []
        for p in self.puzzles:
            nomes_puzzles.append(p.nome)

        self.combo_puzzle_individual = ttk.Combobox(frame_opcoes, values=nomes_puzzles, state="readonly", width=22)
        self.combo_puzzle_individual.current(0)
        self.combo_puzzle_individual.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(frame_opcoes, text="Agente:").grid(row=1, column=0, sticky="w")
        nomes_agentes = []
        for a in self.agentes:
            nomes_agentes.append(a.nome)

        self.combo_agente_individual = ttk.Combobox(frame_opcoes, values=nomes_agentes, state="readonly", width=22)
        self.combo_agente_individual.current(0)
        self.combo_agente_individual.grid(row=1, column=1, padx=5, pady=2)

        tk.Label(frame_opcoes, text="Tamanho (aleatorio):").grid(row=2, column=0, sticky="w")
        nomes_tamanhos = []
        for t in TAMANHOS:
            nomes_tamanhos.append(str(t))

        self.combo_tamanho_individual = ttk.Combobox(frame_opcoes, values=nomes_tamanhos, state="readonly", width=22)
        self.combo_tamanho_individual.current(0)
        self.combo_tamanho_individual.grid(row=2, column=1, padx=5, pady=2)

        self.var_aleatorio_individual = tk.BooleanVar(value=False)
        tk.Checkbutton(
            frame_opcoes, text="Usar puzzle aleatorio (em vez do escolhido acima)",
            variable=self.var_aleatorio_individual,
            command=self.atualizar_estado_individual,
        ).grid(row=3, column=0, columnspan=2, sticky="w")

        tk.Label(frame_opcoes, text="Animacao:").grid(row=4, column=0, sticky="w")
        self.modo_animacao_individual = tk.StringVar(value="passos")

        frame_modo = tk.Frame(frame_opcoes)
        frame_modo.grid(row=4, column=1, sticky="w")
        tk.Radiobutton(frame_modo, text="por passos", variable=self.modo_animacao_individual, value="passos").pack(side="left")
        tk.Radiobutton(frame_modo, text="celula a celula", variable=self.modo_animacao_individual, value="celulas").pack(side="left")

        frame_botoes = tk.Frame(aba)
        frame_botoes.pack(pady=5)

        tk.Button(frame_botoes, text="Resolver", command=self.resolver_individual).pack(side="left", padx=2)
        tk.Button(frame_botoes, text="Reiniciar", command=self.reiniciar_individual).pack(side="left", padx=2)
        tk.Button(frame_botoes, text="Anterior", command=self.voltar_individual).pack(side="left", padx=2)
        tk.Button(frame_botoes, text="Play", command=self.play_individual).pack(side="left", padx=2)
        tk.Button(frame_botoes, text="Pause", command=self.pause_individual).pack(side="left", padx=2)
        tk.Button(frame_botoes, text="Proximo", command=self.avancar_individual).pack(side="left", padx=2)

        self.label_individual = tk.Label(aba, text="", justify="left", font=("Courier", 10))
        self.label_individual.pack(pady=5)

        self.canvas_individual = tk.Canvas(aba, width=420, height=420, bg="white")
        self.canvas_individual.pack(pady=5)

    def atualizar_estado_individual(self):
        if self.var_aleatorio_individual.get():
            self.combo_puzzle_individual.config(state="disabled")
        else:
            self.combo_puzzle_individual.config(state="readonly")

    def pegar_agente(self, combo):
        nome_agente = combo.get()
        for a in self.agentes:
            if a.nome == nome_agente:
                return a
        return self.agentes[0]

    def resolver_individual(self):
        self.pause_individual()

        agente = self.pegar_agente(self.combo_agente_individual)

        if self.var_aleatorio_individual.get():
            tamanho = int(self.combo_tamanho_individual.get())
            puzzle_base = gerar_puzzle_aleatorio(tamanho)
        else:
            puzzle_base = self.pegar_puzzle(self.combo_puzzle_individual)

        p = puzzle_base.copiar()
        resultado = agente.resolver(p)

        historico = self.pegar_historico(resultado, self.modo_animacao_individual)
        if len(historico) == 0:
            historico = [p.tabuleiro]

        self.puzzle_individual = puzzle_base
        self.resultado_individual = resultado
        self.historico_individual = historico
        self.indice_individual = 0

        self.atualizar_individual()

    def atualizar_individual(self):
        if not self.historico_individual:
            return

        tabuleiro = self.historico_individual[self.indice_individual]
        self.desenhar_nonograma(self.canvas_individual, self.puzzle_individual, tabuleiro, 420)

        r = self.resultado_individual

        texto = "puzzle: " + self.puzzle_individual.nome + "\n"
        texto = texto + "agente: " + r["nome"] + "\n"
        texto = texto + "resolvido: " + str(r["resolvido"])
        texto = texto + "  |  tempo total: " + "{:.3f}".format(r["tempo"] * 1000) + " ms"
        texto = texto + "  |  passos: " + str(r["passos"]) + "\n"
        texto = texto + "quadro " + str(self.indice_individual + 1) + " de " + str(len(self.historico_individual))

        self.label_individual.config(text=texto)

    def reiniciar_individual(self):
        self.pause_individual()
        if not self.historico_individual:
            return
        self.indice_individual = 0
        self.atualizar_individual()

    def voltar_individual(self):
        if not self.historico_individual:
            return
        if self.indice_individual > 0:
            self.indice_individual = self.indice_individual - 1
            self.atualizar_individual()

    def avancar_individual(self):
        if not self.historico_individual:
            return

        if self.indice_individual < len(self.historico_individual) - 1:
            self.indice_individual = self.indice_individual + 1
            self.atualizar_individual()
        else:
            self.pause_individual()

    def play_individual(self):
        if not self.historico_individual:
            return
        self.rodando_individual = True
        self.tocar_proximo_individual()

    def pause_individual(self):
        self.rodando_individual = False

    def tocar_proximo_individual(self):
        if not self.rodando_individual:
            return

        if self.indice_individual < len(self.historico_individual) - 1:
            self.avancar_individual()
            self.raiz.after(80, self.tocar_proximo_individual)
        else:
            self.rodando_individual = False

    # ---------------------------------------------------------------
    # aba 2: comparativo (os 4 agentes no mesmo puzzle)
    # ---------------------------------------------------------------

    def montar_aba_comparativo(self, aba):
        frame_opcoes = tk.LabelFrame(aba, text="Opcoes")
        frame_opcoes.pack(padx=10, pady=10, fill="x")

        tk.Label(frame_opcoes, text="Puzzle:").grid(row=0, column=0, sticky="w")
        nomes_puzzles = []
        for p in self.puzzles:
            nomes_puzzles.append(p.nome)

        self.combo_puzzle_comparativo = ttk.Combobox(frame_opcoes, values=nomes_puzzles, state="readonly", width=22)
        self.combo_puzzle_comparativo.current(0)
        self.combo_puzzle_comparativo.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(frame_opcoes, text="Tamanho (aleatorio):").grid(row=1, column=0, sticky="w")
        nomes_tamanhos = []
        for t in TAMANHOS:
            nomes_tamanhos.append(str(t))

        self.combo_tamanho_comparativo = ttk.Combobox(frame_opcoes, values=nomes_tamanhos, state="readonly", width=22)
        self.combo_tamanho_comparativo.current(0)
        self.combo_tamanho_comparativo.grid(row=1, column=1, padx=5, pady=2)

        self.var_aleatorio_comparativo = tk.BooleanVar(value=False)
        tk.Checkbutton(
            frame_opcoes,
            text="Usar puzzle aleatorio (todos os agentes resolvem o mesmo puzzle)",
            variable=self.var_aleatorio_comparativo,
            command=self.atualizar_estado_comparativo,
        ).grid(row=2, column=0, columnspan=2, sticky="w")

        tk.Label(frame_opcoes, text="Animacao:").grid(row=3, column=0, sticky="w")
        self.modo_animacao_comparativo = tk.StringVar(value="passos")

        frame_modo = tk.Frame(frame_opcoes)
        frame_modo.grid(row=3, column=1, sticky="w")
        tk.Radiobutton(frame_modo, text="por passos", variable=self.modo_animacao_comparativo, value="passos").pack(side="left")
        tk.Radiobutton(frame_modo, text="celula a celula", variable=self.modo_animacao_comparativo, value="celulas").pack(side="left")

        frame_botoes = tk.Frame(aba)
        frame_botoes.pack(pady=5)

        tk.Button(frame_botoes, text="Resolver Todos", command=self.resolver_comparativo).pack(side="left", padx=2)
        tk.Button(frame_botoes, text="Reiniciar", command=self.reiniciar_comparativo).pack(side="left", padx=2)
        tk.Button(frame_botoes, text="Anterior", command=self.voltar_comparativo).pack(side="left", padx=2)
        tk.Button(frame_botoes, text="Play", command=self.play_comparativo).pack(side="left", padx=2)
        tk.Button(frame_botoes, text="Pause", command=self.pause_comparativo).pack(side="left", padx=2)
        tk.Button(frame_botoes, text="Proximo", command=self.avancar_comparativo).pack(side="left", padx=2)

        frame_tabuleiros = tk.Frame(aba)
        frame_tabuleiros.pack(pady=5)

        self.canvas_comparativo = []
        self.label_comparativo = []

        for idx in range(len(self.agentes)):
            sub_frame = tk.Frame(frame_tabuleiros)
            sub_frame.grid(row=0, column=idx, padx=5)

            canvas = tk.Canvas(sub_frame, width=180, height=180, bg="white")
            canvas.pack()
            self.canvas_comparativo.append(canvas)

            label = tk.Label(sub_frame, text=self.agentes[idx].nome, justify="left", font=("Courier", 8))
            label.pack()
            self.label_comparativo.append(label)

    def atualizar_estado_comparativo(self):
        if self.var_aleatorio_comparativo.get():
            self.combo_puzzle_comparativo.config(state="disabled")
        else:
            self.combo_puzzle_comparativo.config(state="readonly")

    def resolver_comparativo(self):
        self.pause_comparativo()

        if self.var_aleatorio_comparativo.get():
            tamanho = int(self.combo_tamanho_comparativo.get())
            puzzle_base = gerar_puzzle_aleatorio(tamanho)
        else:
            puzzle_base = self.pegar_puzzle(self.combo_puzzle_comparativo)

        self.puzzle_comparativo = puzzle_base
        self.resultados_comparativo = []
        self.historicos_comparativo = []

        for agente in self.agentes:
            p = puzzle_base.copiar()
            resultado = agente.resolver(p)
            self.resultados_comparativo.append(resultado)

            historico = self.pegar_historico(resultado, self.modo_animacao_comparativo)
            if len(historico) == 0:
                historico = [p.tabuleiro]
            self.historicos_comparativo.append(historico)

        self.indice_comparativo = 0
        self.atualizar_comparativo()

    def maior_historico_comparativo(self):
        maior = 0
        for historico in self.historicos_comparativo:
            if len(historico) > maior:
                maior = len(historico)
        return maior

    def atualizar_comparativo(self):
        if not self.historicos_comparativo:
            return

        for idx in range(len(self.agentes)):
            agente = self.agentes[idx]
            resultado = self.resultados_comparativo[idx]
            historico = self.historicos_comparativo[idx]

            i = self.indice_comparativo
            if i >= len(historico):
                i = len(historico) - 1

            self.desenhar_nonograma(self.canvas_comparativo[idx], self.puzzle_comparativo, historico[i], 180)

            if resultado["passos"] > 0:
                tempo_por_passo = (resultado["tempo"] / resultado["passos"]) * 1000
            else:
                tempo_por_passo = 0.0

            texto = agente.nome + "\n"
            texto = texto + "resolvido: " + str(resultado["resolvido"]) + "\n"
            texto = texto + "tempo total: " + "{:.2f}".format(resultado["tempo"] * 1000) + " ms\n"
            texto = texto + "passos: " + str(resultado["passos"])
            texto = texto + " (~" + "{:.3f}".format(tempo_por_passo) + " ms/passo)\n"
            texto = texto + "quadro " + str(i + 1) + " de " + str(len(historico))

            self.label_comparativo[idx].config(text=texto)

    def reiniciar_comparativo(self):
        self.pause_comparativo()
        if not self.historicos_comparativo:
            return
        self.indice_comparativo = 0
        self.atualizar_comparativo()

    def voltar_comparativo(self):
        if not self.historicos_comparativo:
            return
        if self.indice_comparativo > 0:
            self.indice_comparativo = self.indice_comparativo - 1
            self.atualizar_comparativo()

    def avancar_comparativo(self):
        if not self.historicos_comparativo:
            return

        maior = self.maior_historico_comparativo()

        if self.indice_comparativo < maior - 1:
            self.indice_comparativo = self.indice_comparativo + 1
            self.atualizar_comparativo()
        else:
            self.pause_comparativo()

    def play_comparativo(self):
        if not self.historicos_comparativo:
            return
        self.rodando_comparativo = True
        self.tocar_proximo_comparativo()

    def pause_comparativo(self):
        self.rodando_comparativo = False

    def tocar_proximo_comparativo(self):
        if not self.rodando_comparativo:
            return

        maior = self.maior_historico_comparativo()

        if self.indice_comparativo < maior - 1:
            self.avancar_comparativo()
            self.raiz.after(80, self.tocar_proximo_comparativo)
        else:
            self.rodando_comparativo = False

    # ---------------------------------------------------------------
    # aba 3: benchmark
    # ---------------------------------------------------------------

    def montar_aba_benchmark(self, aba):
        frame_botoes = tk.Frame(aba)
        frame_botoes.pack(pady=5)

        tk.Button(frame_botoes, text="Rodar benchmark (banco de puzzles)", command=self.rodar_benchmark_completo).pack(side="left", padx=5)

        tk.Label(frame_botoes, text="Tamanho aleatorio:").pack(side="left", padx=5)
        nomes_tamanhos = []
        for t in TAMANHOS:
            nomes_tamanhos.append(str(t))

        self.combo_tamanho_benchmark = ttk.Combobox(frame_botoes, values=nomes_tamanhos, state="readonly", width=6)
        self.combo_tamanho_benchmark.current(0)
        self.combo_tamanho_benchmark.pack(side="left", padx=2)

        tk.Button(frame_botoes, text="Rodar com puzzle aleatorio (mesmo p/ todos)", command=self.rodar_benchmark_aleatorio).pack(side="left", padx=5)

        self.canvas_benchmark_puzzle = tk.Canvas(aba, width=220, height=220, bg="white")
        self.canvas_benchmark_puzzle.pack(pady=5)

        self.texto_benchmark = tk.Text(aba, height=22, width=90, font=("Courier", 9))
        self.texto_benchmark.pack(padx=10, pady=5)

    def rodar_benchmark_completo(self):
        self.texto_benchmark.delete("1.0", tk.END)
        self.texto_benchmark.insert(tk.END, "rodando benchmark, aguarde...\n")
        self.raiz.update()

        resultados = rodar_benchmark()

        self.texto_benchmark.delete("1.0", tk.END)

        cabecalho = "{:<20} {:<25} {:<10} {:<12} {:<8}\n".format(
            "puzzle", "agente", "resolvido", "tempo (ms)", "passos"
        )
        self.texto_benchmark.insert(tk.END, cabecalho)
        self.texto_benchmark.insert(tk.END, "-" * 80 + "\n")

        for r in resultados:
            tempo_ms = r["tempo"] * 1000
            linha = "{:<20} {:<25} {:<10} {:<12.3f} {:<8}\n".format(
                r["puzzle"], r["nome"], str(r["resolvido"]), tempo_ms, r["passos"]
            )
            self.texto_benchmark.insert(tk.END, linha)

    def rodar_benchmark_aleatorio(self):
        tamanho = int(self.combo_tamanho_benchmark.get())
        puzzle_base = gerar_puzzle_aleatorio(tamanho)

        self.desenhar_nonograma(self.canvas_benchmark_puzzle, puzzle_base, puzzle_base.tabuleiro, 220)

        self.texto_benchmark.delete("1.0", tk.END)
        self.texto_benchmark.insert(tk.END, "puzzle aleatorio " + str(tamanho) + "x" + str(tamanho) + "\n\n")

        cabecalho = "{:<25} {:<10} {:<12} {:<8}\n".format(
            "agente", "resolvido", "tempo (ms)", "passos"
        )
        self.texto_benchmark.insert(tk.END, cabecalho)
        self.texto_benchmark.insert(tk.END, "-" * 60 + "\n")

        for agente in self.agentes:
            p = puzzle_base.copiar()
            resultado = agente.resolver(p)

            tempo_ms = resultado["tempo"] * 1000
            linha = "{:<25} {:<10} {:<12.3f} {:<8}\n".format(
                resultado["nome"], str(resultado["resolvido"]), tempo_ms, resultado["passos"]
            )
            self.texto_benchmark.insert(tk.END, linha)

    # ---------------------------------------------------------------
    # aba 4: graficos
    # ---------------------------------------------------------------

    def montar_aba_graficos(self, aba):
        frame_botoes = tk.Frame(aba)
        frame_botoes.pack(pady=5)

        tk.Button(frame_botoes, text="Gerar graficos", command=self.gerar_graficos_interface).pack()

        self.label_status_graficos = tk.Label(aba, text="")
        self.label_status_graficos.pack(pady=2)

        self.frame_imagens = tk.Frame(aba)
        self.frame_imagens.pack(pady=10)

    def gerar_graficos_interface(self):
        self.label_status_graficos.config(text="gerando graficos, aguarde...")
        self.raiz.update()

        for widget in self.frame_imagens.winfo_children():
            widget.destroy()
        self.imagens_graficos = []

        gerar_graficos()

        nomes_arquivos = [
            "graph_images/tempo.png",
            "graph_images/passos.png",
            "graph_images/taxa_resolvido.png",
        ]

        for caminho in nomes_arquivos:
            imagem = tk.PhotoImage(file=caminho)
            self.imagens_graficos.append(imagem)

            label = tk.Label(self.frame_imagens, image=imagem)
            label.pack(side="left", padx=5)

        self.label_status_graficos.config(text="graficos gerados (pasta graph_images/)")


if __name__ == "__main__":
    raiz = tk.Tk()
    app = Janela(raiz)
    raiz.mainloop()
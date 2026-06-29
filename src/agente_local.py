# agente de busca local que comeca com um tabuleiro aleatorio e vai
#trocando celulas pintada e vazia tentando diminuir o numero
#de linhas e colunas inconsistentes

import time
import math
import random

from ambiente import PINTADA, VAZIA


class AgenteBuscaLocal:

    def __init__(self):
        self.nome = 'Busca Local (Simulated Annealing)'
        self.temperatura_inicial = 50.0
        self.taxa_resfriamento = 0.995
        self.max_iteracoes = 2000

    def calcular_erros(self, puzzle):
        # a funcao de custo e quantas linhas e colunas estao inconsistentes
        erros = 0

        for i in range(puzzle.linhas):
            if not puzzle.linha_consistente(puzzle.tabuleiro[i], puzzle.pistas_linha[i]):
                erros = erros + 1

        for j in range(puzzle.colunas):
            coluna = [puzzle.tabuleiro[i][j] for i in range(puzzle.linhas)]
            if not puzzle.linha_consistente(coluna, puzzle.pistas_coluna[j]):
                erros = erros + 1

        return erros

    def resolver(self, puzzle):
        inicio = time.time()
        passos = 0
        historico = []
        descricoes = []

        historico.append([linha[:] for linha in puzzle.tabuleiro])
        descricoes.append('Inicio: inicializando tabuleiro aleatoriamente...')

        # inicializa o tabuleiro aleatoriamente
        for i in range(puzzle.linhas):
            for j in range(puzzle.colunas):
                puzzle.tabuleiro[i][j] = random.choice([PINTADA, VAZIA])

        historico.append([linha[:] for linha in puzzle.tabuleiro])
        custo_atual = self.calcular_erros(puzzle)
        descricoes.append('Inicializacao aleatoria: {} linhas/colunas erradas'.format(custo_atual))
        T = self.temperatura_inicial

        while T > 0.01 and custo_atual > 0 and passos < self.max_iteracoes:
            passos = passos + 1

            i = random.randint(0, puzzle.linhas - 1)
            j = random.randint(0, puzzle.colunas - 1)

            estado_anterior = puzzle.tabuleiro[i][j]
            if estado_anterior == PINTADA:
                puzzle.tabuleiro[i][j] = VAZIA
            else:
                puzzle.tabuleiro[i][j] = PINTADA

            novo_custo = self.calcular_erros(puzzle)
            delta = novo_custo - custo_atual

            if delta < 0:
                # aceita porque melhorou
                custo_atual = novo_custo
                linha_copia = [linha[:] for linha in puzzle.tabuleiro]
                historico.append(linha_copia)
                descricoes.append(
                    'T={:.1f}: troca ({},{}) erros {}->{}  aceito: melhora'.format(
                        T, i + 1, j + 1, custo_atual - delta, custo_atual
                    )
                )
            elif random.random() < math.exp(-delta / T):
                # aceita mesmo piorando (exploracao termica)
                prob_aceit = math.exp(-delta / T)
                custo_atual = novo_custo
                linha_copia = [linha[:] for linha in puzzle.tabuleiro]
                historico.append(linha_copia)
                descricoes.append(
                    'T={:.1f}: troca ({},{}) erros {}->{}  aceito: P=exp(-{}/T)={:.0%}'.format(
                        T, i + 1, j + 1, custo_atual - delta, custo_atual, delta, prob_aceit
                    )
                )
            else:
                puzzle.tabuleiro[i][j] = estado_anterior

            T = T * self.taxa_resfriamento

        tempo = time.time() - inicio

        return {
            'nome': self.nome,
            'resolvido': puzzle.esta_resolvido(),
            'tempo': tempo,
            'passos': passos,
            'historico_passos': historico,
            'historico_celulas': historico,
            'descricoes': descricoes,
            'descricoes_passos': descricoes,
        }

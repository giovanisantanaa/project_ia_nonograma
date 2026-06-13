import time
import math
import random
from ambiente import PINTADA, VAZIA

class AgenteBuscaLocal:
    def __init__(self):
        self.nome = 'Busca Local (Simulated Annealing)'
        self.temperatura_inicial = 100.0
        self.taxa_resfriamento = 0.999

    def calcular_erros(self, puzzle):
        # a funcao de custo e quantas linhas e colunas estao inconsistentes
        erros = 0
        for i in range(puzzle.linhas):
            if not puzzle.linha_consistente(puzzle.tabuleiro[i], puzzle.pistas_linha[i]):
                erros += 1
                
        for j in range(puzzle.colunas):
            coluna = [puzzle.tabuleiro[i][j] for i in range(puzzle.linhas)]
            if not puzzle.linha_consistente(coluna, puzzle.pistas_coluna[j]):
                erros += 1
        return erros

    def resolver(self, puzzle):
        inicio = time.time()
        passos = 0
        
        # preenche o tabuleiro aleatoriamente para comecar
        for i in range(puzzle.linhas):
            for j in range(puzzle.colunas):
                puzzle.tabuleiro[i][j] = random.choice([PINTADA, VAZIA])

        custo_atual = self.calcular_erros(puzzle)
        T = self.temperatura_inicial

        while T > 0.01 and custo_atual > 0:
            passos += 1
            
            # escolhe uma celula aleatoria para inverter
            i = random.randint(0, puzzle.linhas - 1)
            j = random.randint(0, puzzle.colunas - 1)
            
            estado_anterior = puzzle.tabuleiro[i][j]
            puzzle.tabuleiro[i][j] = VAZIA if estado_anterior == PINTADA else PINTADA
            
            novo_custo = self.calcular_erros(puzzle)
            delta = novo_custo - custo_atual
            
            if delta < 0 or random.random() < math.exp(-delta / T):
                custo_atual = novo_custo 
            else:
                puzzle.tabuleiro[i][j] = estado_anterior 
                
            T *= self.taxa_resfriamento

        tempo = time.time() - inicio

        return {
            'nome': self.nome,
            'resolvido': puzzle.esta_resolvido(),
            'tempo': tempo,
            'passos': passos
        }

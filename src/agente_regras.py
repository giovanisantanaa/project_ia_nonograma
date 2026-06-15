# agente que resolve o nonograma usando inferencia logica
# baseado em regras que vai descobrindo as celulas com
# certeza ate nao  conseguir mais nada

import time

from ambiente import Nonograma, DESCONHECIDO, PINTADA, VAZIA
from base_ia import Problem, Node, SimpleProblemSolvingAgentProgram


def gerar_candidatos(tamanho, pista):

    if not pista:
        return [[VAZIA] * tamanho]

    resultados = []

    def backtrack(pos, idx, atual):
        if idx == len(pista):
            resultados.append(atual + [VAZIA] * (tamanho - pos))
            return

        g = pista[idx]
        espaco_min = sum(pista[idx:]) + len(pista) - idx - 1

        # tenta posicionar o grupo atual (`g`) em todas posições possíveis
        for inicio in range(pos, tamanho - espaco_min + 1):
            linha = atual + [VAZIA] * (inicio - pos) + [PINTADA] * g
            prox = inicio + g
            if prox < tamanho:
                backtrack(prox + 1, idx + 1, linha + [VAZIA])
            else:
                backtrack(prox, idx + 1, linha)

    backtrack(0, 0, [])
    return resultados


def filtrar_candidatos(linha_atual, candidatos):
    compativeis = []

    for cand in candidatos:
        valido = True
        for j, cel in enumerate(linha_atual):
            # se a célula já estiver definida, deve coincidir com o candidato
            if cel != DESCONHECIDO and cel != cand[j]:
                valido = False
                break

        if valido:
            compativeis.append(cand)

    return compativeis


def intersecao_candidatos(candidatos):
    if len(candidatos) == 0:
        return []

    tamanho = len(candidatos[0])
    resultado = []

    # retorna valor comum em cada posição se todos candidatos concordam,
    # caso contrário marca como DESCONHECIDO
    for j in range(tamanho):
        primeiro = candidatos[0][j]
        todos_iguais = True
        for cand in candidatos:
            if cand[j] != primeiro:
                todos_iguais = False
                break

        if todos_iguais:
            resultado.append(primeiro)
        else:
            resultado.append(DESCONHECIDO)

    return resultado


class ProblemaNonograma(Problem):
    def __init__(self, puzzle):
        self.puzzle = puzzle
        estado_inicial = tuple(tuple(l) for l in puzzle.tabuleiro)
        super().__init__(initial=estado_inicial)

        self.cands_linhas = [
            gerar_candidatos(puzzle.colunas, puzzle.pistas_linha[i])
            for i in range(puzzle.linhas)
        ]
        self.cands_colunas = [
            gerar_candidatos(puzzle.linhas, puzzle.pistas_coluna[j])
            for j in range(puzzle.colunas)
        ]

    def actions(self, state):
        tabuleiro = [list(l) for l in state]
        inferencias = []

        cl = [
            filtrar_candidatos(tabuleiro[i], self.cands_linhas[i])
            for i in range(self.puzzle.linhas)
        ]
        cc = [
            filtrar_candidatos(
                [tabuleiro[r][j] for r in range(self.puzzle.linhas)],
                self.cands_colunas[j],
            )
            for j in range(self.puzzle.colunas)
        ]

        # inferências por linhas: interseção de candidatos mostra células
        # que são iguais em todos os candidatos possíveis
        for i in range(self.puzzle.linhas):
            if not cl[i]:
                continue
            inter = intersecao_candidatos(cl[i])
            for j, val in enumerate(inter):
                if val != DESCONHECIDO and tabuleiro[i][j] == DESCONHECIDO:
                    inferencias.append((i, j, val))

        # inferências por colunas
        for j in range(self.puzzle.colunas):
            if not cc[j]:
                continue
            inter = intersecao_candidatos(cc[j])
            for i, val in enumerate(inter):
                if val != DESCONHECIDO and tabuleiro[i][j] == DESCONHECIDO:
                    inferencias.append((i, j, val))

        vistos = set()
        unicos = []
        for inf in inferencias:
            if (inf[0], inf[1]) not in vistos:
                vistos.add((inf[0], inf[1]))
                unicos.append(inf)
        return unicos

    def result(self, state, action):
        i, j, val = action
        tabuleiro = [list(l) for l in state]
        tabuleiro[i][j] = val
        return tuple(tuple(l) for l in tabuleiro)

    def goal_test(self, state):
        tabuleiro = [list(l) for l in state]
        p = self.puzzle

        for i, linha in enumerate(tabuleiro):
            if DESCONHECIDO in linha:
                return False
            if not p.linha_consistente(linha, p.pistas_linha[i]):
                return False

        for j in range(p.colunas):
            col = [tabuleiro[i][j] for i in range(p.linhas)]
            if not p.linha_consistente(col, p.pistas_coluna[j]):
                return False

        return True


class AgenteRegras(SimpleProblemSolvingAgentProgram):

    def __init__(self):
        super().__init__()
        self.nome = "Baseado em Regras"

    def update_state(self, state, percept):
        return percept

    def formulate_goal(self, state):
        return "resolvido"

    def formulate_problem(self, state, goal):
        return self._problema

    def search(self, problem):
        state = problem.initial
        todas = []

        while True:
            acoes = problem.actions(state)
            if not acoes:
                break
            todas.extend(acoes)

            for a in acoes:
                state = problem.result(state, a)

        return todas

    def resolver(self, puzzle):
        self._problema = ProblemaNonograma(puzzle)

        inicio = time.time()
        passos = 0

        state = self._problema.initial

        while True:
            acoes = self._problema.actions(state)
            passos += 1

            if not acoes:
                break

            # aplica cada inferência diretamente no tabuleiro
            for acao in acoes:
                state = self._problema.result(state, acao)
                i, j, val = acao
                puzzle.tabuleiro[i][j] = val

        tempo = time.time() - inicio

        return {
            "nome": self.nome,
            "resolvido": puzzle.esta_resolvido(),
            "tempo": tempo,
            "passos": passos,
        }

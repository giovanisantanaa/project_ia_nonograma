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

        # verifica linhas
        for i in range(self.puzzle.linhas):
            if not cl[i]:
                continue
            inter = intersecao_candidatos(cl[i])
            for j, val in enumerate(inter):
                if val != DESCONHECIDO and tabuleiro[i][j] == DESCONHECIDO:
                    inferencias.append((i, j, val))

        # verifica colunas
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

    def actions_com_fonte(self, state):
        tabuleiro = [list(l) for l in state]

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

        inferencias = []
        fontes = {}
        vistos = set()

        for i in range(self.puzzle.linhas):
            if not cl[i]:
                continue
            n_cands = len(cl[i])
            inter = intersecao_candidatos(cl[i])
            for j, val in enumerate(inter):
                if val != DESCONHECIDO and tabuleiro[i][j] == DESCONHECIDO and (i, j) not in vistos:
                    inferencias.append((i, j, val))
                    fontes[(i, j)] = ('linha', i, n_cands)
                    vistos.add((i, j))

        for j in range(self.puzzle.colunas):
            if not cc[j]:
                continue
            n_cands = len(cc[j])
            inter = intersecao_candidatos(cc[j])
            for i, val in enumerate(inter):
                if val != DESCONHECIDO and tabuleiro[i][j] == DESCONHECIDO and (i, j) not in vistos:
                    inferencias.append((i, j, val))
                    fontes[(i, j)] = ('coluna', j, n_cands)
                    vistos.add((i, j))

        return inferencias, fontes

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
        historico_passos = []
        historico_celulas = []
        descricoes_celulas = []
        descricoes_passos = []

        historico_celulas.append([linha[:] for linha in puzzle.tabuleiro])
        descricoes_celulas.append('Inicio: analisando candidatos de cada linha e coluna...')

        state = self._problema.initial

        while True:
            acoes, fontes = self._problema.actions_com_fonte(state)
            passos += 1

            if not acoes:
                break

            # aplica cada inferencia e registra o motivo de cada decisao
            for acao in acoes:
                state = self._problema.result(state, acao)
                i, j, val = acao
                puzzle.tabuleiro[i][j] = val

                linha_copia = []
                for linha in puzzle.tabuleiro:
                    linha_copia.append(linha[:])
                historico_celulas.append(linha_copia)

                val_simbolo = '#' if val == PINTADA else '.'
                fonte_info = fontes.get((i, j))
                if fonte_info:
                    tipo, idx_src, n_cands = fonte_info
                    if tipo == 'linha':
                        motivo = 'Linha {} ({} cands): todos concordam em ({},{})={}'.format(
                            idx_src + 1, n_cands, i + 1, j + 1, val_simbolo
                        )
                    else:
                        motivo = 'Coluna {} ({} cands): todos concordam em ({},{})={}'.format(
                            idx_src + 1, n_cands, i + 1, j + 1, val_simbolo
                        )
                else:
                    motivo = 'Inferencia: ({},{}) -> {}'.format(i + 1, j + 1, val_simbolo)
                descricoes_celulas.append(motivo)

            linha_copia = []
            for linha in puzzle.tabuleiro:
                linha_copia.append(linha[:])
            historico_passos.append(linha_copia)
            descricoes_passos.append('Rodada {}: {} celulas inferidas por logica'.format(passos, len(acoes)))

        tempo = time.time() - inicio

        return {
            "nome": self.nome,
            "resolvido": puzzle.esta_resolvido(),
            "tempo": tempo,
            "passos": passos,
            "historico_passos": historico_passos,
            "historico_celulas": historico_celulas,
            "descricoes": descricoes_celulas,
            "descricoes_passos": descricoes_passos,
        }

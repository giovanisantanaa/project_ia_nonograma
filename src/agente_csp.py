#Agente CSP vai modelar o nonograma como problema de satisfacao de restricoes
#usa A* com heuristica MRV pra escolher
#qual celula tentar preencher primeiro

import time

from ambiente import DESCONHECIDO
from base_ia import Problem, astar_search, SimpleProblemSolvingAgentProgram
from agente_regras import gerar_candidatos, filtrar_candidatos


class ProblemaCSP(Problem):

    def __init__(self, puzzle):
        self.puzzle = puzzle
        estado = tuple(tuple(l) for l in puzzle.tabuleiro)
        super().__init__(initial=estado)

        self.cands_l = []
        for i in range(puzzle.linhas):
            self.cands_l.append(gerar_candidatos(puzzle.colunas, puzzle.pistas_linha[i]))

        self.cands_c = []
        for j in range(puzzle.colunas):
            self.cands_c.append(gerar_candidatos(puzzle.linhas, puzzle.pistas_coluna[j]))


    def _candidatos_atuais(self, tabuleiro):
        cl = []
        for i in range(self.puzzle.linhas):
            cl.append(filtrar_candidatos(list(tabuleiro[i]), self.cands_l[i]))

        cc = []
        for j in range(self.puzzle.colunas):
            coluna = []
            for r in range(self.puzzle.linhas):
                coluna.append(tabuleiro[r][j])
            cc.append(filtrar_candidatos(coluna, self.cands_c[j]))

        return cl, cc


    def _dominio(self, i, j, cl, cc):
        vl = []
        for cand in cl[i]:
            if cand[j] not in vl:
                vl.append(cand[j])

        vc = []
        for cand in cc[j]:
            if cand[i] not in vc:
                vc.append(cand[i])

        
        resultado = []
        for v in vl:
            if v in vc:
                resultado.append(v)

        return resultado


    def _escolher_mrv(self, tabuleiro):
        cl, cc = self._candidatos_atuais(tabuleiro)
        melhor = None
        melhor_score = (99999, -99999)

        for i in range(self.puzzle.linhas):
            for j in range(self.puzzle.colunas):
                if tabuleiro[i][j] != DESCONHECIDO:
                    continue

                dom = self._dominio(i, j, cl, cc)
                if len(dom) == 0:
                    return None, None

                desconh_l = 0
                for c in tabuleiro[i]:
                    if c == DESCONHECIDO:
                        desconh_l = desconh_l + 1

                desconh_c = 0
                for r in range(self.puzzle.linhas):
                    if tabuleiro[r][j] == DESCONHECIDO:
                        desconh_c = desconh_c + 1

                score = (len(dom), -(desconh_l + desconh_c))
                if score < melhor_score:
                    melhor_score = score
                    melhor = (i, j, dom)

        if melhor is None:
            return None, None
        
        i, j, dom = melhor
        
        return (i, j), dom


    def actions(self, state):
        tabuleiro = state
        celula, dom = self._escolher_mrv(tabuleiro)
        if celula is None or dom is None:
            return []
        i, j = celula

        acoes = []
        dom_ordenado = sorted(dom, reverse=True)
        for v in dom_ordenado:
            acoes.append((i, j, v))
        return acoes

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
            col = []
            for i in range(p.linhas):
                col.append(tabuleiro[i][j])
            if not p.linha_consistente(col, p.pistas_coluna[j]):
                return False
        
        return True


# quantidade de celulas ainda desconhecidas
def heuristica(node):
    total = 0
    
    for linha in node.state:
        for cel in linha:
            if cel == DESCONHECIDO:
                total = total + 1
    
    return total


class AgenteCSP(SimpleProblemSolvingAgentProgram):

    def __init__(self):
        super().__init__()
        self.nome = 'CSP (A*)'

    def update_state(self, state, percept):
        return percept


    def formulate_goal(self, state):
        return 'resolvido'


    def formulate_problem(self, state, goal):
        return self._csp


    def search(self, problem):
        no = astar_search(problem, heuristica)
        if no is None:
            return []
        return no.solution()


    def resolver(self, puzzle):
        inicio = time.time()

        self._csp = ProblemaCSP(puzzle)
        acoes = self.search(self._csp)

        for acao in acoes:
            i, j, val = acao
            puzzle.tabuleiro[i][j] = val

        tempo = time.time() - inicio

        return {
            'nome': self.nome,
            'resolvido': puzzle.esta_resolvido(),
            'tempo': tempo,
            'passos': len(acoes),
        }
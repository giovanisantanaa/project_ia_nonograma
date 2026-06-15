# agente probabilistico/bayesiano para o nonograma e decide pela
# probabilidade mais alta

import time

from ambiente import DESCONHECIDO, PINTADA, VAZIA
from agente_regras import gerar_candidatos, filtrar_candidatos


def calcular_probabilidades(tabuleiro, linhas, colunas, cl, cc):
    probs = []

    for i in range(linhas):
        linha_probs = []

        for j in range(colunas):
            # pula células já definidas
            if tabuleiro[i][j] != DESCONHECIDO:
                linha_probs.append(None)
                continue

            if len(cl[i]) == 0 or len(cc[j]) == 0:
                linha_probs.append(None)
                continue

            total_l = len(cl[i])
            pintada_l = 0

            for cand in cl[i]:
                if cand[j] == PINTADA:
                    pintada_l = pintada_l + 1

            p_linha = pintada_l / total_l

            total_c = len(cc[j])
            pintada_c = 0

            for cand in cc[j]:
                if cand[i] == PINTADA:
                    pintada_c = pintada_c + 1

            p_coluna = pintada_c / total_c

            # combinação das estimativas por linha e coluna
            prob_pintada = p_linha * p_coluna
            prob_vazia = (1 - p_linha) * (1 - p_coluna)
            total = prob_pintada + prob_vazia

            if total == 0:
                p_final = 0.5
            else:
                p_final = prob_pintada / total

            linha_probs.append(p_final)

        probs.append(linha_probs)

    return probs


class AgenteProbabilistico:

    def __init__(self, limite_alto=0.85, limite_baixo=0.15):
        self.nome = "Probabilistico (Bayes)"
        self.limite_alto = limite_alto
        self.limite_baixo = limite_baixo

    def resolver(self, puzzle):
        inicio = time.time()
        passos = 0

        cands_l = []

        for i in range(puzzle.linhas):
            cands_l.append(gerar_candidatos(puzzle.colunas, puzzle.pistas_linha[i]))

        cands_c = []

        for j in range(puzzle.colunas):
            cands_c.append(gerar_candidatos(puzzle.linhas, puzzle.pistas_coluna[j]))

        # loop principal: calcula probabilidades e aplica decisões
        while not puzzle.esta_resolvido():
            passos = passos + 1

            cl = []
            for i in range(puzzle.linhas):
                cl.append(filtrar_candidatos(puzzle.tabuleiro[i], cands_l[i]))

            cc = []
            for j in range(puzzle.colunas):
                coluna = []

                for r in range(puzzle.linhas):
                    coluna.append(puzzle.tabuleiro[r][j])
                cc.append(filtrar_candidatos(coluna, cands_c[j]))

            probs = calcular_probabilidades(
                puzzle.tabuleiro, puzzle.linhas, puzzle.colunas, cl, cc
            )

            mudou = False

            for i in range(puzzle.linhas):
                for j in range(puzzle.colunas):
                    p = probs[i][j]
                    if p is None:
                        continue
                    if p >= self.limite_alto:
                        puzzle.tabuleiro[i][j] = PINTADA
                        mudou = True
                    elif p <= self.limite_baixo:
                        puzzle.tabuleiro[i][j] = VAZIA
                        mudou = True

            # se houve inferências óbvias (limiar alto/baixo), repete
            if mudou:
                continue

            melhor_i, melhor_j, melhor_p, melhor_dist = None, None, None, -1

            for i in range(puzzle.linhas):
                for j in range(puzzle.colunas):
                    p = probs[i][j]
                    if p is None:
                        continue
                    dist = abs(p - 0.5)
                    if dist > melhor_dist:
                        melhor_dist = dist
                        melhor_i, melhor_j, melhor_p = i, j, p

            # se nenhum palpite plausível, sai do loop
            if melhor_i is None:
                break

            if melhor_p >= 0.5:
                puzzle.tabuleiro[melhor_i][melhor_j] = PINTADA
            else:
                puzzle.tabuleiro[melhor_i][melhor_j] = VAZIA

        tempo = time.time() - inicio

        return {
            "nome": self.nome,
            "resolvido": puzzle.esta_resolvido(),
            "tempo": tempo,
            "passos": passos,
        }

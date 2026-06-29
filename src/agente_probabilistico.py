# agente probabilistico/bayesiano para o nonograma e decide pela
# probabilidade mais alta

import time

from ambiente import DESCONHECIDO, PINTADA, VAZIA
from agente_regras import gerar_candidatos, filtrar_candidatos


def calcular_probabilidades(tabuleiro, linhas, colunas, cl, cc):
    probs = []
    detalhes = []

    for i in range(linhas):
        linha_probs = []
        linha_det = []

        for j in range(colunas):
            if tabuleiro[i][j] != DESCONHECIDO:
                linha_probs.append(None)
                linha_det.append(None)
                continue

            if len(cl[i]) == 0 or len(cc[j]) == 0:
                linha_probs.append(None)
                linha_det.append(None)
                continue

            total_l = len(cl[i])
            pintada_l = sum(1 for cand in cl[i] if cand[j] == PINTADA)
            p_linha = pintada_l / total_l

            total_c = len(cc[j])
            pintada_c = sum(1 for cand in cc[j] if cand[i] == PINTADA)
            p_coluna = pintada_c / total_c

            prob_pintada = p_linha * p_coluna
            prob_vazia = (1 - p_linha) * (1 - p_coluna)
            total = prob_pintada + prob_vazia

            if total == 0:
                p_final = 0.5
            else:
                p_final = prob_pintada / total

            linha_probs.append(p_final)
            linha_det.append((p_linha, p_coluna, p_final))

        probs.append(linha_probs)
        detalhes.append(linha_det)

    return probs, detalhes


class AgenteProbabilistico:

    def __init__(self, limite_alto=0.85, limite_baixo=0.15):
        self.nome = "Probabilistico (Bayes)"
        self.limite_alto = limite_alto
        self.limite_baixo = limite_baixo

    def resolver(self, puzzle):
        inicio = time.time()
        passos = 0
        historico_passos = []
        historico_celulas = []
        descricoes_celulas = []
        descricoes_passos = []

        cands_l = []
        for i in range(puzzle.linhas):
            cands_l.append(gerar_candidatos(puzzle.colunas, puzzle.pistas_linha[i]))

        cands_c = []
        for j in range(puzzle.colunas):
            cands_c.append(gerar_candidatos(puzzle.linhas, puzzle.pistas_coluna[j]))

        historico_celulas.append([linha[:] for linha in puzzle.tabuleiro])
        descricoes_celulas.append('Inicio: calculando P(pintada) para cada celula...')

        # loop principal: calcula probabilidades e aplica decisoes
        while not puzzle.esta_resolvido():
            passos = passos + 1

            cl = []
            for i in range(puzzle.linhas):
                cl.append(filtrar_candidatos(puzzle.tabuleiro[i], cands_l[i]))

            cc = []
            for j in range(puzzle.colunas):
                coluna = [puzzle.tabuleiro[r][j] for r in range(puzzle.linhas)]
                cc.append(filtrar_candidatos(coluna, cands_c[j]))

            probs, detalhes = calcular_probabilidades(
                puzzle.tabuleiro, puzzle.linhas, puzzle.colunas, cl, cc
            )

            mudou = False

            for i in range(puzzle.linhas):
                for j in range(puzzle.colunas):
                    p = probs[i][j]
                    if p is None:
                        continue

                    decidido = False
                    if p >= self.limite_alto:
                        puzzle.tabuleiro[i][j] = PINTADA
                        mudou = True
                        decidido = True
                        val_simbolo = '#'
                        razao = 'P={:.0%} >= {}% -> #{}'.format(p, int(self.limite_alto * 100), '')
                    elif p <= self.limite_baixo:
                        puzzle.tabuleiro[i][j] = VAZIA
                        mudou = True
                        decidido = True
                        val_simbolo = '.'
                        razao = 'P={:.0%} <= {}% -> .{}'.format(p, int(self.limite_baixo * 100), '')

                    if decidido:
                        det = detalhes[i][j]
                        linha_copia = [linha[:] for linha in puzzle.tabuleiro]
                        historico_celulas.append(linha_copia)
                        if det:
                            pl, pc, pf = det
                            descricoes_celulas.append(
                                'Bayes ({},{}): L={:.0%} x C={:.0%} = {:.0%} -> {}'.format(
                                    i + 1, j + 1, pl, pc, pf, val_simbolo
                                )
                            )
                        else:
                            descricoes_celulas.append(
                                'Bayes ({},{}): P={:.0%} -> {}'.format(i + 1, j + 1, p, val_simbolo)
                            )

            if not mudou:
                # nenhuma celula com certeza: chuta a que tem probabilidade mais extrema
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

                if melhor_i is None:
                    break

                val = PINTADA if melhor_p >= 0.5 else VAZIA
                puzzle.tabuleiro[melhor_i][melhor_j] = val

                cl_test = [filtrar_candidatos(puzzle.tabuleiro[i], cands_l[i])
                           for i in range(puzzle.linhas)]
                cc_test = [filtrar_candidatos(
                               [puzzle.tabuleiro[r][j] for r in range(puzzle.linhas)],
                               cands_c[j])
                           for j in range(puzzle.colunas)]
                if any(len(c) == 0 for c in cl_test) or any(len(c) == 0 for c in cc_test):
                    val = VAZIA if val == PINTADA else PINTADA
                    puzzle.tabuleiro[melhor_i][melhor_j] = val

                val_simbolo = '#' if val == PINTADA else '.'

                linha_copia = [linha[:] for linha in puzzle.tabuleiro]
                historico_celulas.append(linha_copia)

                det = detalhes[melhor_i][melhor_j]
                if det:
                    pl, pc, pf = det
                    descricoes_celulas.append(
                        'Chute: ({},{}) mais extremo L={:.0%} x C={:.0%} = {:.0%} -> {}'.format(
                            melhor_i + 1, melhor_j + 1, pl, pc, pf, val_simbolo
                        )
                    )
                else:
                    descricoes_celulas.append(
                        'Chute: ({},{}) P={:.0%} -> {}'.format(melhor_i + 1, melhor_j + 1, melhor_p, val_simbolo)
                    )

            linha_copia = [linha[:] for linha in puzzle.tabuleiro]
            historico_passos.append(linha_copia)
            descricoes_passos.append('Iteracao {}: calculando P(pintada) para cada celula'.format(passos))

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

# gera graficos comparando os 4 agentes em todos os tamanhos de puzzle
# salva os graficos na pasta graph_images/

import sys
import os
from datetime import datetime

sys.path.append("src")

import matplotlib.pyplot as plt

from benchmark import rodar_benchmark
from puzzles import TAMANHOS


def organizar_por_agente_e_tamanho(resultados):
    dados = {}

    for r in resultados:
        nome = r['nome']
        tamanho = r['tamanho']

        if nome not in dados:
            dados[nome] = {}
        if tamanho not in dados[nome]:
            dados[nome][tamanho] = []

        dados[nome][tamanho].append(r)

    return dados


def calcular_media(lista, campo):
    total = 0
    for r in lista:
        total = total + r[campo]
    return total / len(lista)


def calcular_taxa_resolvido(lista):
    total = len(lista)
    resolvidos = 0
    for r in lista:
        if r['resolvido']:
            resolvidos = resolvidos + 1
    return (resolvidos / total) * 100


def organizar_por_puzzle(resultados):
    dados = {}

    for r in resultados:
        puzzle = r['puzzle']
        if puzzle not in dados:
            dados[puzzle] = []
        dados[puzzle].append(r)

    return dados


def obter_nomes_agentes(resultados):
    nomes = []
    for r in resultados:
        if r['nome'] not in nomes:
            nomes.append(r['nome'])
    return nomes


def obter_nomes_puzzles(resultados):
    nomes = []
    for r in resultados:
        if r['puzzle'] not in nomes:
            nomes.append(r['puzzle'])
    return nomes


def encontrar_resultado(lista, nome_agente):
    for r in lista:
        if r['nome'] == nome_agente:
            return r
    return None


def calcular_resumo_valor(resultados_agente, campo, tipo_resumo, multiplicador=1):
    valores = []
    for r in resultados_agente:
        valores.append(r[campo] * multiplicador)

    if tipo_resumo == 'media':
        return sum(valores) / len(valores)
    if tipo_resumo == 'min':
        return min(valores)
    if tipo_resumo == 'max':
        return max(valores)
    return 0


def formatar_valor(valor, campo):
    if campo == 'tempo':
        return f'{valor:.1f}'
    return f'{valor:.0f}'


def desenhar_barras_agrupadas(labels, series, titulo, xlabel, ylabel, arquivo, largura=0.22):
    plt.figure(figsize=(18, 8))

    indices = list(range(len(labels)))
    deslocamento_base = (len(series) - 1) * largura / 2

    for indice, serie in enumerate(series):
        posicoes = [x + (indice * largura) - deslocamento_base for x in indices]
        plt.bar(posicoes, serie['valores'], width=largura, label=serie['label'])

        for posicao, valor in zip(posicoes, serie['valores']):
            plt.text(posicao, valor, formatar_valor(valor, serie['campo']), ha='center', va='bottom', fontsize=8)

    plt.xticks(indices, labels, rotation=45, ha='right')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(titulo)
    plt.legend()
    plt.tight_layout()
    plt.savefig(arquivo)
    plt.close()


def grafico_passos_por_puzzle(resultados, pasta):
    nomes_agentes = obter_nomes_agentes(resultados)
    nomes_puzzles = obter_nomes_puzzles(resultados)
    por_puzzle = organizar_por_puzzle(resultados)

    labels = nomes_puzzles + ['media', 'menos passos', 'mais passos']
    series = []

    for nome_agente in nomes_agentes:
        resultados_agente = []
        valores = []

        for nome_puzzle in nomes_puzzles:
            resultado = encontrar_resultado(por_puzzle[nome_puzzle], nome_agente)
            if resultado is not None:
                resultados_agente.append(resultado)
                valores.append(resultado['passos'])

        valores.append(calcular_resumo_valor(resultados_agente, 'passos', 'media'))
        valores.append(calcular_resumo_valor(resultados_agente, 'passos', 'min'))
        valores.append(calcular_resumo_valor(resultados_agente, 'passos', 'max'))

        series.append({
            'label': nome_agente,
            'valores': valores,
            'campo': 'passos',
        })

    titulo = 'Passos de resolucao por agente em cada puzzle (Gerado em ' + datetime.now().strftime('%H:%M:%S') + ')'
    desenhar_barras_agrupadas(labels, series, titulo, 'Puzzle', 'Passos', pasta + '/passos_por_puzzle.png')


def grafico_tempo_por_puzzle(resultados, pasta):
    nomes_agentes = obter_nomes_agentes(resultados)
    nomes_puzzles = obter_nomes_puzzles(resultados)
    por_puzzle = organizar_por_puzzle(resultados)

    labels = nomes_puzzles + ['media', 'melhor tempo', 'pior tempo']
    series = []

    for nome_agente in nomes_agentes:
        resultados_agente = []
        valores = []

        for nome_puzzle in nomes_puzzles:
            resultado = encontrar_resultado(por_puzzle[nome_puzzle], nome_agente)
            if resultado is not None:
                resultados_agente.append(resultado)
                valores.append(resultado['tempo'] * 1000)

        valores.append(calcular_resumo_valor(resultados_agente, 'tempo', 'media', 1000))
        valores.append(calcular_resumo_valor(resultados_agente, 'tempo', 'min', 1000))
        valores.append(calcular_resumo_valor(resultados_agente, 'tempo', 'max', 1000))

        series.append({
            'label': nome_agente,
            'valores': valores,
            'campo': 'tempo',
        })

    titulo = 'Tempo de resolucao por agente em cada puzzle (Gerado em ' + datetime.now().strftime('%H:%M:%S') + ')'
    desenhar_barras_agrupadas(labels, series, titulo, 'Puzzle', 'Tempo (ms)', pasta + '/tempo_por_puzzle.png')


def grafico_percentual_resolvido_por_agente(resultados, pasta):
    nomes_agentes = obter_nomes_agentes(resultados)
    labels = nomes_agentes
    series = []

    valores = []
    for nome_agente in nomes_agentes:
        resultados_agente = []
        for r in resultados:
            if r['nome'] == nome_agente:
                resultados_agente.append(r)
        valores.append(calcular_taxa_resolvido(resultados_agente))

    series.append({
        'label': 'Resolucao',
        'valores': valores,
        'campo': 'tempo',
    })

    plt.figure(figsize=(10, 6))
    barras = plt.bar(labels, valores)
    for barra, valor in zip(barras, valores):
        plt.text(barra.get_x() + barra.get_width() / 2, valor, f'{valor:.1f}%', ha='center', va='bottom')

    plt.ylim(0, 105)
    plt.xlabel('Agente')
    plt.ylabel('Percentual resolvido (%)')
    plt.title('Percentual de puzzles resolvidos por agente (Gerado em ' + datetime.now().strftime('%H:%M:%S') + ')')
    plt.tight_layout()
    plt.savefig(pasta + '/taxa_resolvido_por_agente.png')
    plt.close()


def grafico_barras(dados, pasta, campo, arquivo, titulo, ylabel, multiplicador=1, usar_taxa_resolvido=False):
    plt.figure()

    nomes_agentes = list(dados.keys())
    largura = 0.18
    deslocamento_base = (len(nomes_agentes) - 1) * largura / 2

    for indice, nome_agente in enumerate(nomes_agentes):
        valores = []
        tamanhos = []
        for tamanho in TAMANHOS:
            if tamanho in dados[nome_agente]:
                if usar_taxa_resolvido:
                    media = calcular_taxa_resolvido(dados[nome_agente][tamanho])
                else:
                    media = calcular_media(dados[nome_agente][tamanho], campo)
                tamanhos.append(tamanho)
                valores.append(media * multiplicador)

        if tamanhos:
            posicoes = [tamanho + (indice * largura) - deslocamento_base for tamanho in tamanhos]
            plt.bar(posicoes, valores, width=largura, label=nome_agente)

    plt.xticks(TAMANHOS)
    plt.xlabel('tamanho do puzzle (NxN)')
    plt.ylabel(ylabel)
    plt.title(titulo)
    plt.legend()
    plt.savefig(pasta + '/' + arquivo)
    plt.close()


def grafico_tempo(dados, pasta):
    plt.figure()

    for nome_agente in dados:
        tamanhos = []
        tempos = []
        for tamanho in TAMANHOS:
            if tamanho in dados[nome_agente]:
                media = calcular_media(dados[nome_agente][tamanho], 'tempo')
                tamanhos.append(tamanho)
                tempos.append(media * 1000)

        plt.plot(tamanhos, tempos, marker='o', label=nome_agente)

    plt.xticks(TAMANHOS)
    plt.xlabel('tamanho do puzzle (NxN)')
    plt.ylabel('tempo medio (ms)')
    plt.title('Tempo medio por tamanho de puzzle')
    plt.legend()
    plt.savefig(pasta + '/tempo.png')
    plt.close()


def grafico_passos(dados, pasta):
    plt.figure()

    for nome_agente in dados:
        tamanhos = []
        passos = []
        for tamanho in TAMANHOS:
            if tamanho in dados[nome_agente]:
                media = calcular_media(dados[nome_agente][tamanho], 'passos')
                tamanhos.append(tamanho)
                passos.append(media)

        plt.plot(tamanhos, passos, marker='o', label=nome_agente)

    plt.xticks(TAMANHOS)
    plt.xlabel('tamanho do puzzle (NxN)')
    plt.ylabel('passos medios')
    plt.title('Passos medios por tamanho de puzzle')
    plt.legend()
    plt.savefig(pasta + '/passos.png')
    plt.close()


def grafico_taxa_resolvido(dados, pasta):
    plt.figure()

    for nome_agente in dados:
        tamanhos = []
        taxas = []
        for tamanho in TAMANHOS:
            if tamanho in dados[nome_agente]:
                taxa = calcular_taxa_resolvido(dados[nome_agente][tamanho])
                tamanhos.append(tamanho)
                taxas.append(taxa)

        plt.plot(tamanhos, taxas, marker='o', label=nome_agente)

    plt.xticks(TAMANHOS)
    plt.xlabel('tamanho do puzzle (NxN)')
    plt.ylabel('% resolvido')
    plt.title('Taxa de resolucao por tamanho de puzzle')
    plt.legend()
    plt.ylim(0, 105)
    plt.savefig(pasta + '/taxa_resolvido.png')
    plt.close()


def gerar_graficos():
    resultados = rodar_benchmark()
    dados = organizar_por_agente_e_tamanho(resultados)

    pasta = 'graph_images'
    if not os.path.exists(pasta):
        os.makedirs(pasta)

    grafico_tempo(dados, pasta)
    grafico_passos(dados, pasta)
    grafico_taxa_resolvido(dados, pasta)
    grafico_barras(dados, pasta, 'tempo', 'tempo_barras.png', 'Tempo medio por tamanho de puzzle (barras)', 'tempo medio (ms)', 1000)
    grafico_barras(dados, pasta, 'passos', 'passos_barras.png', 'Passos medios por tamanho de puzzle (barras)', 'passos medios')
    grafico_barras(dados, pasta, 'resolvido', 'taxa_resolvido_barras.png', 'Taxa de resolucao por tamanho de puzzle (barras)', '% resolvido', usar_taxa_resolvido=True)
    grafico_passos_por_puzzle(resultados, pasta)
    grafico_tempo_por_puzzle(resultados, pasta)
    grafico_percentual_resolvido_por_agente(resultados, pasta)

    print('graficos salvos na pasta ' + pasta)


if __name__ == "__main__":
    gerar_graficos()
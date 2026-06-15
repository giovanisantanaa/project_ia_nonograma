# gera graficos comparando os 4 agentes em todos os tamanhos de puzzle
# salva os graficos na pasta graph_images/

import sys
import os

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

    print('graficos salvos na pasta ' + pasta)


if __name__ == "__main__":
    gerar_graficos()
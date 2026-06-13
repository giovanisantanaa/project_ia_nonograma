#roda todos os agentes em todos os puzzles e  faz
# a organização dos resultados
# numa tabela pra comparar o desempenho

import sys

sys.path.append("src")

from agente_regras import AgenteRegras
from agente_csp import AgenteCSP
from agente_probabilistico import AgenteProbabilistico
from puzzles import puzzles_5x5, puzzles_10x10


def rodar_benchmark():
    agentes = [AgenteRegras(), AgenteCSP(), AgenteProbabilistico()]
    puzzles = puzzles_5x5() + puzzles_10x10()

    resultados = []

    for puzzle in puzzles:
        for agente in agentes:
            p = puzzle.copiar()
            resultado = agente.resolver(p)
            resultado['puzzle'] = puzzle.nome
            resultados.append(resultado)

    return resultados


def imprimir_tabela(resultados):
    print("{:<20} {:<25} {:<10} {:<12} {:<8}".format( "puzzle", "agente", "resolvido", "tempo (s)", "passos" ))
    print("-" * 80)

    for r in resultados:
        print("{:<20} {:<25} {:<10} {:<12.6f} {:<8}".format(
            r['puzzle'], r['nome'], str(r['resolvido']), r['tempo'], r['passos']
        ))


if __name__ == "__main__":
    resultados = rodar_benchmark()
    imprimir_tabela(resultados)
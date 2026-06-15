#roda todos os agentes em todos os puzzles e organiza os resultados numa tabela pra comparar desempenho

import sys

sys.path.append("src")

from agente_regras import AgenteRegras
from agente_csp import AgenteCSP
from agente_probabilistico import AgenteProbabilistico
from agente_local import AgenteBuscaLocal
from puzzles import puzzles_todos


def rodar_benchmark():
    agentes = [AgenteRegras(), AgenteCSP(), AgenteProbabilistico(), AgenteBuscaLocal()]
    puzzles = puzzles_todos()

    resultados = []

    for puzzle in puzzles:
        for agente in agentes:
            p = puzzle.copiar()
            resultado = agente.resolver(p)
            resultado['puzzle'] = puzzle.nome
            resultado['tamanho'] = puzzle.linhas
            resultados.append(resultado)

    return resultados


def imprimir_tabela(resultados):
    print("{:<20} {:<25} {:<10} {:<12} {:<8}".format(
        "puzzle", "agente", "resolvido", "tempo (ms)", "passos"
    ))
    print("-" * 80)

    for r in resultados:
        tempo_ms = r['tempo'] * 1000
        print("{:<20} {:<25} {:<10} {:<12.3f} {:<8}".format(
            r['puzzle'], r['nome'], str(r['resolvido']), tempo_ms, r['passos']
        ))


if __name__ == "__main__":
    resultados = rodar_benchmark()
    imprimir_tabela(resultados)
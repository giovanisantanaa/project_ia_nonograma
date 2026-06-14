import sys

sys.path.append("src")

from agente_regras import AgenteRegras
from agente_csp import AgenteCSP
from agente_probabilistico import AgenteProbabilistico
# from puzzles import puzzles_5x5, puzzles_10x10
# tentativa de puzzle_gen (puzzles2.py)
from puzzles2 import carregar_puzzles_csv, gerar_puzzles_unicos, DEFAULT_PUZZLES_CSV


def rodar_benchmark():
    agentes = [AgenteRegras(), AgenteCSP(), AgenteProbabilistico()]
    # puzzles = puzzles_5x5() + puzzles_10x10()
    # tentativa de puzzle_gen (puzzles2.py)
    try:
        puzzles = carregar_puzzles_csv(DEFAULT_PUZZLES_CSV)
    except FileNotFoundError:
        puzzles = gerar_puzzles_unicos(5, 30, arquivo_csv="puzzles.csv")

    resultados = []

    for puzzle in puzzles:
        for agente in agentes:
            p = puzzle.copiar()
            resultado = agente.resolver(p)
            resultado['puzzle'] = puzzle.nome
            resultados.append(resultado)

    return resultados


def imprimir_tabela(resultados):
    print("{:<20} {:<25} {:<10} {:<12} {:<8}".format("puzzle", "agente", "resolvido", "tempo (ms)", "passos"))
    print("-" * 80)

    for r in resultados:
        tempo_ms = r['tempo'] * 1000
        print("{:<20} {:<25} {:<10} {:<12.3f} {:<8}".format(r['puzzle'], r['nome'], str(r['resolvido']), tempo_ms, r['passos']))


if __name__ == "__main__":
    resultados = rodar_benchmark()
    imprimir_tabela(resultados)
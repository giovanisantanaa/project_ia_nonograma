import os
from datetime import datetime

import matplotlib.pyplot as plt
from benchmark import rodar_benchmark


OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "graph_images")


def gerar_graficos():
    resultados = rodar_benchmark()

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Preserva a ordem dos puzzles e organiza métricas por agente
    ordem_puzzles = []
    dados_por_puzzle = {}
    agentes = []

    for resultado in resultados:
        puzzle = resultado["puzzle"]
        agente = resultado["nome"]

        if puzzle not in dados_por_puzzle:
            dados_por_puzzle[puzzle] = {}
            ordem_puzzles.append(puzzle)
        dados_por_puzzle[puzzle][agente] = resultado

        if agente not in agentes:
            agentes.append(agente)

    timestamp = datetime.now().strftime("%H-%M-%S")
    timestamp_label = datetime.now().strftime("%H:%M:%S")

    # Organiza dados para cada agente em cada puzzle
    x = list(ordem_puzzles)
    tempos_por_agente = {agente: [] for agente in agentes}
    passos_por_agente = {agente: [] for agente in agentes}

    for puzzle in x:
        for agente in agentes:
            resultado = dados_por_puzzle.get(puzzle, {}).get(agente, None)
            if resultado is None:
                tempos_por_agente[agente].append(0)
                passos_por_agente[agente].append(0)
            else:
                tempos_por_agente[agente].append(resultado["tempo"] * 1000)
                passos_por_agente[agente].append(resultado["passos"])

    cores = ["#4c72b0", "#dd8452", "#55a868", "#8172b3", "#64b5cd"]
    largura = 0.15
    indice = range(len(x))

    # Tempo total de cada agente em cada puzzle
    plt.figure(figsize=(14, 8))
    for idx, agente in enumerate(agentes):
        deslocamento = [i + largura * idx for i in indice]
        valores = tempos_por_agente[agente]
        barras = plt.bar(deslocamento, valores, width=largura, label=agente, color=cores[idx % len(cores)])
        for barra, valor in zip(barras, valores):
            altura = barra.get_height()
            plt.text(
                barra.get_x() + barra.get_width() / 2,
                altura,
                f"{valor:.1f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    plt.xlabel("Puzzle")
    plt.ylabel("Tempo (ms)")
    plt.title(f"Tempo de resolução por agente em cada puzzle (Gerado em {timestamp_label})")
    plt.xticks([i + largura * (len(agentes) - 1) / 2 for i in indice], x, rotation=45, ha="right")
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.tight_layout()
    tempo_image_path = os.path.join(OUTPUT_DIR, f"tempo_{timestamp}.png")
    plt.savefig(tempo_image_path)
    plt.close()

    # Passos por agente em cada puzzle
    plt.figure(figsize=(14, 8))
    for idx, agente in enumerate(agentes):
        deslocamento = [i + largura * idx for i in indice]
        valores = passos_por_agente[agente]
        barras = plt.bar(deslocamento, valores, width=largura, label=agente, color=cores[idx % len(cores)])
        for barra, valor in zip(barras, valores):
            altura = barra.get_height()
            plt.text(
                barra.get_x() + barra.get_width() / 2,
                altura,
                str(valor),
                ha="center",
                va="bottom",
                fontsize=8,
            )

    plt.xlabel("Puzzle")
    plt.ylabel("Passos")
    plt.title(f"Passos de resolução por agente em cada puzzle (Gerado em {timestamp_label})")
    plt.xticks([i + largura * (len(agentes) - 1) / 2 for i in indice], x, rotation=45, ha="right")
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.tight_layout()
    passos_image_path = os.path.join(OUTPUT_DIR, f"passos_{timestamp}.png")
    plt.savefig(passos_image_path)
    plt.close()

    return [tempo_image_path, passos_image_path]


if __name__ == "__main__":
    gerar_graficos()

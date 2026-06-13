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

    # keep original puzzle count
    original_count = len(x)

    # --- Tempo chart: puzzles + média + melhor tempo + pior tempo
    x_tempo = x + ["média", "melhor tempo", "pior tempo"]
    indice_tempo = range(len(x_tempo))

    plt.figure(figsize=(14, 8))
    for idx, agente in enumerate(agentes):
        # base values per puzzle
        base_vals = list(tempos_por_agente[agente])
        if original_count > 0:
            avg = sum(base_vals) / original_count
            nonzero = [v for v in base_vals if v > 0]
            best = min(nonzero) if nonzero else 0
            worst = max(base_vals) if base_vals else 0
        else:
            avg = best = worst = 0

        valores = base_vals + [avg, best, worst]
        deslocamento = [i + largura * idx for i in indice_tempo]
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
    plt.xticks([i + largura * (len(agentes) - 1) / 2 for i in indice_tempo], x_tempo, rotation=45, ha="right")
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.tight_layout()
    tempo_image_path = os.path.join(OUTPUT_DIR, f"{timestamp}_tempo.png")
    plt.savefig(tempo_image_path)
    plt.close()

    # --- Passos chart: puzzles + média + menos passos + mais passos
    x_passos = x + ["média", "menos passos", "mais passos"]
    indice_passos = range(len(x_passos))

    plt.figure(figsize=(14, 8))
    for idx, agente in enumerate(agentes):
        base_vals = list(passos_por_agente[agente])
        if original_count > 0:
            avg_p = sum(base_vals) / original_count
            nonzero_p = [v for v in base_vals if v > 0]
            least = min(nonzero_p) if nonzero_p else 0
            most = max(base_vals) if base_vals else 0
        else:
            avg_p = least = most = 0

        valores_p = base_vals + [avg_p, least, most]
        deslocamento = [i + largura * idx for i in indice_passos]
        barras = plt.bar(deslocamento, valores_p, width=largura, label=agente, color=cores[idx % len(cores)])
        for barra, valor in zip(barras, valores_p):
            altura = barra.get_height()
            plt.text(
                barra.get_x() + barra.get_width() / 2,
                altura,
                f"{int(valor)}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    plt.xlabel("Puzzle")
    plt.ylabel("Passos")
    plt.title(f"Passos de resolução por agente em cada puzzle (Gerado em {timestamp_label})")
    plt.xticks([i + largura * (len(agentes) - 1) / 2 for i in indice_passos], x_passos, rotation=45, ha="right")
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.tight_layout()
    passos_image_path = os.path.join(OUTPUT_DIR, f"{timestamp}_passos.png")
    plt.savefig(passos_image_path)
    plt.close()

    # Percentual de puzzles resolvidos por agente (use only actual puzzles count)
    total_puzzles = original_count if original_count > 0 else 1
    porcentagens = []
    for agente in agentes:
        count = 0
        for puzzle in x:
            res = dados_por_puzzle.get(puzzle, {}).get(agente)
            if res and res.get("resolvido"):
                count += 1
        porcentagens.append((count / total_puzzles) * 100)

    plt.figure(figsize=(10, 6))
    barras = plt.bar(agentes, porcentagens, color=[cores[i % len(cores)] for i in range(len(agentes))])
    for barra, valor in zip(barras, porcentagens):
        plt.text(
            barra.get_x() + barra.get_width() / 2,
            barra.get_height(),
            f"{valor:.1f}%",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.ylim(0, 100)
    plt.xlabel("Agente")
    plt.ylabel("Percentual resolvido (%)")
    plt.title(f"Percentual de puzzles resolvidos por agente (Gerado em {timestamp_label})")
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.tight_layout()
    resolvido_image_path = os.path.join(OUTPUT_DIR, f"{timestamp}_taxa_resolvido.png")
    plt.savefig(resolvido_image_path)
    plt.close()

    return [tempo_image_path, passos_image_path, resolvido_image_path]


if __name__ == "__main__":
    gerar_graficos()

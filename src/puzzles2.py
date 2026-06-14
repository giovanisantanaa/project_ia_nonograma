import csv
import json
import os
import random
import time

from ambiente import Nonograma
from agente_csp import AgenteCSP, ProblemaCSP

DEFAULT_PUZZLES_CSV = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "puzzles.csv"))


def calcular_pistas(desenho):
    linhas = len(desenho)
    colunas = len(desenho[0])

    pistas_linha = []
    for i in range(linhas):
        grupos = []
        contador = 0

        for j in range(colunas):
            if desenho[i][j] == 1:
                contador += 1
            else:
                if contador > 0:
                    grupos.append(contador)
                    contador = 0

        if contador > 0:
            grupos.append(contador)
        if len(grupos) == 0:
            grupos = [0]

        pistas_linha.append(grupos)

    pistas_coluna = []
    for j in range(colunas):
        grupos = []
        contador = 0

        for i in range(linhas):
            if desenho[i][j] == 1:
                contador += 1
            else:
                if contador > 0:
                    grupos.append(contador)
                    contador = 0

        if contador > 0:
            grupos.append(contador)
        if len(grupos) == 0:
            grupos = [0]

        pistas_coluna.append(grupos)

    return pistas_linha, pistas_coluna


def criar_puzzle(desenho, nome):
    pistas_linha, pistas_coluna = calcular_pistas(desenho)
    return Nonograma(pistas_linha, pistas_coluna, nome=nome)





def _count_solutions(puzzle, max_solutions=2, timeout=10):
    problema = ProblemaCSP(puzzle)
    inicio = time.time()
    contador = 0

    def busca(estado):
        nonlocal contador
        if contador >= max_solutions or time.time() - inicio > timeout:
            return

        celula, dominio = problema._escolher_mrv(estado)
        if celula is None:
            if problema.goal_test(estado):
                contador += 1
            return

        i, j = celula
        for valor in sorted(dominio):
            if contador >= max_solutions or time.time() - inicio > timeout:
                break
            proximo_estado = problema.result(estado, (i, j, valor))
            busca(proximo_estado)

    busca(problema.initial)
    return contador


def validar_unica_solucao(puzzle, timeout=10):
    agente = AgenteCSP()
    copia = puzzle.copiar()
    resultado = agente.resolver(copia)
    if not resultado.get("resolvido"):
        return False

    num_sol = _count_solutions(puzzle, max_solutions=2, timeout=timeout)
    return num_sol == 1


def gerar_puzzles_unicos(tamanho, quantidade, arquivo_csv="puzzles.csv", timeout=10, max_tentativas=1000):
    if tamanho not in {5, 10, 15, 20, 25}:
        raise ValueError("Tamanho inválido. Use 5, 10, 15, 20 ou 25.")

    puzzles = []
    vistos = set()
    tentativas = 0

    while len(puzzles) < quantidade and tentativas < max_tentativas:
        tentativas += 1
        desenho = [[random.randint(0, 1) for _ in range(tamanho)] for _ in range(tamanho)]
        puzzle = criar_puzzle(desenho, f"puzzle_{tamanho}x{tamanho}_{len(puzzles)+1}")
        chave = json.dumps({
            "pistas_linha": puzzle.pistas_linha,
            "pistas_coluna": puzzle.pistas_coluna,
        }, sort_keys=True)

        if chave in vistos:
            continue

        if validar_unica_solucao(puzzle, timeout=timeout):
            vistos.add(chave)
            puzzles.append({
                "nome": puzzle.nome,
                "tamanho": tamanho,
                "pistas_linha": puzzle.pistas_linha,
                "pistas_coluna": puzzle.pistas_coluna,
                "desenho": desenho,
            })

    if not puzzles:
        raise RuntimeError("Nenhum puzzle válido foi gerado. Tente aumentar max_tentativas ou timeout.")

    caminho_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", arquivo_csv))
    os.makedirs(os.path.dirname(caminho_csv), exist_ok=True)

    with open(caminho_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["nome", "tamanho", "pistas_linha", "pistas_coluna", "desenho"])
        writer.writeheader()
        for puzzle in puzzles:
            writer.writerow({
                "nome": puzzle["nome"],
                "tamanho": puzzle["tamanho"],
                "pistas_linha": json.dumps(puzzle["pistas_linha"], ensure_ascii=False),
                "pistas_coluna": json.dumps(puzzle["pistas_coluna"], ensure_ascii=False),
                "desenho": json.dumps(puzzle["desenho"], ensure_ascii=False),
            })

    return caminho_csv


def carregar_puzzles_csv(caminho_csv=None):
    if caminho_csv is None:
        caminho_csv = DEFAULT_PUZZLES_CSV
    caminho_csv = os.path.abspath(caminho_csv)
    if not os.path.exists(caminho_csv):
        raise FileNotFoundError(f"Arquivo CSV não encontrado: {caminho_csv}")

    puzzles = []
    with open(caminho_csv, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            pistas_linha = json.loads(row["pistas_linha"])
            pistas_coluna = json.loads(row["pistas_coluna"])
            nome = row.get("nome") or f"puzzle_{len(puzzles)+1}"
            puzzles.append(Nonograma(pistas_linha, pistas_coluna, nome=nome))

    return puzzles


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Gerar nonograms com solução única verificada pelo agente CSP.")
    parser.add_argument("--tamanho", type=int, choices=[5, 10, 15, 20, 25], default=5, help="Tamanho do puzzle")
    parser.add_argument("--quantidade", type=int, default=1, help="Número de puzzles a gerar")
    parser.add_argument("--csv", default="puzzles.csv", help="Arquivo CSV de saída")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout de verificação por puzzle em segundos")
    parser.add_argument("--max-tentativas", type=int, default=1000, help="Número máximo de tentativas para gerar puzzles válidos")

    args = parser.parse_args()
    caminho = gerar_puzzles_unicos(
        args.tamanho,
        args.quantidade,
        arquivo_csv=args.csv,
        timeout=args.timeout,
        max_tentativas=args.max_tentativas,
    )
    print(f"Puzzles gerados e salvos em: {caminho}")

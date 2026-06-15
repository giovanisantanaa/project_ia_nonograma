import sys

sys.path.append("src")

from puzzles import puzzles_5x5, puzzles_10x10
from agente_regras import AgenteRegras
from agente_csp import AgenteCSP
from agente_probabilistico import AgenteProbabilistico
from agente_local import AgenteBuscaLocal


def pegar_puzzle(nome):
    for puzzle in puzzles_5x5():
        if puzzle.nome == nome:
            return puzzle
    return None


def test_agente_regras_resolve_cruz():
    puzzle = pegar_puzzle("cruz 5x5")
    p = puzzle.copiar()
    agente = AgenteRegras()
    resultado = agente.resolver(p)
    assert resultado["resolvido"] == True


def test_agente_csp_resolve_cruz():
    puzzle = pegar_puzzle("cruz 5x5")
    p = puzzle.copiar()
    agente = AgenteCSP()
    resultado = agente.resolver(p)
    assert resultado["resolvido"] == True


def test_agente_csp_sempre_resolve():
    for puzzle in puzzles_5x5():
        p = puzzle.copiar()
        agente = AgenteCSP()
        resultado = agente.resolver(p)
        assert resultado["resolvido"] == True


def test_agente_probabilistico_resolve_quadrado():
    puzzle = pegar_puzzle("quadrado 5x5")
    p = puzzle.copiar()
    agente = AgenteProbabilistico()
    resultado = agente.resolver(p)
    assert resultado["resolvido"] == True


def test_agente_csp_tem_historico():
    puzzle = pegar_puzzle("cruz 5x5")
    p = puzzle.copiar()
    agente = AgenteCSP()
    resultado = agente.resolver(p)
    assert len(resultado["historico_passos"]) == resultado["passos"]
    assert len(resultado["historico_celulas"]) == resultado["passos"]


def test_agente_busca_local_retorna_resultado():
    puzzle = pegar_puzzle("cruz 5x5")
    p = puzzle.copiar()
    agente = AgenteBuscaLocal()
    resultado = agente.resolver(p)
    assert "resolvido" in resultado
    assert "historico_passos" in resultado
    assert "historico_celulas" in resultado
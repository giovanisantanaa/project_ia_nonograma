import sys
sys.path.append("src")

from ambiente import Nonograma, DESCONHECIDO, PINTADA, VAZIA


def test_criacao_tabuleiro_vazio():
    p = Nonograma([[1], [1]], [[1], [1]], nome="teste")
    assert p.linhas == 2
    assert p.colunas == 2
    for linha in p.tabuleiro:
        for celula in linha:
            assert celula == DESCONHECIDO


def test_linha_consistente():
    p = Nonograma([[1]], [[1]], nome="teste")
    linha = [PINTADA, VAZIA, VAZIA]
    assert p.linha_consistente(linha, [1]) == True


def test_linha_inconsistente():
    p = Nonograma([[1]], [[1]], nome="teste")
    linha = [PINTADA, PINTADA, VAZIA]
    assert p.linha_consistente(linha, [1]) == False


def test_esta_resolvido_false_quando_vazio():
    p = Nonograma([[1], [1]], [[1], [1]], nome="teste")
    assert p.esta_resolvido() == False


def test_copiar_gera_tabuleiro_novo():
    p1 = Nonograma([[1], [1]], [[1], [1]], nome="teste")
    p1.tabuleiro[0][0] = PINTADA

    p2 = p1.copiar()
    assert p2.tabuleiro[0][0] == DESCONHECIDO
#banco de puzzles de nonograma

from ambiente import Nonograma


def calcular_pistas(desenho):
    linhas = len(desenho)
    colunas = len(desenho[0])

    pistas_linha = []
    for i in range(linhas):
        grupos = []
        contador = 0
        
        for j in range(colunas):
            if desenho[i][j] == 1:
                contador = contador + 1
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
                contador = contador + 1
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


#desenhos 5x5
#pintada: 1
#vazia: 0

DESENHO_CRUZ = [
    [0, 0, 1, 0, 0],
    [0, 0, 1, 0, 0],
    [1, 1, 1, 1, 1],
    [0, 0, 1, 0, 0],
    [0, 0, 1, 0, 0],
]

DESENHO_QUADRADO = [
    [1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1],
]

DESENHO_X = [
    [1, 0, 0, 0, 1],
    [0, 1, 0, 1, 0],
    [0, 0, 1, 0, 0],
    [0, 1, 0, 1, 0],
    [1, 0, 0, 0, 1],
]


DESENHO_CORACAO = [
    [0, 1, 0, 1, 0],
    [1, 0, 1, 0, 1],
    [1, 0, 0, 0, 1],
    [0, 1, 0, 1, 0],
    [0, 0, 1, 0, 0],
]

TORRE = [
    [1, 0, 1, 0, 1],
    [1, 1, 1, 1, 1],
    [0, 1, 1, 1, 0],
    [0, 1, 0, 1, 0],
    [0, 1, 1, 1, 0],
]

XADREZ = [
    [1, 0, 1, 0, 1],
    [0, 1, 0, 1, 0],
    [1, 0, 1, 0, 1],
    [0, 1, 0, 1, 0],
    [1, 0, 1, 0, 1],
]

SORRISO = [
    [0, 1, 0, 1, 0],
    [0, 1, 0, 1, 0],
    [0, 0, 0, 0, 0],
    [1, 0, 0, 0, 1],
    [0, 1, 1, 1, 0],
]

ALEATORIO = [
    [1, 0, 1, 1, 0],
    [0, 1, 0, 1, 0],
    [1, 0, 1, 0, 1],
    [0, 1, 0, 1, 0],
    [0, 1, 1, 0, 0],
]

def puzzles_5x5():
    lista = []
    lista.append(criar_puzzle(DESENHO_CRUZ, "cruz 5x5"))
    lista.append(criar_puzzle(DESENHO_QUADRADO, "quadrado 5x5"))
    lista.append(criar_puzzle(DESENHO_X, "x 5x5"))
    lista.append(criar_puzzle(DESENHO_CORACAO, "coracao 5x5"))
    lista.append(criar_puzzle(TORRE, "torre 5x5"))
    lista.append(criar_puzzle(XADREZ, "xadrez 5x5"))
    lista.append(criar_puzzle(SORRISO, "sorriso 5x5"))
    return lista
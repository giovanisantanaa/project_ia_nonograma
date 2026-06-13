DESCONHECIDO = 0
PINTADA = 1
VAZIA = -1

class Nonograma:
    def __init__(self, pistas_linha, pistas_coluna, nome='Puzzle'):
        self.pistas_linha = pistas_linha
        self.pistas_coluna = pistas_coluna
        self.nome = nome
        self.linhas = len(pistas_linha)
        self.colunas = len(pistas_coluna)
        self.tabuleiro = []
        
        for i in range(self.linhas):
            linha = []
            for j in range(self.colunas):
                linha.append(DESCONHECIDO)
            self.tabuleiro.append(linha)
            
    def linha_consistente(self, linha, pista):
        grupos = []
        contador = 0
        
        for celula in linha:
            if celula == PINTADA:
                contador += 1
            else:
                if contador > 0:
                    grupos.append(contador)
                    contador = 0
        if contador > 0:
            grupos.append(contador)
            
        pista_certa = []
        
        for i in pista:
            if i > 0:
                pista_certa.append(i)
                
        return grupos == pista_certa
    
    
    def esta_resolvido(self):
        for i in range(self.linhas):
            linha = self.tabuleiro[i]
            
            if DESCONHECIDO in linha:
                return False
            
            if not self.linha_consistente(linha, self.pistas_linha[i]):
                return False
            
        for j in range(self.colunas):
            coluna = []
            for i in range(self.linhas):
                coluna.append(self.tabuleiro[i][j])
            
            if not self.linha_consistente(coluna, self.pistas_coluna[j]):
                return False
            
        return True
    
    
    def copiar(self):
        novo = Nonograma(self.pistas_linha, self.pistas_coluna, self.nome)
        return novo
    
    def __repr__(self):
        simbolos = {DESCONHECIDO: '?', PINTADA: '#', VAZIA: '.'}
        texto = ''
        for linha in self.tabuleiro:
            partes = []
            for c in linha:
                partes.append(simbolos[c])
            texto = texto + ' '.join(partes) + '\n'
        return texto
# IA de Nonogramas

Projeto da disciplina **IMD3001 - Introdução à Inteligência Artificial (UFRN)**

## Integrantes

* Giovani Macedo
* Ítalo Nardy
* Paulo Morais

## Objetivo

O projeto implementa e compara quatro agentes de Inteligência Artificial capazes de resolver Nonogramas de diferentes tamanhos (de 5x5 até 25x25), utilizando métodos estudados na disciplina: inferência lógica, CSP com busca A*, raciocínio probabilístico/bayesiano e busca local.

## Modelagem PEAS

* **Performance:** porcentagem de células corretas, resolução completa do puzzle, tempo de execução e número de passos.
* **Ambiente:** o tabuleiro do nonograma (matriz NxN) e as pistas de cada linha e coluna. Trata-se de um ambiente totalmente observável e determinístico.
* **Atuadores:** preencher uma célula como **PINTADA** ou **VAZIA**.
* **Sensores:** o estado atual do tabuleiro (células já decididas) e as pistas de cada linha e coluna.

## Os 4 Agentes

### 1. Agente Baseado em Regras (`src/agente_regras.py`)

Para cada linha e coluna, o agente gera todos os arranjos possíveis que satisfazem a pista (`gerar_candidatos`), filtra aqueles compatíveis com o estado atual do tabuleiro (`filtrar_candidatos`) e, quando todas as possibilidades restantes concordam sobre o valor de uma célula, marca essa célula com certeza (`intersecao_candidatos`).

O processo é repetido até que nenhuma nova inferência possa ser realizada (ponto fixo). O agente é modelado como um `Problem` (baseado no material da disciplina), em que cada ação corresponde a uma inferência lógica.

**Limitação:** o agente só realiza marcações quando possui 100% de certeza. Em puzzles ambíguos, pode interromper a execução sem resolver completamente o tabuleiro.

### 2. CSP com A* (`src/agente_csp.py`)

O problema é modelado como um CSP (Problema de Satisfação de Restrições), em que cada célula representa uma variável com domínio `{PINTADA, VAZIA}`.

Antes da busca, é realizada uma propagação de restrições semelhante a uma versão simplificada do AC-3: toda célula que possui apenas um valor possível é imediatamente decidida. Para as células restantes, o agente utiliza busca A* com:

* Heurística: número de células ainda desconhecidas;
* Seleção de variáveis: heurística MRV (*Minimum Remaining Values*).

Como a busca completa pode se tornar inviável em puzzles muito ambíguos, o algoritmo possui um limite de nós expandidos. Caso esse limite seja atingido, o agente completa o tabuleiro de forma gulosa utilizando MRV, sem realizar backtracking.

**Limitação:** quando o limite de nós é alcançado, a solução gulosa não garante a resolução completa do puzzle.

### 3. Agente Probabilístico / Bayesiano (`src/agente_probabilistico.py`)

Para cada célula desconhecida, o agente calcula:

* `P(linha)`: fração dos candidatos válidos da linha em que a célula está pintada;
* `P(coluna)`: fração dos candidatos válidos da coluna em que a célula está pintada.

Essas probabilidades são combinadas utilizando a regra do produto com normalização, baseada no Teorema de Bayes (de forma semelhante ao laboratório do agente probabilístico do Mundo de Wumpus).

O agente decide automaticamente células com probabilidade muito alta ou muito baixa. Caso nenhuma célula ultrapasse os limiares definidos, escolhe a célula com a probabilidade mais extrema (decisão MAP — *Maximum A Posteriori*).

**Limitação:** trata-se de uma abordagem gulosa, sem backtracking. Assim, decisões incorretas podem comprometer a resolução de puzzles mais ambíguos.

### 4. Busca Local — Simulated Annealing (`src/agente_local.py`)

O agente inicia com um tabuleiro completamente aleatório. A cada iteração, seleciona uma célula aleatória e inverte seu valor.

A função de custo corresponde ao número de linhas e colunas inconsistentes com as pistas. Se a alteração reduz o custo, ela é aceita. Caso contrário, pode ser aceita com uma probabilidade dada por:

`exp(-delta/T)`

Essa probabilidade diminui à medida que a temperatura do sistema é reduzida.

A execução termina quando:

* O custo atinge zero;
* A temperatura se torna muito baixa;
* O limite de iterações é alcançado.

**Limitação:** a função de custo varia pouco a cada alteração de célula. Em puzzles maiores, isso pode dificultar a convergência e fazer com que o algoritmo permaneça preso em regiões de baixa qualidade da busca.

## Histórico de Animação

Todos os agentes retornam, além do resultado (`resolvido`, `tempo` e `passos`), dois históricos contendo snapshots do tabuleiro:

* `historico_passos`: um snapshot por iteração do laço principal do agente;
* `historico_celulas`: um snapshot para cada célula decidida individualmente.

A interface utiliza esses históricos para animar o processo de resolução.

## Estrutura do Projeto

```text
project_ia_nonograma/

├── main.py                     # Executa o benchmark e abre a interface
├── requirements.txt

├── src/
│   ├── base_ia.py              # Problem, Node, BFS/DFS/Greedy/A* (material da disciplina)
│   ├── ambiente.py             # Classe Nonograma (tabuleiro, pistas e validação)
│   ├── puzzles.py              # Banco de puzzles (5x5 a 25x25) + gerador aleatório
│   ├── agente_regras.py        # Agente 1: baseado em regras
│   ├── agente_csp.py           # Agente 2: CSP com A* e propagação
│   ├── agente_probabilistico.py# Agente 3: probabilístico/bayesiano
│   ├── agente_local.py         # Agente 4: busca local (Simulated Annealing)
│   ├── benchmark.py            # Executa os 4 agentes em todos os puzzles
│   ├── graph_gen.py            # Gera gráficos comparativos (graph_images/)
│   └── interface.py            # Interface gráfica (Tkinter)

└── tests/
    ├── test_ambiente.py
    └── test_agentes.py
```

## Como Executar

Para executar o benchmark e abrir a interface gráfica:

```bash
python main.py
```

### Interface Gráfica

Na interface é possível:

* Escolher um puzzle do banco (5x5 a 25x25);
* Utilizar o modo **Puzzle Aleatório**, que gera um tabuleiro aleatório do tamanho escolhido;
* Selecionar um dos quatro agentes;
* Executar a resolução clicando em **Resolver**;
* Acompanhar a animação utilizando os controles **Play**, **Pause** e **Avançar**.

O modo **Por Passos / Célula a Célula** permite alterar o nível de detalhamento da animação.

## Geração de Gráficos Comparativos

```bash
python src/graph_gen.py
```

Serão gerados gráficos em `graph_images/` comparando os quatro agentes:

* `tempo.png`, `passos.png`, `taxa_resolvido.png` — gráficos de linha por tamanho;
* `tempo_barras.png`, `passos_barras.png`, `taxa_resolvido_barras.png` — gráficos de barras por tamanho;
* `tempo_por_puzzle.png`, `passos_por_puzzle.png` — gráficos de barras por puzzle individual;
* `taxa_resolvido_por_agente.png` — taxa total de resolução por agente.

## Testes

```bash
python -m pytest tests/ -v
```

## Dificuldades e Limitações Encontradas no Desenvolvimento

* O agente CSP, em sua modelagem inicial (busca A* pura, decidindo uma célula por vez via MRV), apresentava execução extremamente lenta em puzzles 15x15 ou maiores. Isso ocorria porque alguns desenhos possuem elevado grau de ambiguidade, provocando uma explosão no número de estados explorados pela busca. O problema foi mitigado em duas etapas: primeiro, adicionando uma fase de propagação de restrições antes da busca, capaz de resolver muitos puzzles sem necessidade de exploração; depois, impondo um limite de nós expandidos pelo A*, com um preenchimento guloso como mecanismo de fallback. Mesmo assim, em puzzles muito ambíguos (como alguns 20x20), o agente ainda pode não alcançar 100% de resolução.

* O agente probabilístico, em sua primeira versão, utilizava uma média simples entre as probabilidades calculadas para a linha e para a coluna. Em determinados puzzles, isso fazia com que o agente entrasse em ciclos sem conseguir decidir nenhuma célula. A estratégia foi substituída pela combinação probabilística baseada no Teorema de Bayes (regra do produto com normalização), reduzindo significativamente esse comportamento. Entretanto, como o agente é guloso e não realiza backtracking, ainda pode assumir decisões incorretas e comprometer a resolução completa de puzzles maiores ou mais ambíguos.

* Durante a integração do trabalho desenvolvido pelos integrantes do grupo, um dos puzzles do banco de testes (`coracao`) foi definido duas vezes: uma versão 5x5 e outra 10x10. Como ambas utilizavam o mesmo identificador, a versão 10x10 sobrescrevia a 5x5 devido ao comportamento padrão do Python para variáveis globais. O problema foi corrigido renomeando uma das versões.

* O agente de busca local (Simulated Annealing), com os parâmetros inicialmente adotados, necessitava de aproximadamente 90 mil iterações para que a temperatura atingisse níveis baixos, tornando sua execução inviável para os benchmarks realizados. Foi necessário ajustar a temperatura inicial e a taxa de resfriamento para reduzir o número de iterações para aproximadamente 2 mil. Apesar dessa melhoria, a função de custo utilizada (quantidade de linhas e colunas inconsistentes com as pistas) varia pouco a cada modificação individual de célula, dificultando a convergência em puzzles maiores.

* Os puzzles gerados aleatoriamente pela interface tendem a apresentar níveis de ambiguidade superiores aos puzzles elaborados manualmente. Isso impacta principalmente os agentes CSP e probabilístico, que dependem fortemente da quantidade de informação inferível a partir das pistas disponíveis.

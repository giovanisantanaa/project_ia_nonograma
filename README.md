# Projeto IA - Nonogramas

Projeto da disciplina IMD3001 - Introducao a Inteligencia Artificial

Integrantes:

-

## Sobre

Implementacao de agentes de IA para resolver Nonogramas, usando os conceitos vistos em sala:
busca, CSP e raciocinio probabilistico.

## Como gerar puzzles
```
tamanhos(5,10,15,20,25). >= 15 é lento.
python src/puzzles2.py --tamanho 10 --quantidade 30 --csv puzzles.csv
```

## Como rodar

```
python main.py
```

## Como gerar gráficos

```
python src/graph_gen.py
```

## Executar os testes

```
python -m pytest tests/ -v
```

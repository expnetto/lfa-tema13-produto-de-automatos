# Tema 13: produto de autômatos

Linguagens Formais e Autômatos, trabalho prático (Prof. Dr. Leonardo Angelo, 2026.2).

**Integrante:** Eraldo Xavier P Netto

O programa monta dois AFDs sobre Σ = {0, 1} e constrói sozinho o AFD produto deles:

- **A**: número **par** de 0.
- **B**: número **ímpar** de 1.
- Produtos gerados automaticamente: **A ∩ B**, **A ∪ B** e **A − B**.

Cada palavra é lida símbolo por símbolo pelo autômato. Não há expressão regular nem função pronta de contagem na solução. Símbolo fora de {0, 1} vai para o **poço** (estado de erro), que aparece no código e nas tabelas.

## Como rodar

Só precisa do Python 3 (o código exige 3.7 ou mais novo; rodei no 3.13 e no 3.14). Não instala nada. Nos exemplos abaixo, use `python3` no macOS e no Linux e `python` no Windows.

```
python src/main.py
```

Mostra as tabelas de transição dos cinco autômatos (A, B e os três produtos) e fica lendo palavras, uma por linha. Palavra vazia é uma linha em branco (ou `ε`, ou `eps`). Para sair: `sair`, ou Ctrl+D (Linux/macOS), ou Ctrl+Z e Enter (Windows).

Outras formas de usar:

```
python src/main.py 001 0101 ε          # testa as palavras dadas
python src/main.py --sem-tabelas 001   # só o resultado
python src/main.py --so-tabelas        # só as tabelas
python src/main.py < palavras.txt      # lê de um arquivo, uma palavra por linha
```

Espaço conta como símbolo da palavra (e leva ao poço), então cuidado com espaço sobrando no fim de uma linha.

Para cada palavra o programa mostra se **A**, **B** e cada produto aceita ou rejeita, e o caminho de estados percorrido:

```
palavra: 001
  A      aceita   par0 → impar0 → par0 → par0
  B      aceita   par1 → par1 → par1 → impar1
  A ∩ B  aceita   q0 → q1 → q0 → q2
  A ∪ B  aceita   q0 → q1 → q0 → q2
  A − B  rejeita  q0 → q1 → q0 → q2
```

## Testes

```
python testes/rodar_testes.py
```

Roda tudo de uma vez e mostra, para cada palavra, o resultado esperado, o obtido e se bateu. Termina com código de saída 0 se tudo passou e 1 se algo falhou.

- `testes/obrigatorias.txt`: as 7 palavras obrigatórias do enunciado (A ∩ B).
- `testes/proprias.txt`: 10 aceitas e 10 rejeitadas para A ∩ B, com bordas (menor palavra aceita, um símbolo a mais, um a menos, símbolo fora do alfabeto no começo, no meio e no fim, palavra vazia), mais 11 palavras para A ∪ B e 11 para A − B.
- Verificação cruzada: compara os cinco autômatos com a definição das linguagens em todas as palavras de até 10 símbolos.
- `testes/test_unidades.py`: testes de unidade do AFD, do produto e do programa.

## Onde está cada coisa

```
src/
  afd.py        classe AFD (Q, Σ, δ, q0, F) com poço explícito, execução e tabela
  produto.py    construção do produto e os critérios de ∩, ∪ e −
  automatos.py  os AFDs A e B, escritos à mão, e a montagem dos três produtos
  main.py       programa de linha de comando
testes/         palavras de teste e o script que roda tudo
docs/
  relatorio.pdf relatório (modelagem, definição formal, diagrama, testes, ER equivalente)
  diagrama.png  diagrama dos autômatos
ferramentas/    scripts que refazem o diagrama e o PDF (precisam de matplotlib e reportlab)
```

Para desenhar um autômato basta olhar `src/automatos.py`: estados, alfabeto, a tabela `delta`, o estado inicial e os finais estão escritos ali. O produto (`src/produto.py`) é montado por busca em largura a partir do par de estados iniciais, e os estados novos saem como q0, q1, q2, q3. A única coisa que muda entre ∩, ∪ e − é o critério que decide quais pares são finais.

## Refazer o diagrama e o relatório (opcional)

Só é preciso se o código mudar. Usa as mesmas tabelas do programa, então o diagrama e o PDF não destoam do código.

```
pip install matplotlib reportlab
python ferramentas/diagrama.py
python ferramentas/relatorio.py
```

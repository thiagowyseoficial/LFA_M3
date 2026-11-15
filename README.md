# Trabalho M3 — Máquinas de Turing

Disciplina: Linguagens Formais e Autômatos — UNIVALI.

Integrantes: preencher com os nomes da equipe (máximo de três).

Os estados aparecem no JFLAP como `q0`, `q1`, `q2` etc., com numeração própria em cada máquina. O estado inicial é `q0`; os estados finais são indicados por círculo duplo.

Os quatro arquivos `.jff` contêm máquinas determinísticas de **uma fita**, com movimentos para a esquerda e para a direita; `S` significa permanecer na mesma célula. A fita se estende nos dois sentidos. O símbolo em branco é representado por um campo vazio no XML. Não digite espaços na entrada.

## Abrir e executar no JFLAP

1. Abra o JFLAP e selecione **File → Open** para abrir um arquivo `.jff`.
2. Use **Input → Step** para acompanhar a execução ou **Input → Fast Run** para executar diretamente.
3. Digite uma das entradas abaixo, sem espaços. Nos exercícios 2 e 4, os separadores `+` e `#` são aceitos. Isso contempla o texto e os exemplos do enunciado.
4. Para acompanhar o conteúdo final da fita nos exercícios 1 e 2, use a execução passo a passo. O resultado é o bloco binário que resta na fita; a posição final do cabeçote não faz parte do resultado.

Entradas inválidas param sem alcançar um estado final e são rejeitadas. Não é necessário um estado explícito de rejeição. Nos reconhecedores, a aceitação indica que a entrada pertence à linguagem; as marcas auxiliares podem permanecer na fita.

## 1. Multiplicar por dois

Arquivo: `01_multiplicar_por_dois.jff`.

Entrada: um ou mais bits. A máquina percorre o número até o primeiro branco, escreve `0` à direita e aceita. Acrescentar um zero à direita equivale a multiplicar o valor binário por dois.

| Entrada | Saída |
|---|---|
| `101` | `1010` |
| `111` | `1110` |
| `0` | `00` |
| `0011` | `00110` |

Zeros à esquerda são preservados. `00` representa corretamente o dobro de zero. A entrada vazia é rejeitada. Tempo linear no comprimento da entrada.

## 2. Somar dois números binários

Arquivo: `02_soma_binaria.jff`.

Entrada: `a+b` ou `a#b`, em que cada operando contém pelo menos um bit.

A máquina valida a entrada e normaliza o separador para `+`. Enquanto o segundo operando é diferente de zero, subtrai uma unidade dele e soma uma unidade ao primeiro:

1. Procura um `1` no segundo operando para verificar se ele é positivo.
2. Percorre esse operando até o fim e efetua o empréstimo binário: zeros finais viram `1`, e o primeiro `1` encontrado da direita para a esquerda vira `0`.
3. Volta ao primeiro operando e efetua o transporte binário: uns finais viram `0`, e o primeiro `0` ou branco vira `1`.
4. Quando o segundo operando chega a zero, apaga seus bits e o separador e aceita.

O invariante é que a soma dos dois valores permanece constante. O segundo valor diminui a cada ciclo, portanto a máquina termina. Ao final, o primeiro valor contém a soma original.

| Entrada | Saída |
|---|---|
| `101+11` | `1000` |
| `111#1` | `1000` |
| `0+0` | `0` |
| `00101+00011` | `01000` |

A saída pode preservar zeros à esquerda. A estratégia foi escolhida pela facilidade de explicar; executa um ciclo por unidade do segundo valor, por isso pode ser lenta para operandos grandes. Use números pequenos na apresentação.

## 3. Reconhecer L = {ww | w ∈ {a,b,c}*}

Arquivo: `03_reconhecer_ww.jff`.

A máquina primeiro valida que a entrada contém somente `a`, `b` e `c`. Depois divide a palavra em duas metades e as compara **na mesma ordem**.

Na divisão, marca a primeira letra ainda livre à esquerda usando `A`, `B` ou `C`, preservando seu valor. Em seguida, marca a última letra ainda livre à direita usando `X`, `Y` ou `Z`. Repete esse processo até as metades se encontrarem. Se faltar uma letra para formar um par, o comprimento é ímpar e a máquina rejeita.

| Letra original | Marca da metade esquerda | Marca da metade direita |
|---|---|---|
| `a` | `A` | `X` |
| `b` | `B` | `Y` |
| `c` | `C` | `Z` |

Na comparação, escolhe a primeira marca não processada da esquerda e busca a primeira marca não processada da direita. Exige os pares `A/X`, `B/Y` ou `C/Z`. As letras já comparadas viram `L` e `R`. Aceita quando todas as letras foram pareadas corretamente.

| Entrada | Resultado |
|---|---|
| vazia (ε) | Aceita |
| `aa` | Aceita |
| `abcabc` | Aceita |
| `acacaacaca` | Aceita |
| `abacbabacb` | Aceita |
| `aaabacbbca` | Rejeita |
| `bcbaabcb` | Rejeita |
| `abba` | Rejeita |
| `abc` | Rejeita |

A palavra vazia é aceita porque `w` pode ser vazia. Ter comprimento par é necessário, mas não suficiente: as duas metades precisam ser iguais. Tempo quadrático no comprimento da entrada.

## 4. Primeiro número maior que o segundo

Arquivo: `04_primeiro_maior_que_segundo.jff`.

Entrada: `a+b` ou `a#b`. Aceita exatamente quando o valor de `a` é estritamente maior que o de `b`; igualdade é rejeitada.

A máquina valida a entrada e marca os zeros à esquerda com `Z` no primeiro operando e `W` no segundo. Esses zeros não participam da comparação. Um operando formado apenas por zeros fica sem bits significativos.

Depois, pareia os bits significativos de cada número, da esquerda para a direita. As marcas `A/B` guardam os valores `0/1` do primeiro operando, e `X/Y` guardam os valores `0/1` do segundo. O estado lembra a primeira diferença observada:

- `E`: prefixos iguais;
- `G`: primeiro prefixo maior;
- `L`: primeiro prefixo menor.

Se um número tiver mais bits significativos, ele é maior, independentemente da diferença lembrada. Se os comprimentos forem iguais, a primeira diferença decide: somente `G` aceita.

| Entrada do enunciado | Resultado |
|---|---|
| `1010#101` | Aceita |
| `111#110` | Aceita |
| `101#101` | Rejeita |
| `10#0001` | Aceita |
| `0000100#110` | Rejeita |

`0#0` e `000#0` são rejeitadas; `1#000` é aceita. Tempo quadrático no comprimento da entrada.

## Verificação e reprodução

`gerar_e_testar.py` utiliza apenas a biblioteca padrão do Python. Ele gera os quatro arquivos e executa um simulador de máquina de Turing sobre as mesmas tabelas de transição.

No Windows, execute:

```powershell
py gerar_e_testar.py
```

A verificação inclui todos os números de 0 a 255 para o dobro; pares de 0 a 31 para a soma; pares de 0 a 31 para a comparação, com diferentes quantidades de zeros à esquerda e ambos os separadores; todas as palavras de comprimento até 8 sobre `{a,b,c}`; casos inválidos e exemplos. O XML gerado também é relido e conferido.

Os testes foram executados no simulador incluído. A interface gráfica do JFLAP não foi executada neste ambiente; a conferência visual e a apresentação devem ser feitas abrindo os `.jff` no JFLAP.

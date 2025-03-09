# Solitário Flet

Este projeto é uma implementação do clássico jogo de Paciência (Solitário) utilizando a biblioteca [Flet](https://flet.dev) para Python. O jogo permite que o usuário interaja com as cartas por meio de arrastar e soltar, execute jogadas automáticas (como mover cartas para as fundações com duplo clique), desfaça jogadas, e até salve/carregue o estado do jogo. Além disso, é possível personalizar a imagem da traseira das cartas. Muitas destas funcionalidades foram desenvolvidas com apoio de um tutorial oficial do Flet para implementar o jogo base.


## Funcionalidades

- **Distribuição de Cartas:**
  - Embaralhamento e distribuição das 52 cartas entre o tableau (pilhas de jogo) e o estoque.
- **Interação com Cartas:**
  - Arrastar e soltar cartas entre os slots (estoque, descarte, fundações e tableau).
  - Clique e duplo clique para virar cartas e mover automaticamente para as fundações, quando aplicável.
- **Desfazer Jogada:**
  - Permite reverter a última ação realizada.
- **Salvar e Carregar Jogo:**
  - Salva o estado atual do jogo no armazenamento do cliente e permite carregá-lo posteriormente.
- **Personalização da Traseira das Cartas:**
  - Escolha entre diferentes imagens (Padrão, Pokemon, YuGiOh, Uno) para a traseira das cartas.

## Requisitos

- **Python 3.10+** (recomenda-se utilizar a versão mais recente)
- **Flet:** Para instalar, execute:

```bash
pip install flet
```

## Estrutura do Projeto

- **solitaire.py:**  
  Responsável pela lógica do jogo, criação e distribuição das cartas, gerenciamento dos slots e controle do estado do jogo (salvar, carregar, desfazer jogadas e customização da traseira das cartas).

- **card.py:**  
  Define a classe `Card`, que representa uma carta do baralho, com métodos para virar, arrastar, soltar e interagir com o usuário.

- **slot.py:**  
  Define a classe `Slot`, que representa os locais (estoque, descarte, fundações e tableau) onde as cartas são organizadas.

- **/images:**  
  Pasta contendo as imagens utilizadas no jogo: imagens das faces das cartas e as imagens para as traseiras (ex.: `card_back.png`, `pokemon_back.jpg`, `yugioh_back.jpg`, `uno_back.jpg`).

## Como Executar

1. **Clone o repositório:**

```bash
git clone <URL-do-repositório>
cd <nome-do-repositório>
```

## Instale as dependências:
```bash
pip install flet
```
## Execute o projeto:
```bash
python solitaire.py
```
O jogo será iniciado e poderá ser jogado através da interface gráfica exibida.

## Uso e Customizações

**Interação com o Jogo:**  
Utilize o mouse ou toque (em dispositivos móveis) para arrastar e soltar as cartas. Clique simples e duplo clique nas cartas para virar e mover automaticamente para as fundações, conforme as regras do jogo.

**Desfazer Jogada:**  
O botão "Desfazer Jogada" reverte a última jogada realizada.

**Salvar e Carregar Jogo:**  
- **Salvar Jogo:** O botão "Salvar Jogo" serializa o estado atual (posição, face, slot e ordem das cartas) e o armazena no armazenamento do cliente.  
- **Carregar Jogo:** O botão "Carregar Jogo" restaura o estado salvo, permitindo que o jogo continue de onde parou.

**Personalizar Traseira das Cartas:**  
O menu "Escolher Traseira da carta" permite selecionar entre as opções disponíveis (Padrão, Pokemon, YuGiOh e Uno). Ao escolher uma opção, todas as cartas viradas para baixo atualizarão sua imagem para a nova traseira selecionada.

# Othello

Aplicação que simula partidas do jogo Otello para testar algoritimos de
inteligência artificial.

## Como instalar
```shell script
# Clone o repositório do projeto
git clone https://github.com/HeavenVolkoff/TabuleiroOthello.git
# Entre na raiz do projeto
cd TabuleiroOthello
# Instale o projeto
pip install --user .
```

## Como usar
A aplicação pode ser acessada através do executavel `othello` após sua instalação

```
usage: othello [-h] [--automatico] [--debug] [CAMINHO [CAMINHO ...]]

Simula partidas do jogo Otello

positional arguments:
  CAMINHO       Lista de caminhos para pastas ou arquivos contendo definições
                de jogadores em python

optional arguments:
  -h, --help    show this help message and exit
  --automatico  Passa para próxima jogada automaticamente
  --debug       Habilita mostrar a stacktrace de errors e outros dados
```

Exemplo de como adicionar novos jogadores:
```shell script
othello ./extra_players/minmax.py
```

É possivel adicionar quantos jogadores extras for desejado, so precisa passar os
caminhos das pastas e arquivos como argumento do executavel do simulador.

A escolha de qual jogador a ser usado é feita no inicio do programa de maneira
interativa

Exemplo:
```
$> othello --automatic ./extra_players
   _|_|      _|      _|                  _|  _|
 _|    _|  _|_|_|_|  _|_|_|      _|_|    _|  _|    _|_|
 _|    _|    _|      _|    _|  _|_|_|_|  _|  _|  _|    _|
 _|    _|    _|      _|    _|  _|        _|  _|  _|    _|
   _|_|        _|_|  _|    _|    _|_|_|  _|  _|    _|_|
Selecione um dos players abaixo para ser o jogador preto
0 - corner_player
1 - human_player
2 - random_player
3 - guloso
4 - minimax
Digite o numero do player que voce deseja: 4

Selecione um dos players abaixo para ser o jogador branco
0 - corner_player
1 - human_player
2 - random_player
3 - guloso
4 - minimax
Digite o numero do player que voce deseja: 3
```

## Como criar jogadores
[Vide documentação](docs/CRIAR_JOGADORES.md)

## Licensa

Public Domain

[![Build Status](https://travis-ci.org/matheussampaio/stack-overgol.svg?branch=develop)](https://travis-ci.org/matheussampaio/stack-overgol)

Stack Overgol Bot
=================

## Commands:

listar - Imprimi a lista de presença.
vou - Adiciona a lista de presença.
naovou - Remove da lista de presença.
vouagarrar - Adiciona a lista de goleiros.
convidado - <nome> <sobrenome <rating> - Adiciona a lista de presença.
convidado_agarrar - <nome> <sobrenome> - Adiciona a lista de goleiros.
abrir - [Admin] Abrir o check-in.
fechar - [Admin] Fechar check-in.
resetar - [Admin] Reseta a lista.
times - [<quantidade_times> <tamanho_time>] - [Admin] Tira os times.
naovai - <nome> <sobrenome> - [Admin] Tira alguém da lista de presença.
vai - <nome> <sobrenome> - [Admin] Coloca alguém da lista de presença.
vai_agarrar - <nome> <sobrenome> - [Admin] Coloca alguém da lista de goleiros.

## Requirements:
- python3
- pip
- virtualenv

## How to install:
```
$ virtualenv -p python3 venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

## How to configure:
```
$ cp example_configs.yml src/.configs.yml
```

## How to run:
```
$ python3 src/main.py
```

## How to run the tests:
```
$ nose2
```

## License
MIT

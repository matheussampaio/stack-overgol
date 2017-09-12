[![Build Status](https://travis-ci.org/matheussampaio/stack-overgol.svg?branch=develop)](https://travis-ci.org/matheussampaio/stack-overgol)

Stack Overgol Bot
=================

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

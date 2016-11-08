Stack Overgol Bot
=================

## Requirements:
- python3 and python3-dev
- pip
- virtualenv

## How to:
```
$ # clone project and cd to it
$ virtualenv -p python3 venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ cp src/default_configs.py src/configs.py
$ # edit `src/configs.py` with your configurations
$ python3 src/main.py
```

FROM python:3.7

WORKDIR /opt/app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . ./

CMD [ "python", "./src/main.py" ]

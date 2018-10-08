FROM python:3.7 as python-base
COPY requirements.txt .
RUN pip install --install-option="--prefix=/install" -r requirements.txt

FROM python:3.7-alpine
WORKDIR /opt/app
COPY --from=python-base /install /usr/local
COPY . ./

CMD [ "python", "./src/main.py" ]

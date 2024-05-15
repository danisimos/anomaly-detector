FROM python:3.9.7

WORKDIR /app

RUN wget "https://storage.yandexcloud.net/cloud-certs/CA.pem"

COPY ../pythonProject .
RUN pip install -r requirements.txt

EXPOSE 80

CMD python run.py
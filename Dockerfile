FROM python:3.6-alpine3.12

ADD . /app

WORKDIR /app

RUN pip3 install -r requirements.txt

CMD ["python3", "proxy.py"]

EXPOSE 8000

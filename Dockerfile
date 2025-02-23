FROM python:3.12-alpine3.20@sha256:4ce45e8acd11d49ee07aa736cd7ca2950df75033b946f3a5d9eca1cb4aae2ab7

WORKDIR /code

COPY /requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY / .

CMD ["python3", "main.py"]
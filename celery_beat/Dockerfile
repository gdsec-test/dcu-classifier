FROM python:3.7-slim

WORKDIR /app/

ADD ./*.py /app/
RUN pip install --compile celery[mongodb]

ENTRYPOINT celery -A run beat -l INFO
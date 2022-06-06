FROM docker-dcu-local.artifactory.secureserver.net/dcu-python3.7:3.3

USER root
RUN adduser --disabled-password --disabled-login --no-create-home --ingroup dcu --system dcu

WORKDIR /app/
RUN chown -R dcu:dcu /app

ADD ./*.py /app/
RUN pip install --compile celery[mongodb]

USER dcu
ENTRYPOINT celery -A run beat -l INFO
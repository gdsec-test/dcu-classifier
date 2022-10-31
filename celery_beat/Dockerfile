FROM docker-dcu-local.artifactory.secureserver.net/dcu-python3.7:3.3

USER root
WORKDIR /app/
RUN chown -R dcu:dcu /app

ADD ./*.py /app/
COPY requirements.txt /tmp/
RUN python -m pip install --upgrade pip pip==20.2.4
RUN pip install -r /tmp/requirements.txt
RUN pip install --compile celery[mongodb]

USER dcu
ENTRYPOINT celery -A run beat -l INFO
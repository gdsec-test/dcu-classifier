FROM python:3.7.10-slim as base
LABEL MAINTAINER="dcueng@godaddy.com"

RUN addgroup dcu && adduser --disabled-password --disabled-login --no-create-home --ingroup dcu --system dcu
RUN apt-get update && apt-get install -y gcc phantomjs

RUN pip install -U pip
COPY ./private_pips /tmp/private_pips
RUN pip install --compile /tmp/private_pips/dcdatabase

FROM base as deliverable

RUN mkdir -p /app
COPY ./run.py ./celeryconfig.py ./settings.py ./*.yaml ./health.sh /app/

# Compile the Flask API
COPY . /tmp
RUN pip install --compile /tmp

# cleanup
RUN apt-get remove -y gcc
RUN rm -rf /tmp

# Something to get PhantomJS to run without throwing errors
RUN mkdir -p /tmp/runtime-dcu
RUN chown -R dcu:dcu /tmp/runtime-dcu
RUN strip --remove-section=.note.ABI-tag /usr/lib/x86_64-linux-gnu/libQt5Core.so.5

# Fix permissions.
RUN chown -R dcu:dcu /app

USER dcu
WORKDIR /app
ENV QT_QPA_PLATFORM offscreen

CMD ["/usr/local/bin/celery", "-A", "run", "worker", "-l", "INFO", "--without-heartbeat", "--without-gossip", "--without-mingle"]
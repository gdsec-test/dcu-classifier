FROM docker-dcu-local.artifactory.secureserver.net/dcu-python3.7:3.3
LABEL MAINTAINER="dcueng@godaddy.com"

USER root
RUN adduser --disabled-password --disabled-login --no-create-home --ingroup dcu --system dcu
RUN apt-get update && apt-get install -y gcc bzip2 libfreetype6 libfontconfig1 wget -y

# We need to pull this specific phantomjs. We want to maintain consistency with GDBS.
RUN wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2
RUN tar xvjf phantomjs-2.1.1-linux-x86_64.tar.bz2 -C /usr/local/share/
RUN ln -s /usr/local/share/phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin/

RUN pip install -U pip

RUN mkdir -p /tmp/build
COPY requirements.txt /tmp/build/
COPY pip_config /tmp/build/pip_config
RUN PIP_CONFIG_FILE=/tmp/build/pip_config/pip.conf pip install -r /tmp/build/requirements.txt

COPY *.py /tmp/build/
COPY test_requirements.txt /tmp/build/
COPY README.md /tmp/build/
COPY celery_beat /tmp/build/celery_beat
COPY service /tmp/build/service
RUN PIP_CONFIG_FILE=/tmp/build/pip_config/pip.conf pip install --compile /tmp/build/

COPY ./run.py ./celeryconfig.py ./settings.py ./logging.yaml ./health.sh /app/

# cleanup
RUN apt-get remove -y gcc wget bzip2
RUN rm -rf /tmp

# Fix permissions.
RUN chown -R dcu:dcu /app

# Something to get PhantomJS to run without throwing errors
RUN mkdir -p /tmp/runtime-dcu
RUN chown -R dcu:dcu /tmp/runtime-dcu

WORKDIR /app
USER dcu
ENV QT_QPA_PLATFORM phantom
ENV OPENSSL_CONF /etc/ssl/

CMD ["/usr/local/bin/celery", "-A", "run", "worker", "-l", "INFO", "--without-heartbeat", "--without-gossip", "--without-mingle"]
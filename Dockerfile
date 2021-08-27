FROM python:3.7.10-slim
LABEL MAINTAINER="dcueng@godaddy.com"

RUN addgroup dcu && adduser --disabled-password --disabled-login --ingroup dcu --system dcu
RUN apt-get update && apt-get install -y --no-install-recommends gcc bzip2 libfreetype6 libfontconfig1 wget \
libgtk-3-dev libdbus-glib-1-2  libpci-dev libavcodec-extra libxt6

# firefox install
ARG FIREFOX_VERSION=91.0.2
RUN FIREFOX_DOWNLOAD_URL="https://download.mozilla.org/?product=firefox-$FIREFOX_VERSION&os=linux64" \
   && rm -rf /var/lib/apt/lists/* /var/cache/apt/* \
   && wget --no-verbose -O /tmp/firefox.tar.bz2 $FIREFOX_DOWNLOAD_URL \
   && rm -rf /opt/firefox \
   && tar -C /opt -xjf /tmp/firefox.tar.bz2 \
   && rm /tmp/firefox.tar.bz2 \
   && mv /opt/firefox /opt/firefox-$FIREFOX_VERSION \
   && ln -fs /opt/firefox-$FIREFOX_VERSION/firefox /usr/bin/firefox

# geckodriver install
RUN GK_VERSION=0.29.1 \
  && wget --no-verbose -O /tmp/geckodriver.tar.gz https://github.com/mozilla/geckodriver/releases/download/v$GK_VERSION/geckodriver-v$GK_VERSION-linux64.tar.gz \
  && rm -rf /opt/geckodriver \
  && tar -C /opt -zxf /tmp/geckodriver.tar.gz \
  && rm /tmp/geckodriver.tar.gz \
  && mv /opt/geckodriver /opt/geckodriver-$GK_VERSION \
  && chmod 755 /opt/geckodriver-$GK_VERSION \
  && ln -fs /opt/geckodriver-$GK_VERSION /usr/bin/geckodriver


COPY ./run.py ./celeryconfig.py ./settings.py ./logging.yaml ./health.sh /app/
COPY . /tmp

RUN pip install -U pip
RUN PIP_CONFIG_FILE=/tmp/pip_config/pip.conf pip install --compile /tmp

# cleanup
RUN apt-get remove -y gcc wget bzip2
RUN rm -rf /tmp/*

# Fix permissions.
RUN chown -R dcu:dcu /app
RUN chown -R dcu:dcu /tmp

WORKDIR /app
USER dcu
ENV OPENSSL_CONF /etc/ssl/

CMD ["/usr/local/bin/celery", "-A", "run", "worker", "-l", "INFO", "--without-heartbeat", "--without-gossip", "--without-mingle"]

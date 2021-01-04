# DCU-Classifier
#
#

FROM ubuntu:16.04
MAINTAINER DCU ENG <DCUEng@godaddy.com>

RUN groupadd -r dcu && useradd -r -m -g dcu dcu

# apt-get installs

RUN apt-get update && \
    apt-get install -y build-essential \
    fontconfig \
    gcc \
    libffi-dev \
    libssl-dev \
    python3-dev \
    python3-pip \
    curl \
    && ln -s /usr/bin/python3 python \
    && pip3 --no-cache-dir install --upgrade pip

RUN cd /usr/local/share && \
    curl -L https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2 | tar xj && \
    ln -s /usr/local/share/phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/bin/phantomjs

COPY ./run.py ./run.sh ./celeryconfig.py ./settings.py ./*.yaml ./health.sh /app/

COPY . /tmp

# pip install private pips staged by Makefile
RUN for entry in dcdatabase; \
    do \
    pip install --compile "/tmp/private_pips/$entry"; \
    done

RUN pip install --compile /tmp

# cleanup
RUN apt-get remove --purge -y build-essential \
    curl \
    gcc \
    libffi-dev \
    libssl-dev \
    python-dev && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /tmp && \
    chown -R dcu:dcu /app

WORKDIR /app

ENTRYPOINT ["/app/run.sh"]

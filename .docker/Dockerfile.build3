FROM alpine:3.8

MAINTAINER Aleksey Shirokih <shirokih@nocproject.org>

WORKDIR /opt/noc
ENV\
    DJANGO_SETTINGS_MODULE=noc.settings \
    PYTHONPATH=/opt/noc:/opt:/usr/bin/python3.6 \
    NOC_THREAD_STACK_SIZE=524288 \
    NOC_PYTHON_INTERPRETER=/usr/bin/python3

COPY requirements/docker3.txt /opt/noc/requirements/docker3.txt
COPY requirements/test.txt /opt/noc/requirements/test.txt

RUN apk add --update --no-cache \
    ca-certificates \
    libpq libssh2 \
    py3-cffi \
    py3-numpy \
    py3-pip \
    snappy \
    tzdata \
    curl
RUN apk add --no-cache --virtual .build-deps \
    cyrus-sasl-dev \
    gcc \
    libffi-dev \
    libmemcached-dev \
    libressl-dev \
    musl-dev \
    postgresql-dev \
    python3-dev \
    zlib-dev
RUN pip3 install --no-cache --upgrade -r /opt/noc/requirements/docker3.txt \
    && pip3 install --no-cache --upgrade -r /opt/noc/requirements/test.txt

RUN pip3 install cython

COPY . /opt/noc
RUN /usr/bin/cythonize -i speedup/*.pyx

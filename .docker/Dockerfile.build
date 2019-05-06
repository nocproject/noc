FROM alpine:3.8

MAINTAINER Aleksey Shirokih <shirokih@nocproject.org>

WORKDIR /opt/noc
ENV\
    DJANGO_SETTINGS_MODULE=noc.settings \
    PYTHONPATH=/opt/noc:/opt:/usr/bin/python2.7 \
    NOC_THREAD_STACK_SIZE=524288 \
    NOC_PYTHON_INTERPRETER=/usr/bin/python

COPY requirements/docker.txt /opt/noc/requirements/docker.txt
COPY requirements/test.txt /opt/noc/requirements/test.txt

RUN apk add --update --no-cache \
    ca-certificates \
    libpq libssh2 \
    py-cffi \
    py-numpy \
    py-pip \
    snappy \
    tzdata \
    curl \
   && apk add --no-cache --virtual .build-deps \
        cyrus-sasl-dev \
        cython \
        cython-dev \
        gcc \
        libffi-dev \
        libmemcached-dev \
        libressl-dev \
        libssh2-dev \
        musl-dev \
        postgresql-dev \
        python-dev \
        zlib-dev
RUN pip install --no-cache --trusted-host cdn.getnoc.com --find-links https://cdn.getnoc.com/npkg/ --upgrade -r /opt/noc/requirements/docker.txt \
    && pip install --no-cache --trusted-host cdn.getnoc.com --find-links https://cdn.getnoc.com/npkg/ --upgrade -r /opt/noc/requirements/test.txt

COPY . /opt/noc
RUN find /opt/noc/ -type f -name "*.py" -print0 | xargs -0 python -m py_compile \
    && /usr/bin/cythonize -i speedup/*.pyx

# Base layer containing system packages and requirements
FROM alpine:3.12 AS base
ENV\
    DJANGO_SETTINGS_MODULE=noc.settings \
    NOC_THREAD_STACK_SIZE=524288 \
    NOC_PYTHON_INTERPRETER=/usr/bin/python3 \
    PYTHONPATH=/opt/noc:/opt:/usr/bin/python3.8 \
    PROJ_DIR=/usr
ADD thin.tgz /
RUN\
    apk add --no-cache \
        python3 \
        libffi \
        libpq \
        snappy \
        cyrus-sasl \
        ca-certificates \
        tzdata \
        git \
        zlib \
        proj \
    && apk add --virtual .build-dependencies --no-cache \
        build-base \
        python3-dev \
        libffi-dev \
        postgresql-dev \
        snappy-dev \
        zlib-dev \
        autoconf \
        automake \
        libtool \
        m4 \
        cyrus-sasl-dev \
        cmake \
        proj-util \
        proj-dev \
    && chmod a+x /usr/bin/get-noc-requirements \
    && /usr/bin/python3 -m ensurepip --upgrade \
    && /usr/bin/pip3 install --upgrade pip wheel \
    && (/usr/bin/get-noc-requirements activator dev test cython | /usr/bin/pip3 install -r /dev/stdin )\
    && /usr/bin/cythonize -i /opt/noc/speedup/*.pyx \
    && /usr/bin/pip3 uninstall -y Cython \
    && rm /requirements.txt \
    && apk del .build-dependencies \
    && rm -rf /var/cache/apk/* /root/.cache/

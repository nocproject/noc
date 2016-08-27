#!/bin/sh

currrent_dir=$(pwd)

compile_login () {
    if [ ! -f ../ui/login/index.html ]; then
        cd ../ui/src/login
        echo "Compiling login ..."
        docker-compose up
        cd ${currrent_dir}
    fi
}
start_dbs() {
    docker-compose up -d mongo \
                         postgres \
                         nsqd \
                         nsqlookupd \
                         clickhouse
    echo "Seeping a while to db start"
    sleep 6
}

start_sae() {
    docker-compose up -d sae \
                         discovery \
                         activator.default \
                         scheduler \
                         omap \
                         ping.default \
                         syslogcollector.default \
                         trapcollector.default
}

start_web() {
    docker-compose up -d web card login grafana front
}

start_pm() {
    docker-compose up -d influxdb pmwriter
}

start_fm() {
    docker-compose up -d classifier \
                         correlator \
                         mailsender
}
compile_login
start_dbs
start_sae
start_web
start_pm
start_fm
#!/bin/sh

currrent_dir=$(pwd)

pull_images () {
    echo "Pulling noc images..."
    docker-compose pull dev
    docker-compose pull sae
}

start_dbs() {
    echo "starting dbs..."
    docker-compose up -d mongo \
                         postgres \
                         nsqd \
                         nsqlookupd \
                         clickhouse
}
cytonize() {
    echo "Cythonizing..."
    docker-compose run --rm --entrypoint "/usr/bin/cythonize -i speedup/*.pyx" dev
}
migrate() {
    echo "Loading data to db's..."
    docker-compose run --rm --entrypoint /opt/noc/bundle/scripts/migrate.sh dev
}

install_npkg() {
    echo "Installing depends card..."
    docker-compose run --rm --entrypoint "./scripts/deploy/install-packages requirements/card.json" dev
    echo "Installing depends login..."
    docker-compose run --rm --entrypoint "./scripts/deploy/install-packages requirements/login.json" dev
    echo "Installing depends mib..."
    docker-compose run --rm --entrypoint "./scripts/deploy/install-packages requirements/mib.json" dev
    echo "Installing depends web..."
    docker-compose run --rm --entrypoint "./scripts/deploy/install-packages requirements/web.json" dev
}

start_sae() {
    echo "Starting SAE..."
    docker-compose up -d sae \
                         discovery \
                         activator-default \
                         scheduler \
                         omap \
                         ping-default \
                         syslogcollector-default \
                         trapcollector-default
}

start_web() {
    echo "Starting WEB..."
    docker-compose up -d web card login grafana grafanads front bi mrt
}

start_pm() {
    echo "Starting PM..."
    docker-compose up -d influxdb pmwriter
}

start_fm() {
    echo "Starting FM..."
    docker-compose up -d classifier \
                         correlator \
                         mailsender
}


start_dbs
pull_images
install_npkg
cytonize
migrate
start_sae
start_web
start_pm
start_fm

#!/bin/sh

currrent_dir=$(pwd)
dckrc="/usr/local/bin/docker-compose -f docker-compose-dbs.yml \
                -f docker-compose-discovery.yml \
                -f docker-compose-fm.yml \
                -f docker-compose-infra.yml \
                -f docker-compose-ping.yml \
                -f docker-compose-sae.yml \
                -f docker-compose-web.yml \
                -f docker-compose-pm.yml \
                -f docker-compose.yml"

start_registrator () {
    echo "Starting registrator..."
    ${dckrc} up -d registrator
}

pull_images () {
    echo "Pulling noc images..."
    ${dckrc} pull dev
    ${dckrc} pull sae
}

start_dbs() {
    echo "starting dbs..."
    ${dckrc} up -d mongo \
                         postgres \
                         nsqd \
                         nsqlookupd \
                         clickhouse
}
cytonize() {
    echo "Cythonizing..."
    ${dckrc} run --rm --entrypoint "/usr/bin/cythonize -i speedup/*.pyx" dev
}
migrate() {
    echo "Loading data to db's..."
    ${dckrc} run --rm --entrypoint /opt/noc/bundle/scripts/migrate.sh dev
}

install_npkg() {
    echo "Installing depends card..."
    ${dckrc} run --rm --entrypoint "./scripts/deploy/install-packages requirements/card.json" dev
    echo "Installing depends mib..."
    ${dckrc} run --rm --entrypoint "./scripts/deploy/install-packages requirements/mib.json" dev
    echo "Installing depends web..."
    ${dckrc} run --rm --entrypoint "./scripts/deploy/install-packages requirements/web.json" dev
}

start_sae() {
    echo "Starting SAE..."
    ${dckrc} up -d sae \
                         discovery-default \
                         activator-default \
                         scheduler \
                         omap \
                         ping-default \
                         syslogcollector-default \
                         trapcollector-default
}

start_web() {
    echo "Starting WEB..."
    ${dckrc} up -d web card login grafana grafanads front bi mrt
}

start_pm() {
    echo "Starting PM..."
    ${dckrc} up -d influxdb pmwriter
}

start_fm() {
    echo "Starting FM..."
    ${dckrc} up -d classifier \
                         correlator-default \
                         mailsender
}


start_registrator
start_dbs
pull_images
install_npkg
cytonize
migrate
start_sae
start_web
start_pm
start_fm

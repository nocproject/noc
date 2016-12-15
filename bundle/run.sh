#!/bin/sh

MODE=$1

if [ -z ${MODE} ] ; then
    echo "set mode local or distribute"
    exit 1
fi

currrent_dir=$(pwd)
dckrc="/usr/local/bin/docker-compose \
                -f ${MODE}/docker-compose-dbs.yml \
                -f ${MODE}/docker-compose-discovery.yml \
                -f ${MODE}/docker-compose-fm.yml \
                -f ${MODE}/docker-compose-infra.yml \
                -f ${MODE}/docker-compose-ping.yml \
                -f ${MODE}/docker-compose-sae.yml \
                -f ${MODE}/docker-compose-web.yml \
                -f ${MODE}/docker-compose-pm.yml \
                -f ${MODE}/docker-compose.yml"

start_registrator () {
    echo "Starting registrator..."
    /usr/local/bin/docker-compose -f ${MODE}/docker-compose-reg.yml up -d registrator
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
    ${dckrc} up -d web card login grafanads bi mrt
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

#!/bin/sh

MODE=$1

if [ -z ${MODE} ] ; then
    echo "set mode local or distribute"
    exit 1
fi

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

${dckrc} stop # just stop
${dckrc} rm -vf # remove containers
echo "Removing dbs"
sudo rm -r ../../noc_data/mongo ../../noc_data/postgres   #drop dbs
echo "Removing so files"
sudo rm ../speedup/*.so # drop cython

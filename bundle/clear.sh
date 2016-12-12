#!/bin/sh

dckrc="/usr/local/bin/docker-compose -f docker-compose-dbs.yml \
                -f docker-compose-discovery.yml \
                -f docker-compose-fm.yml \
                -f docker-compose-infra.yml \
                -f docker-compose-ping.yml \
                -f docker-compose-sae.yml \
                -f docker-compose-web.yml \
                -f docker-compose-pm.yml \
                -f docker-compose.yml"
${dckrc} stop # just stop
${dckrc} rm -vf # remove containers
echo "Removing dbs"
sudo rm -r ../../noc_data/mongo ../../noc_data/postgres   #drop dbs
echo "Removing so files"
sudo rm ../speedup/*.so # drop cython

#!/usr/bin/env bash

TMPPATH=$(mktemp -d)
TMPPATH1=$(mktemp -d)
#TMPPATH2=$(mktemp -d)

CHECKWAN() {
  echo "Checking internet connection"
  echo "----"
  touch "$INSTALLPATH"/docker/.env.proxy
  if ! ping -c 1 -q google.com > /dev/null 2>&1
    then
      echo "Internet connection not found"
      echo "Checking proxy ..."
      PROXYFORWAN="$HTTPS_PROXY"
      if [ -z "$PROXYFORWAN" ]
        then
          echo "You need setup 'HTTPS_PROXY' parameter"
          echo "Example: export HTTPS_PROXY=http://<ip>:<port>"
          echo "Break!!!"
          exit
        else
          echo "Detected proxy:" "$PROXYFORWAN"
          echo "Create .env.proxy file"
          echo "----"
          {
            echo "https_proxy=$PROXYFORWAN"
          } > "$INSTALLPATH"/docker/.env.proxy
      fi
  fi
}

CREATEDIR() {
  echo "Creating directories"
  echo "----"
  mkdir -p -v "$INSTALLPATH"/docker/var/backup-data
  mkdir -p -v "$INSTALLPATH"/docker/var/backup-images
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-alertmanager/etc
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-clickhouse/data
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-consul
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-grafana/db
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-grafana/plugins
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-kafka/data
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-mongo
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-mongorestore
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-nginx/ssl
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-noc/beef
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-noc/code
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-noc/custom
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-noc/etc
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-noc/etlimport
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-noc/biimport
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-postgres
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-postgresrestore
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-promgrafana/db
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-promgrafana/etc/dashboards
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-promgrafana/etc/provisioning/dashboards
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-promgrafana/etc/provisioning/datasources
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-promgrafana/etc/provisioning/notifiers
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-promgrafana/plugins
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-vmagent/etc
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-vmagent/data
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-vmalert/etc
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-vmalert/etc/rules.d
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-vmalert/etc/rules.custom.d
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-vmmetrics
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-sentry/pg
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-sentry/redis
  mkdir -p -v "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-redis
}

SETPERMISSION() {
  chown 101   -R "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-clickhouse/data
  chown 1001  -R "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-kafka
  chown 472   -R "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-grafana
  chown 472   -R "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-promgrafana
  chown 70    -R "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-sentry/pg
  chown 999   -R "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-mongo
  chown 999   -R "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-postgres
  chown 999   -R "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-sentry/redis
}

SETUPALERTMANAGER() {
    echo "Copy bulk alertmanager.conf to " "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-alertmanager/etc
    echo "---"
    if [ ! -f "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-alertmanager/etc/alertmanager.conf ]
      then
          cp ./etc/alertmanager/alertmanager.conf.bulk "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-alertmanager/etc/alertmanager.conf
    fi
}

SETUPPROMGRAFANA() {
  echo "GRAFANA dashboards download from code.getnoc.com/noc/grafana-selfmon-dashboards"
  echo "---"
  cd "$TMPPATH" && git clone -q https://code.getnoc.com/noc/grafana-selfmon-dashboards.git .
  cp -f -r "$TMPPATH"/dashboards/* "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-promgrafana/etc/dashboards
  cp -f -r "$TMPPATH"/provisioning/* "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-promgrafana/etc/provisioning
  if [ ! -f "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-promgrafana/etc/grafana.ini ]
    then
      cp -rf "$INSTALLPATH"/docker/etc/promgrafana/etc/grafana.ini "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-promgrafana/etc/
  fi
}

SETUPPROMRULES() {
  echo "PROMETHEUS alert rules download from code.getnoc.com/noc/noc-prometheus-alerts.git"
  echo "---"
  cd "$TMPPATH1" && git clone -q https://code.getnoc.com/noc/noc-prometheus-alerts.git .
  cp -f "$TMPPATH1"/*.yml "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-vmalert/etc/rules.d
  if [ ! -f "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-vmagent/etc/prometheus.yml ]
    then
      cp -rf "$INSTALLPATH"/docker/etc/vmagent/etc/prometheus.yml "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-vmagent/etc/
  fi
}

SETUPSENTRY() {
  if [ ! -f "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-sentry/sentry.env ]
    then
# @TODO
      GENERATE_PASSWORD="$(dd if=/dev/urandom bs=1 count=32 2>/dev/null | base64 -w 0 | rev | cut -b 2- | rev)"

      echo "Sentry env write in $INSTALLPATH/docker/var/$COMPOSEPREFIX-sentry/sentry.env"
      echo "after first start container need run command to make migration by setting up admin user passwd"
      echo "cd $INSTALLPATH/docker && docker-compose -f docker-compose-infra.yml exec sentry sentry upgrade"
      echo "---"
      { echo SENTRY_POSTGRES_HOST=sentry-postgres
        echo SENTRY_DB_NAME=sentry
        echo SENTRY_DB_USER=sentry
        echo SENTRY_DB_PASSWORD="$GENERATE_PASSWORD"
        echo SENTRY_SECRET_KEY="$(dd 'if=/dev/random' 'bs=1' 'count=32' 2>/dev/null | base64)"
        echo SENTRY_REDIS_HOST=sentry-redis
        echo SENTRY_METRICS_SAMPLE_RATE=0.9
        echo POSTGRES_USER=sentry
        echo POSTGRES_DBNAME=sentry
        echo POSTGRES_PASSWORD="$GENERATE_PASSWORD"
        echo "#Important!!! POSTGRES_PASSWORD == SENTRY_DB_PASSWORD"
      } >> "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-sentry/sentry.env
  fi
}


# @TODO
# need check $INSTALLPATH == $COMPOSEPATH and make warning if not
SETUPENV() {
  GENERATED_PG_PASSWORD="$(dd if=/dev/urandom bs=1 count=12 2>/dev/null | base64 -w 0 | rev | cut -b 2- | rev)"
  # TODO
  # need fix created mongo container with NOC_MONGO_PASSWORD instean "noc"
  # GENERATED_MONGO_PASSWORD="$(dd if=/dev/urandom bs=1 count=12 2>/dev/null | base64 -w 0 | rev | cut -b 2- | rev)"
  GENERATED_MONGO_PASSWORD=noc

  if [ ! -f "$INSTALLPATH"/docker/.env ]
      then
          echo "Writed COMPOSEPATH=$INSTALLPATH/docker in $INSTALLPATH/docker/.env"
          echo "You can change the parameters NOC_PG_PASSWORD\NOC_MONGO_PASSWORD if you want"
          echo "---"
          { echo "COMPOSEPATH=$INSTALLPATH/docker"
            echo "COMPOSEPREFIX=$COMPOSEPREFIX"
            echo "CONSUL_VERSION_TAG=1.8.6"
            echo "CLICKHOUSE_VERSION_TAG=22.4.5.9"
            echo "COMPOSE_HTTP_TIMEOUT=300"
            echo "# logging driver: json-file, local, journald"
            echo "COMPOSE_LOG_DRIVER=json-file"
            echo "COMPOSE_LOG_MAX_SIZE=10m"
            echo "COMPOSE_LOG_MAX_FILE=1"
            echo "GRAFANA_VERSION_TAG=9.5.1"
            echo "KAFKA_VERSION_TAG=3.6.2"
            echo "### NOC env ###"
            echo "NOC_VERSION_TAG=$PARAM_TAG"
            echo "# NOC_CODE_PATH '/home' for PROD or '/opt/noc' for DEV"
            echo "NOC_CODE_PATH=$NOC_CODE_PATH"
            echo "# Important!!! NOC_PG_PASSWORD must by similar in .data/noc/etc/noc.conf file"
            echo "NOC_PG_PASSWORD=$GENERATED_PG_PASSWORD"
            echo "PGPASSWORD=$GENERATED_PG_PASSWORD"
            echo "PG_VERSION_TAG=14-bullseye"
            echo "# Important!!! NOC_MONGO_PASSWORD must by similar in .data/noc/etc/noc.conf file"
            echo "NOC_MONGO_PASSWORD=$GENERATED_MONGO_PASSWORD"
            echo "# See https://jira.mongodb.org/browse/SERVER-48516 for mongo 4.2+"
            echo "MONGO_VERSION_TAG=4.2"
            echo "VICTORIAMETRICS_VERSION_TAG=1.44.0"
          } >> "$INSTALLPATH"/docker/.env
  fi

  # make noc.conf
  if [ ! -f "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-noc/etc/noc.conf ]
    then
        echo "Write $INSTALLPATH/docker/var/$COMPOSEPREFIX-noc/etc/noc.conf"
        echo "You can change the parameters NOC_PG_PASSWORD\NOC_MONGO_PASSWORD if you want"
        echo "---"
        { echo "NOC_CONFIG=env:///NOC"
          echo "NOC_MONGO_ADDRESSES=mongo:27017"
          echo "NOC_PG_ADDRESSES=postgres:5432"
          echo "NOC_BI_LANGUAGE=en"
          echo "NOC_CARD_LANGUAGE=en"
          echo "# Cache method: mongo(noc.core.cache.mongo.MongoCache) or Redis(noc.core.cache.redis.RedisCache)"
          echo "NOC_CACHE_CACHE_CLASS=noc.core.cache.redis.RedisCache"
          echo "NOC_CLICKHOUSE_RW_ADDRESSES=clickhouse:8123"
          echo "NOC_CLICKHOUSE_RO_ADDRESSES=clickhouse:8123"
          echo "NOC_FEATURES_CONSUL_HEALTHCHECKS=true"
          echo "NOC_FEATURES_SERVICE_REGISTRATION=true"
          echo "NOC_INSTALLATION_NAME=NOC-DC"
          echo "NOC_PATH_CUSTOM_PATH=/opt/noc_custom"
          echo "NOC_PATH_ETL_IMPORT=/var/lib/noc/import"
          echo "NOC_PG_DB=noc"
          echo "# Important!!! NOC_PG_PASSWORD must by similar in .env file"
          echo "NOC_PG_PASSWORD=$GENERATED_PG_PASSWORD"
          echo "NOC_PG_USER=noc"
          echo "NOC_POOL=default"
          echo "# en/ru only"
          echo "NOC_LANGUAGE=en"
          echo "NOC_LANGUAGE_CODE=en"
          echo "NOC_LOGIN_LANGUAGE=en"
          echo "NOC_LOGLEVEL=info"
          echo "NOC_REDPANDA_ADDRESSES=kafka:9092"
          echo "NOC_MONGO_USER=noc"
          echo "# Important!!! NOC_MONGO_PASSWORD must by similar in .env file"
          echo "NOC_MONGO_PASSWORD=$GENERATED_MONGO_PASSWORD"
          echo "NOC_REDIS_ADDRESSES=redis:6379"
          echo "NOC_SELFMON_ENABLE_FM=true"
          echo "NOC_SELFMON_ENABLE_INVENTORY=true"
          echo "NOC_SELFMON_ENABLE_TASK=true"
          echo "NOC_WEB_LANGUAGE=en"
          echo "NOC_FEATURES_SENTRY=false"
          echo "# setup Sentry DSN (Deprecated) http://<ip<:9000/settings/sentry/projects/<NAMEPROJECT>/keys/"
          echo "# NOC_SENTRY_URL=http://6ab3d0b0702d44d0acee73298a5bb40f:43d1cb7adc1946488ac9bba1d5e0dc58@sentry:9000/2"
          echo "TZ=Europe/Moscow"
          echo "LC_LANG=en_US.UTF-8"
        } >> "$INSTALLPATH"/docker/var/"$COMPOSEPREFIX"-noc/etc/noc.conf
  fi

  # make .env.infra
  if [ ! -f "$INSTALLPATH"/docker/.env.infra ]
    then
        echo "Write $INSTALLPATH/docker/.env.infra"
        echo "You can change the parameters for infra monitoring if you want"
        echo "---"
        { echo "### vm metrics ###"
          echo "vm_retentionPeriod=3"
          echo "### vmagent ###"
          echo "vmagent_loggerLevel=INFO"
          echo "vmagent_promscrape_suppressScrapeErrors=False"
          echo "vmagent_promscrape_consulSDCheckInterval=10s"
          echo "### vmalert ###"
          echo "vmalert_loggerLevel=INFO"
          echo "vmalert_rule_validateTemplates=True"
          echo "vmalert_rule=/rules/rules.custom.d/*.rules.yml,/rules/rules.d/*.rules.yml"
        } >> "$INSTALLPATH"/docker/.env.infra
  fi
}

CLEANVOLUMES() {
    echo "clean volumes"

}

while [ -n "$1" ]
do
    case "$1" in
        -t) PARAM_TAG="$2"
            #echo "Found the -t option, with parameter value $PARAM_TAG"
            shift ;;
        -p) PARAM_P="$2"
            #echo "Found the -p option, with parameter value $PARAM_P"
            shift ;;
        -d) INSTALLPATH="$2"
            #echo "Found the -d option, with parameter value $INSTALLPATH"
            shift ;;
        -c) NOC_CODE_PATH="$2"
            shift ;;
        -e) COMPOSEPREFIX="$2"
            shift ;;
        -h) echo "  -d    Dir where download NOC. default is '/opt/noc'"
            echo "  -p    'all' setup and configure all components"
            echo "        'env' write .env and .env.proxy file, creaete dir and some other setups"
            echo "        'perm' create dir and set permission "
            echo "        'grafana' setup grafana dashboards for infrastructure monitoring from https://code.getnoc.com/noc/grafana-selfmon-dashboards.git"
            echo "        'promrules' setup PROMETHEUS rules for alerting from https://code.getnoc.com/noc/noc-prometheus-alerts.git"
            echo "        'sentry' setup Sentry"
            echo "  -t    'tag' for docker images from https://code.getnoc.com/noc/noc/container_registry"
            echo "  -e    'COMPOSEPREFIX' for environment variables. Default is 'nocdc'"
            echo "                 Start 'noc-dc' with new COMPOSEPREFIX: 'docker-compose -p <COMPOSEPREFIX> up -d'"
            echo "Example: ./noc-docker-setup.sh -p all -d /opt/noc -t stable"
            break
            shift ;;
        --) shift
            break ;;
        *) echo "Example: ./noc-docker-setup.sh -p all -d /opt/noc -t stable -e nocdc";;
    esac
    shift
done

if [ -z "$COMPOSEPREFIX" ]
    then
        COMPOSEPREFIX="docker"
        echo "COMPOSEPREFIX is: $COMPOSEPREFIX"
        echo "---"
fi

if [ -z "$INSTALLPATH" ]
    then
        INSTALLPATH=/opt/noc
        echo "NOC-DC installing in: $INSTALLPATH/docker"
        echo "---"
fi

if [ -z "$PARAM_TAG" ]
    then
        PARAM_TAG="stable"
        echo "Docker use image with tag: $PARAM_TAG"
        echo "See all tags in https://code.getnoc.com/noc/noc/container_registry"
        echo "---"
fi

# Generate DEV or PROD env
if [ "$NOC_CODE_PATH" = "dev" ]
    then
        #NOC_CODE_PATH=/opt/noc
        # checkout NOC code to ./data/noc/code
        #echo "NOC code downloading from code.getnoc.com/noc/noc.git"
        #echo "Please read Readme.develop.md!!!"
        echo "Work in progress"
        echo "---"
        #cd "$TMPPATH2" && git clone -q https://code.getnoc.com/noc/noc.git .
        #cp -rf "$TMPPATH2"/. "$INSTALLPATH"/data/noc/code
    else
        NOC_CODE_PATH=/home
fi

if [ -n "$PARAM_P" ]
    then
        if [ "$PARAM_P" = "all" ]
            then
                CREATEDIR
                SETUPENV
                CHECKWAN
                SETUPALERTMANAGER
                SETUPPROMGRAFANA
                SETUPPROMRULES
                SETUPSENTRY
                SETPERMISSION
        elif [ "$PARAM_P" = "perm" ]
            then
                CREATEDIR
                SETPERMISSION
        elif [ "$PARAM_P" = "grafana" ]
            then
                CREATEDIR
                CHECKWAN
                SETUPPROMGRAFANA
        elif [ "$PARAM_P" = "promrules" ]
            then
                CREATEDIR
                SETUPPROMRULES
        elif [ "$PARAM_P" = "sentry" ]
            then
                SETUPSENTRY
        elif [ "$PARAM_P" = "env" ]
            then
                CREATEDIR
                CHECKWAN
                SETUPENV
                SETPERMISSION
        else
            echo "Unknown parameter for -p"
            echo "For help use: ./noc-docker-setup.sh -h"
        fi
else
    echo "No -p parameters found."
    echo "For help use: ./noc-docker-setup.sh -h"
    exit
fi

echo "Configuring NOC-DC finished."

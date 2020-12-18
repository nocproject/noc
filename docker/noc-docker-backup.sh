#!/usr/bin/env bash

# Script backup persistent ./var  and docker images for noc
# Stop NOC before start backup.
# Use: docker-compose -f docker-compose.yml down
#      docker-compose -f docker-compose-infra.yml down
# IMPORTANT!!! Saved ALL VERSIONS images needed for NOC

BACKUPDATA() {
    # backup ./data
    FILES="$BACKUPPATH/docker-compose.yml	$BACKUPPATH/../docker-compose-infra.yml"
    for file in ${FILES};
    do
        if docker-compose -f "$file" --project-directory=.. ps | grep Up ;
        then
    	    echo "---"
    	    echo "You need stop NOC-DC and/or NOC-DC-INFRA container"
    	    echo "docker-compose -f ""$file"" stop"
            exit
        fi
    done
    echo "Backup rersistent to: ""$BACKUPPATH"/var/backup-data/data-"$(date +%Y%m%d-%H-%M)".tar.gz
    echo "---"
    tar --exclude ./var/backup-data --exclude ./var/backup-images --exclude ./etc --exclude ./*.yml --exclude ./*.sh -cvpzf  "$BACKUPPATH"/var/backup-data/data-"$(date +%Y%m%d-%H-%M)".tar.gz --one-file-system -C "$BACKUPPATH"/ ./
}

BACKUPIMAGES() {
    FILES="$BACKUPPATH/docker-compose.yml	$BACKUPPATH/docker-compose-infra.yml"
    echo "Backup docker images to: ""$BACKUPPATH"
    echo "---"
    for file in ${FILES};
    do
        IMAGES=$(grep image "$file" | grep -v 'NOC_VERSION_TAG' | awk -e '{print $2}' | sort | uniq  )
        for image in ${IMAGES};
            do
                # remove ':${......_VERSION_TAG}' substring in name backup file
                NAMEIMAGE=$( echo "$image" | sed 's/[:\/]/_/g' | sed 's/${.*_VERSION_TAG}//g' )
                # remove ':${......_VERSION_TAG}' substring for non NOC images
                image=$( echo "$image" | sed 's/\:${.*_VERSION_TAG}//g' )
                docker save "$image" | gzip > "$BACKUPPATH""/var/backup-images/image-""$NAMEIMAGE"".tar.gz"
            done
    done
    # backup all NOC images
    # todo get $COMPOSETAG from .env file or save all NOC images
    IMAGESNOC=$(docker image ls --format '{{.Repository}}-{{.Tag}}' | grep 'registry.getnoc.com/noc/noc/')
    for imagesnoc in ${IMAGESNOC}
        do
            NAMEIMAGE=$( echo "$imagesnoc" | sed 's/[:\/]/_/g' )
            docker save "$image" | gzip > "$BACKUPPATH""/var/backup-images/image-""$NAMEIMAGE"".tar.gz"
        done
}

while [ -n "$1" ]
do
    case "$1" in
        -p) PARAM_P="$2"
            #echo "Found the -p option, with parameter value $PARAM_P"
            shift ;;
        -d) BACKUPPATH="$2"
            #echo "Found the -d option, with parameter value $BACKUPPATH"
            shift ;;
        -h) echo "  -p  'all' backup docker images and persistent data in ./var/"
            echo "      'data' backup persistent data in ./var/"
            echo "      'images' backup docker images (ALL versions) needed NOC"
            echo "  -d  path to 'docker-compose.yml' file. Default '/opt/noc/docker'"
            echo "Example: ./noc-docker-backup.sh -p all -d /opt/noc/docker"
            exit
            shift ;;
        --) shift
            break ;;
        *) echo "Example: ./noc-docker-backup.sh -p all -d /opt/noc/docker";;
    esac
    shift
done

if [ -z "$BACKUPPATH" ]
    then
        BACKUPPATH=$PWD
        echo "Backup NOC-DC to: $BACKUPPATH/var/backup-..."
        echo "---"
fi

if [ -n "$PARAM_P" ]
    then
        if [ "$PARAM_P" = "all" ]
            then
                BACKUPDATA
                BACKUPIMAGES
        elif [ "$PARAM_P" = "data" ]
            then
                BACKUPDATA
        elif [ "$PARAM_P" = "images" ]
            then
                BACKUPIMAGES
        else
            echo "Unknown parameter. Use: ./noc-docker-backup.sh -h"
        fi
else
    echo "No -p parameters found. Use: ./noc-docker-backup.sh -h"
fi

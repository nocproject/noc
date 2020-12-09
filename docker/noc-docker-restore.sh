#!/usr/bin/env bash

# Script restore persistent ./data  and docker images for noc
# Stop NOC before start restore
# -p - restore images or data
# -f - install dir
# -d - file with data archive

RESTOREDATA() {
    # check NOC is not running
    FILES="$PARAM_F/docker-compose.yml	$PARAM_F/docker-compose-infra.yml"
    for file in ${FILES};
    do
        # TODO Need update
        if docker-compose -f "$file" --project-directory=.. ps | grep Up ;
        then
    	    echo "---"
    	    echo "You need stop NOC-DC and/or NOC-DC-INFA container"
    	    echo "cd .. && docker-compose -f ""$file"" stop"
            exit
        fi
    done
    if [ -z "$PARAM_D" ]
        then
            echo "Error: '-d' is NULL. Exit"
            echo "Example: ./noc-docker-restore.sh -p data -d data-yyyymmdd-hh-mm.tar.gz"
            exit
    fi

    # restore ./data
    if ! [ -f "$PARAM_F"/var/backup-data/"$PARAM_D" ]
    then
        echo "Restore file: $PARAM_F/$PARAM_D not found"
        exit
    fi
    echo "Restore NOC-DC from file : ""$PARAM_D" to "$PARAM_F/../data"
    echo "---"
    tar -xvpzf "$PARAM_F"/var/backup-data/"$PARAM_D" -C "$PARAM_F"/
}

RESTOREIMAGES() {
    # restore docker image
    echo "Restore NOC-DC docker images from : $PARAM_F/var/backup-images"
    echo "---"
    FILES=$(find "$PARAM_F""/var/backup-images" -name "image-*.tar.gz" -type f -printf "%f\t" )
    if [ -z "$FILES" ]
        then
            echo "Images not fount in $PARAM_F/var/backup-images"
            exit
    fi
    for f in ${FILES};
    do
	    # load docker image from path
	    docker load < "$PARAM_F""/var/backup-images/""$f"
    done
}

while [ -n "$1" ]
do
    case "$1" in
        -p) PARAM_P="$2"
            #echo "Found the -p option, with parameter value $PARAM_P"
            shift ;;
        -f) PARAM_F="$2"
            echo "Found the -f option, full path to docker-compose.yml file"
            shift ;;
        -d) PARAM_D="$2"
            shift ;;
        -h) echo "  -p  'all' restore docker images and persistent data"
            echo "      'data' restore saved persistent data"
            echo "      'images' restore docker images"
            echo "Example: ./noc-docker-restore.sh -p images"
            echo "Example: ./noc-docker-restore.sh -p data -f /opt/noc -d data-yyyymmdd-hh-mm.tar.gz"
            exit
            shift ;;
        --) shift
            break ;;
        *)  echo "Example: ./noc-docker-restore.sh -p data -f /opt/noc -d data-yyyymmdd-hh-mm.tar.gz"
            echo "Example: ./noc-docker-restore.sh -p images";;
    esac
    shift
done

if [ -z "$PARAM_F" ]
    then
        PARAM_F=$PWD
        echo "Work dir NOC-DC is: ""$PARAM_F"
        echo "---"
fi

if [ -n "$PARAM_P" ]
   then
      if [ "$PARAM_P" = "all" ]
         then
             RESTOREDATA
             RESTOREIMAGES
      elif [ "$PARAM_P" = "data" ]
         then
             RESTOREDATA
      elif [ "$PARAM_P" = "images" ]
         then
             RESTOREIMAGES
      else
         echo "Unknown parameter.  Use: ./noc-docker-restore.sh -p images"
         echo "or: ./noc-docker-restore.sh -p data -f /opt/noc-dc -p data-yyyymmdd-hh-mm.tar.gz"
         echo "---"
      fi
else
   echo "No restore parameters found. Use: ./noc-docker-restore.sh -p images"
   echo "or: ./noc-docker-restore.sh -p data -f data-yyyymmdd-hh-mm.tar.gz"
   echo "---"
fi


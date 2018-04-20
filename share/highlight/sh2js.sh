#!/bin/sh
TMP=$(mktemp /tmp/noc-highlight.XXXXXX)
D=$(dirname $0)/shjs
#SRC=$(cd $(dirname $1); pwd)/$(basename $1)
#DST=$(cd $(dirname $2); pwd)/$(basename $2)
SRC=$1
DST=$2
perl -I$D $D/sh2js.pl $SRC > $TMP
if [ $? -eq 0 ]; then
    mv $TMP $DST
else
    rm -f $TMP
fi

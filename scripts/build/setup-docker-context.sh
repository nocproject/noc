#!/bin/sh
set -x
CTX=build/docker
mkdir -p $CTX
cp Dockerfile $CTX
# Prepare thin context
ROOT=$CTX/thin
echo "Preparing thin context at $ROOT"
rm -r $ROOT
mkdir -p $ROOT
mkdir -p $ROOT/usr/bin
mkdir -p $ROOT/opt/noc/speedup
cp requirements.txt $ROOT
cp scripts/build/get-noc-requirements.py $ROOT/usr/bin/get-noc-requirements
chmod a+x $ROOT/usr/bin/get-noc-requirements
cp speedup/*.pyx $ROOT/opt/noc/speedup
(cd $ROOT && tar cfz ../thin.tgz .)
rm -r $ROOT
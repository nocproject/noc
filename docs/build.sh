#!/bin/sh
set -e
for cfg in */mkdocs.yml; do
    book=$(dirname $cfg)
    if [ $book = "en" ]; then
        continue
    fi
    if [ $book = "ru" ]; then
        continue
    fi
    echo "##"
    echo "## Building ${book}"
    echo "##"
    cd $book    
    mkdocs build --strict
    cd ..
done
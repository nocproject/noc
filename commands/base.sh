#!/bin/sh

error_exit ( ) {
    printf "\033[1;31m$PROGNAME: ${1:-'Unknown error'}\033[0m\n" 1>&2
    exit 1
}

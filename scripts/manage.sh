#! /bin/bash

if test $(basename $0) != "manage.sh"; then
    echo "This script cannot be sourced; it must be executed." >&2
    return
fi
cd $(dirname $(readlink -f $0))/..

source functions.sh

assert_not_root
manage "$@"
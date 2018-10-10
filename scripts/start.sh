#! /bin/bash

if test $(basename $0) != "start.sh"; then
    echo "This script cannot be sourced; it must be executed." >&2
    return
fi
cd $(dirname $(readlink -f $0))/..

source functions.sh

assert_not_root
# TODO: these are broken because manage.py is invoked from cron without
#  setting up the environment variables from env-defaults.sh/env-overrides.sh
#schedule_django_tasks
start_solr

# allow SOLR to startup
sleep 10

start_gunicorn

#! /bin/bash

if test $(basename $0) != "install-deps.sh"; then
    echo "This script cannot be sourced; it must be executed." >&2
    return
fi
cd $(dirname $(readlink -f $0))/..

source functions.sh

assert_not_root
init_deps_dirs
install_system_packages
install_python_packages requirements.txt
install_bootstrap
install_jquery

# this file only contains function definitions; nothing is executed
# it is meant to be sourced by ./scripts/*.sh

source env-defaults.sh
if test -f env-overrides.sh; then
    source env-overrides.sh
fi

function assert_file_exists {
    local missing=false
    for f in $@; do
        if ! test -f $f; then
            echo "File '$f' does not exist." >&2
            missing=true
        fi
    done
    if $missing; then
        echo "Critical file(s) missing. Aborting." >&2
        exit 1
    fi
}

function assert_not_root {
    if test $(whoami) == "root"; then
        echo "this script is not to be run as root!" >&2
        exit 1
    fi
}

function init_deps_dirs {
    for d in deps/static/{css,js,fonts}; do
        mkdir -vp $d
    done
}

function install_pyenv {
    if which pyenv > /dev/null; then
        # pyenv already installed
        return
    fi
    echo "Installing pyenv" >&2
    curl -L "https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer" | bash
    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"

    init_pyenv='
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
'
    for rcfile in $HOME/.{profile,bashrc,bash_profile}; do
        if test -f $rcfile; then
            if ! grep -q 'pyenv init -' $rcfile; then
                echo "Adding pyenv init to $rcfile" >&2
                echo "$init_pyenv" | cat - $rcfile | sponge $rcfile
            fi
        fi
    done
}

function install_python {
    install_pyenv
    if pyenv local | grep $python_version > /dev/null \
            && python --version 2>&1 | grep $python_version > /dev/null; then
        return
    fi
    echo "Installing Python $python_version" >&2
    export PYTHON_CONFIGURE_OPTS="--enable-shared"
    pyenv install $python_version
}

function install_python_packages {
    install_python
    pyenv local $python_version/$virtualenv
    pip install -U pip
    pip install -U -r requirements.txt
}

function install_system_packages {
    apt_packages=$(grep -vP '^\s*#' apt-packages.txt)
    if ! apt -qq list $apt_packages 2>/dev/null | \
        grep -v '\[installed\]' > /dev/null 2>&1; then
        echo "All required system packages are installed" >&2
        return
    fi
    echo "Some system packages need to be installed." >&2
    echo "Run the following command as root:" >&2
    echo apt-get install $apt_packages
    exit 1
}

function install_bootstrap {
    echo "Installing bootstrap" >&2
    if ! test -f deps/bootstrap-$bs_version-dist/css/bootstrap.css; then
        wget -P deps $bs_base_url/bootstrap-$bs_version-dist.zip
        unzip -d deps -u deps/bootstrap-$bs_version-dist.zip
        rm -f deps/bootstrap-$bs_version-dist.zip
    fi
    for d in css js fonts; do
        ln -f deps/bootstrap-$bs_version-dist/$d/* deps/static/$d/
    done
}

function install_jquery {
    echo "Installing jquery" >&2
    if ! test -f deps/jquery-$jq_version/jquery-$jq_version.min.js; then
        mkdir -p deps/jquery-$jq_version
        wget -P deps/jquery-$jq_version -c \
            $jq_base_url/jquery-$jq_version.{js,min.js,min.map}
    fi
    for ext in  js min.js min.map; do
        ln -f deps/jquery-$jq_version/jquery-$jq_version.$ext deps/static/js/jquery.$ext
    done
}

function kill_process {
    pidfile=$1
    if ! test -f $pidfile; then
        echo "PID file $pidfile does not exist" >&2
        return
    fi
    pid=$(cat $pidfile)
    if ! test -d /proc/$pid; then
        echo "No process with PID=$pid" >&2
        rm -f $pidfile
        return
    fi
    echo "Sending TERM signal to process with PID=$pid" >&2
    kill -s TERM $pid
    for t in {0..3}; do
        if ! test -d /proc/$pid; then
            break
        fi
        sleep 1
    done
    if test -d /proc/$pid; then
        echo "Sending KILL signal to process with PID=$pid" >&2
        kill -s KILL $pid
    fi
    rm -f $pidfile
}

function init_run_dirs {
    mkdir -vp $DATA_DIR $LOGS_DIR $LOCK_DIR $PIDS_DIR
}

function start_standalone {
    init_run_dirs
    assert_file_exists manage.py metashare/settings.py
    exec python manage.py runserver $repository_port
}

function manage {
    assert_file_exists manage.py metashare/settings.py
    exec python manage.py "$@"
}

function start_gunicorn {
    echo "Starting gunicorn"
    init_run_dirs
    assert_file_exists manage.py metashare/settings.py
    gunicorn \
        --bind 127.0.0.1:$repository_port \
        --pid $PIDS_DIR/gunicorn.pid \
        --access-logfile $LOGS_DIR/access.log \
        --error-logfile $LOGS_DIR/error.log \
        --capture-output \
        --name repository-gunicorn \
        --daemon \
        metashare.wsgi:application
    echo "Gunicorn started"
}

function stop_gunicorn {
    echo "Stopping gunicorn"
    kill_process $PIDS_DIR/gunicorn.pid
    echo "Stopped gunicorn"
}

function start_solr {
    if test -f $PIDS_DIR/solr.txt \
        && test -d /proc/$(cat $PIDS_DIR/solr.txt); then
        echo "SOLR appears to be running" >&2
        return
    fi
    init_run_dirs
    # Update schema.xml files, just in case:
    assert_file_exists manage.py metashare/settings.py
    pushd "$CODE_DIR" > /dev/null
    python manage.py build_solr_schema \
        --filename="$CODE_DIR/solr/solr/main/conf/schema.xml"
    cp "$CODE_DIR/solr/solr/main/conf/schema.xml" \
        "$CODE_DIR/solr/solr/testing/conf/schema.xml"
    popd > /dev/null

    pushd "$CODE_DIR/solr" > /dev/null
    echo "Trying to start SOLR server" >&2
    java -Djetty.port=$solr_port \
        -DSTOP.PORT=$solr_stop_port \
        -DSTOP.KEY="$solr_stop_key" \
        -jar "$CODE_DIR/solr/start.jar" \
        > "$LOGS_DIR/solr.txt" 2>&1 &
    echo $! > "$PIDS_DIR/solr.txt"
    sleep 4
    popd > /dev/null
}

function stop_solr {
    if [ -f $PIDS_DIR/solr.txt ]; then
        pushd "$CODE_DIR/solr" > /dev/null
        echo "Trying to stop SOLR server" >&2
        java -DSTOP.PORT=$solr_stop_port -DSTOP.KEY="$solr_stop_key" \
            -jar "$CODE_DIR/solr/start.jar" --stop
        popd > /dev/null
    else
        echo "SOLR is not running" >&2
    fi
}

function kill_solr {
    pid="x"
    if test -f cat $PIDS_DIR/solr.txt; then
        pid=$(cat $PIDS_DIR/solr.txt)
    fi
    if test -d /proc/$pid; then
        echo "Killing SOLR (PID=$pid)" >&2
        kill -s SIGKILL $pid
    else
        echo "SOLR is not running" >&2
    fi
    rm -f -- $PIDS_DIR/solr.txt
}

function schedule_django_tasks {
    echo "Scheduling Django tasks" >&2
    python manage.py installtasks >&2
    echo "Scheduled Django tasks" >&2
}

function deploy {
    if test $# != 1; then
        echo "Missing one argument." >&2
        echo "Usage: $0 COMMIT" >&2
        return
    fi

    local NEW_COMMIT=$1
    local CURRENT_COMMIT=$(git show --format=%H --no-patch)

    echo "Updating from $CURRENT_COMMIT to $NEW_COMMIT"

    git checkout -B production $NEW_COMMIT

    if git diff --name-only $CURRENT_COMMIT $NEW_COMMIT | grep -q /static/ ; then
        echo "Static resources have changed"
        echo "Running manage.py collectstatic..."
        ./scripts/manage.sh collectstatic
        echo "Finished manage.py collectstatic"
    else
        echo "Static resources not changed"
    fi

    stop_gunicorn
    start_gunicorn
}

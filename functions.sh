# this file only contains function definitions; nothing is executed
# it is meant to be sourced by ./scripts/*.sh

source env-defaults.sh
if test -f env-overrides.sh; then
    source env-overrides.sh
fi

function assert_file_exists {
    local MISSING=false
    for f in $@; do
        if ! test -f $f; then
            echo "File '$f' does not exist." >&2
            MISSING=true
        fi
    done
    if $MISSING; then
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
    for D in $DEPS_DIR/static/{css,js,fonts}; do
        mkdir -vp $D
    done
}

function check_pyenv {
    if which pyenv > /dev/null; then
        return
    fi
    if test -d $HOME/.pyenv; then
        export PATH="$HOME/.pyenv:$PATH"
    fi
    if which pyenv > /dev/null; then
        eval "$(pyenv init -)"
        eval "$(pyenv virtualenv-init -)"
        true
    fi
}
function install_pyenv {
    if check_pyenv; then
        # pyenv already installed
        return
    fi
    echo "Installing pyenv" >&2
    curl -L "https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer" | bash
    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"

    local INIT_PYENV='
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
'
    for RCFILE in $HOME/.{profile,bashrc,bash_profile}; do
        if test -f $RCFILE; then
            if ! grep -q 'pyenv init -' $RCFILE; then
                echo "Adding pyenv init to $RCFILE" >&2
                echo "$INIT_PYENV" | cat - $RCFILE | sponge $RCFILE
            fi
        fi
    done
}

function install_python {
    install_pyenv
    if pyenv versions | grep $PYTHON_VERSION > /dev/null; then
        return
    fi
    echo "Installing Python $PYTHON_VERSION" >&2
    export PYTHON_CONFIGURE_OPTS="--enable-shared"
    pyenv install $PYTHON_VERSION
}

function install_python_packages {
    install_python
    pyenv virtualenv $PYTHON_VERSION $VIRTUALENV_NAME
    pyenv local $VIRTUALENV_NAME
    pip install -U pip
    # increase timeout to 1 minute (60 seconds)
    # default is 15 seconds
    pip install -U --timeout 60 -r $1
}

function install_system_packages {
    local APT_PACKAGES=$(grep -vP '^\s*#' apt-packages.txt)
    if ! apt -qq list $APT_PACKAGES 2>/dev/null | \
        grep -v '\[installed\]' > /dev/null 2>&1; then
        echo "All required system packages are installed" >&2
        return
    fi
    echo "Some system packages need to be installed." >&2
    echo "Run the following commands as root:" >&2
    echo dpkg --add-architecture i386
    echo apt-get update
    echo apt-get install $APT_PACKAGES
    exit 1
}

function install_bootstrap {
    echo "Installing bootstrap" >&2
    if ! test -f $DEPS_DIR/bootstrap-$BS_VERSION-dist/css/bootstrap.css; then
        wget -P $DEPS_DIR $BS_BASE_URL/bootstrap-$BS_VERSION-dist.zip
        unzip -d $DEPS_DIR -u $DEPS_DIR/bootstrap-$BS_VERSION-dist.zip
        rm -f $DEPS_DIR/bootstrap-$BS_VERSION-dist.zip
    fi
    for D in css js fonts; do
        ln -f $DEPS_DIR/bootstrap-$BS_VERSION-dist/$D/* $DEPS_DIR/static/$D/
    done
}

function install_jquery {
    echo "Installing jquery" >&2
    if ! test -f $DEPS_DIR/jquery-$JQ_VERSION/jquery-$JQ_VERSION.min.js; then
        mkdir -p $DEPS_DIR/jquery-$JQ_VERSION
        wget -P $DEPS_DIR/jquery-$JQ_VERSION -c \
            $JQ_BASE_URL/jquery-$JQ_VERSION.{js,min.js,min.map}
    fi
    for EXT in  js min.js min.map; do
        ln -f $DEPS_DIR/jquery-$JQ_VERSION/jquery-$JQ_VERSION.$EXT $DEPS_DIR/static/js/jquery.$EXT
    done
}

function collect_static {
    echo "Running manage.py collectstatic..."
    manage collectstatic --link --noinput
    echo "Finished manage.py collectstatic"
}

function kill_process {
    local PIDFILE=$1
    if ! test -f $PIDFILE; then
        echo "PID file $PIDFILE does not exist" >&2
        return
    fi
    local PID=$(cat $PIDFILE)
    if ! test -d /proc/$PID; then
        echo "No process with PID=$PID" >&2
        rm -f $PIDFILE
        return
    fi
    echo "Sending TERM signal to process with PID=$PID" >&2
    kill -s TERM $PID
    for t in {0..3}; do
        if ! test -d /proc/$PID; then
            break
        fi
        sleep 1
    done
    if test -d /proc/$PID; then
        echo "Sending KILL signal to process with PID=$PID" >&2
        kill -s KILL $PID
    fi
    rm -f $PIDFILE
}

function init_run_dirs {
    mkdir -vp $DATA_DIR $LOGS_DIR $LOCK_DIR $PIDS_DIR
}

function start_standalone {
    init_run_dirs
    check_pyenv
    assert_file_exists manage.py metashare/settings.py
    exec python manage.py runserver $REPOSITORY_PORT
}

function manage {
    check_pyenv
    assert_file_exists manage.py metashare/settings.py
    exec python manage.py "$@"
}

function start_gunicorn {
    init_run_dirs
    check_pyenv
    assert_file_exists manage.py metashare/settings.py
    gunicorn \
        --bind 127.0.0.1:$REPOSITORY_PORT \
        --pid $PIDS_DIR/gunicorn.pid \
        --access-logfile $LOGS_DIR/access.log \
        --error-logfile $LOGS_DIR/error.log \
        --capture-output \
        --name repository-gunicorn \
        --daemon \
        metashare.wsgi:application
}

function stop_gunicorn {
    kill_process $PIDS_DIR/gunicorn.pid
}

function start_solr {
    if solr_is_running; then
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
    java -Djetty.port=$SOLR_PORT \
        -DSTOP.PORT=$SOLR_STOP_PORT \
        -DSTOP.KEY="$SOLR_STOP_KEY" \
        -jar "$CODE_DIR/solr/start.jar" \
        > "$LOGS_DIR/solr.txt" 2>&1 &
    echo $! > "$PIDS_DIR/solr.txt"
    popd > /dev/null

    # wait until solr starts responding to pings:
    for i in {1..20}; do
        sleep 2
        if ping_solr; then
            break
        fi
    done
}

function ping_solr {
    curl -s http://localhost:$SOLR_PORT/solr/main/admin/ping?indent=1 |
    grep -q '<str name="status">OK</str>'
}

function solr_is_running {
    test -f $PIDS_DIR/solr.txt \
        && test -d /proc/$PID \
        && ping_solr
}

function stop_solr {
    if solr_is_running; then
        pushd "$CODE_DIR/solr" > /dev/null
        echo "Trying to stop SOLR server" >&2
        java -DSTOP.PORT=$SOLR_STOP_PORT \
            -DSTOP.KEY="$SOLR_STOP_KEY" \
            -jar "$CODE_DIR/solr/start.jar" \
            --stop
        popd > /dev/null
    else
        echo "SOLR is not running" >&2
    fi
}

function kill_solr {
    if solr_is_running; then
        local PID=$(cat $PIDS_DIR/solr.txt)
        echo "Killing SOLR (PID=$PID)" >&2
        kill -s SIGKILL $PID
    else
        echo "SOLR is not running" >&2
    fi
    rm -f -- $PIDS_DIR/solr.txt
}

function schedule_django_tasks {
    check_pyenv
    python manage.py installtasks >&2
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

    echo "Installing dependencies"

    ./scripts/install-deps.sh

    if git diff --name-only $CURRENT_COMMIT $NEW_COMMIT | grep -q /static/ ; then
        echo "Static resources have changed"
        collect_static
    else
        echo "Static resources not changed"
    fi

    stop_gunicorn
    start_gunicorn
}

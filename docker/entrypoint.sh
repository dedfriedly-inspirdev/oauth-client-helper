#!/usr/bin/env bash
set -e

export PYTHONPATH=${PYTHONPATH}:/usr/local/src
echo 'export PYTHONPATH=${PYTHONPATH}:/usr/local/src' >> ~/.bashrc


TRY_LOOP="10"

# Install custom python package if requirements.txt is present in root
# TODO: require user to set PY_REQ_FILE env var as a path to file AND ensure file exists at location
if [ -e "/requirements.txt" ]; then
    $(command -v pip) install --user -r /requirements.txt
fi

wait_for_port() {
  local name="$1" host="$2" port="$3"
  local j=0
  while ! nc -z "$host" "$port" >/dev/null 2>&1 < /dev/null; do
    j=$((j+1))
    if [ $j -ge $TRY_LOOP ]; then
      echo >&2 "$(date) - $host:$port still not reachable, giving up"
      exit 1
    fi
    echo "$(date) - waiting for $name (Host:${host} Port:${port})... $j/$TRY_LOOP"
    sleep 5
  done
}

# Adding globals for message queue
# Setup globals
: "${MQ_HOST:="redis"}"
: "${MQ_PASS:=""}"
: "${MQ_DB:="0"}"
: "${MQ_PROTOCOL:="redis"}"
: "${MQ_PORT:="6379"}"
: "${MQ_EXTRAS:-""}"

wait_for_port "Message Queue" "${MQ_HOST}" "${MQ_PORT}"

# Build out for specific quick-hitters
case "$1" in
  "auth")
    echo "Starting my flask app"
    sleep 2
    python ${CODEDIR}/wsgi.py
    ;;
  "debug")
    echo "Running open ended proc, drop into image with exec"
    # Trap interrupts and exit instead of continuing the loop
    trap "echo Exited!; exit;" SIGINT SIGTERM
    while true; do sleep 5; done
    ;;
  *)
    # The command is something like bash, not an airflow subcommand. Just run it in the right environment.
    echo "DEBUG: uncaught docker command"
    exec "$@"
    ;;
esac
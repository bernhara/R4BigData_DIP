#! /bin/bash

SUB_CMD="$1"

THERE=`dirname "${SUB_CMD}"`
CMD=`basename "${SUB_CMD}"`

: ${stdout_log_file:="${THERE}/${CMD}.stdout.log"}
: ${stderr_log_file:="${THERE}/${CMD}.stderr.log"}


: ${redirect_output:=true}

if ${redirect_output}
then
    exec 1>"${stdout_log_file}" 2>"${stderr_log_file}"
fi

exec "$@"

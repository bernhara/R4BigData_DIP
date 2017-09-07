#! /bin/bash

: ${PYTHON:="python3"}

here=`dirname "$0"`
wrapped_command="$1"
shift 1


corresponding_python_main=`basename "${wrapped_command}" ".sh"`

: ${python_src_dir:="${here}/../src"}

: ${python_main:="${python_src_dir}/${corresponding_python_main}.py"}

${PYTHON} "${python_main}" "$@"


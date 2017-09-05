#! /bin/bash

: ${PYTHON:="python3"}

here=`dirname "$0"`

this_command=`basename "$0" ".sh"`

: ${python_src_dir:="${here}/../src"}

: ${python_main:="${python_src_dir}/${this_command}.py"}

${PYTHON} "${python_main}" "$@"

#! /bin/bash

: ${PYTHON_WARPPER:="_python_wrapper.sh"}

`dirname "$0"`/"${PYTHON_WARPPER}" "$0" "$@"

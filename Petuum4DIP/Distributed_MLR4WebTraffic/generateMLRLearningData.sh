#! /bin/bash

HERE=`dirname $0`
CMD=`basename $0`

ARGarray=( "$@" )

if [ -r "${HERE}/${CMD}-config" ]
then
    . "${HERE}/${CMD}-config"
fi


Usage ()
{
    if [ -n "$1" ]
    then
	echo "ERROR: $1" 1>&2
    fi
    echo "Usage: ${CMD} [(-l|--labels) <indexed table of all labels/categories>] <libsvm file name containing translated squid access logs>" 1>&2
    exit 1
}

libsvm_file=''
labels_file=''

set -- "${ARGarray[@]}"

while [ -n "$1" ]
do
    case "$1" in
	'-l' | '--labels' )
	    shift 1
	    labels_file="$1"
	    if [ -z "${labels_file}" ]
	    then
		Usage
	    fi
	    ;;

	* )
	    if [ -n "${libsvm_file}" ]
	    then
		Usage
	    fi
	    libsvm_file="$1"
	    ;;
    esac
    shift
    
done

if [ -z "${libsvm_file}" ]
then
    Usage "Missing <target svm file> argument"
fi

##############################################################################################

: ${DIP_ROOT_DIR:="${HERE}/../.."}

: ${rebuidFillSquidLogs:="${DIP_ROOT_DIR}/DataCollection/SquidLogsImport/rebuildFullSquidLogs.sh"}
: ${translateAccessLogToSquidGuardInput:="${DIP_ROOT_DIR}/SquidGuardClassifier/translateAccessLogToSquidGuardInput.sh"}
: ${squidGuard_conf:="${DIP_ROOT_DIR}/SquidGuardClassifier/squidGuard.conf"}
: ${squidGuard_cmd:="squidGuard -c ${squidGuard_conf}"}

: ${squidGuardToSVM_py:="${HERE}/lib/python/SquidGuardToSVM/src/squidGuardToSVM.py"}

#
# Manage tmp storage

: ${remove_tmp:=true}
: ${tmp_dir:=`mktemp -u -p "${HERE}/tmp"`}

: ${python:=python3}

if ${remove_tmp}
then
    trap 'rm -rf "${tmp_dir}"' 0
fi

# import_logs_dir is supposed to exist
mkdir -p "${tmp_dir}"

#
# Classify all available logs with squidGuard
#


${rebuidFillSquidLogs} > "${tmp_dir}/access.log"

cat "${tmp_dir}/access.log" | \
${translateAccessLogToSquidGuardInput} \ |
( ${squidGuard_cmd} 2>${tmp_dir}/squidGuard.stderr ) \
 > "${tmp_dir}/squidGuardClassifiedLogs.txt"

${python} "${squidGuardToSVM_py}" \
    --squidAccessLogFile "${tmp_dir}/access.log" \
    --squidGuardFile "${tmp_dir}/squidGuardClassifiedLogs.txt" \
    --libSVMFile "${tmp_dir}/access_libsvm.txt" \
    --squidGuardConf "${squidGuard_conf}" \
    --categoriesDump "${tmp_dir}/labels.txt"


# procude results
cp "${tmp_dir}/access_libsvm.txt" "${libsvm_file}"
cp "${tmp_dir}/access_libsvm.txt.meta" "${libsvm_file}.meta"

if [ -n "${labels_file}" ]
then
    cp "${tmp_dir}/labels.txt" "${labels_file}"
fi

#! /bin/bash

HERE=`dirname $0`
CMD=`basename $0`

if [ -r "${HERE}/${CMD}-config" ]
then
    . "${HERE}/${CMD}-config"
fi


: ${DIP_ROOT_DIR:="${HERE}/../.."}

: ${rebuidFillSquidLogs:="${DIP_ROOT_DIR}/DataCollection/SquidLogsImport/rebuildFullSquidLogs.sh"}
: ${translateAccessLogToSquidGuardInput:="${DIP_ROOT_DIR}/SquidGuardClassifier/translateAccessLogToSquidGuardInput.sh"}
: ${squidGuard_cmd:="squidGuard -c ${DIP_ROOT_DIR}/SquidGuardClassifier/squidGuard.conf"}

#
# Manage tmp storage

: ${remove_tmp:=true}
: ${tmp_dir:=`mktemp -u -p "${HERE}/tmp"`}

if ${remove_tmp}
then
    trap 'rm -rf "${tmp_dir}"' 0
fi

# import_logs_dir is supposed to exist
mkdir -p "${tmp_dir}"

#
# Classify all available logs with squidGuard
#


${rebuidFillSquidLogs} | \
${translateAccessLogToSquidGuardInput} \ |
${squidGuard_cmd} > ${tmp_dir}/squidGuardClassifiedLogs.txt

exit 1

##############################################################

: ${import_logs_dir:=${HERE}/ClonedLogs/imported}
: ${full_logs_file:=${HERE}/ClonedLogs/full_access.log}


: ${tmp_dir:=`mktemp -u -p "${HERE}/ClonedLogs/tmp"`}

if [ -r "myId.sh" ]
then
    echo "ERROR: shell variable \"my_name\" undefinded. See ${HERE}/${CMD}-config file." 1>&2
    exit 1
fi


access_log_file_list=`find "${import_logs_dir}" -type f -name "access.log*" -print`

# concatenate all log files

(
   for log_file in ${access_log_file_list}
   do
      case "${log_file}" in
	  *.gz)
	      zcat "${log_file}"
	      ;;
	  *)
	      cat "${log_file}"
	      ;;
      esac
   done
) > "${tmp_dir}/summed_logs.txt"

sort -g --output="${full_logs_file}" "${tmp_dir}/summed_logs.txt"

cat "${tmp_dir}/summed_logs.txt"

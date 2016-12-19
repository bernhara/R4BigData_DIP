#! /bin/bash

: ${import_logs_dir:=ClonedLogs/imported}
: ${full_logs_file:=ClonedLogs/full_access.log}

: ${remove_tmp:=true}
: ${tmp_dir:=ClonedLogs/tmp}

if [ -r "myId.sh" ]
then
   # to prevent bad X flag
   chmod +x "myId.sh"

   . ./myId.sh
fi

date

if ${remove_tmp}
then
    trap 'rm -rf "${tmp_dir}"' 0
fi

# import_logs_dir is supposed to exist
mkdir -p "${tmp_dir}"

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

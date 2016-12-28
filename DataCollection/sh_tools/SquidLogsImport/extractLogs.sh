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
	echo "ERROR: $1"
    fi
    echo "Usage: ${CMD} [(-s|--start_date) <start date>] [(-e|--end_date) <end_date>]" 1>&2
    exit 1
}

hr_start_date=''
hr_end_date=''

set -- "${ARGarray[@]}"

while [ -n "$1" ]
do
    case "$1" in
	'-s' | '--start_date')
	    shift 1
	    hr_start_date="$1"
	    if [ -z "${hr_start_date}" ]
	    then
		Usage
	    fi
	    ;;

	'-e' | '--end_date' )
	    shift 1
	    hr_end_date="$1"
	    if [ -z "${hr_end_date}" ]
	    then
		Usage
	    fi
	    ;;

	* )
	    echo "Arg error: $OPTARG" 1>&2
	    ;;
    esac
    shift
    
done

date -d "${hr_start_date}" >/dev/null 2>/dev/null
if [ $? -ne 0 ]
then
    Usage "bad start date format"
fi

date -d "${hr_end_date}" >/dev/null 2>/dev/null
if [ $? -ne 0 ]
then
    Usage "bad end date format"
fi

if [ -z "${hr_start_date}" ]
then
    # the epoch
    start_date_since_epoch=0
else
    start_date_since_epoch=`date -d "${hr_start_date}" +%s`
fi

if [ -z "${hr_endt_date}" ]
then
    # far future!
    end_date_since_epoch=`date -d 'now + 10 years' +%s`
else
    end_date_since_epoch=`date -d "${hr_end_date}" +%s`
fi

exit 1

: ${import_logs_dir:=${HERE}/ClonedLogs/imported}
: ${full_logs_file:=${HERE}/ClonedLogs/full_access.log}

: ${remove_tmp:=true}
: ${tmp_dir:=ClonedLogs/tmp}

if [ -r "myId.sh" ]
then
    echo "ERROR: shell variable \"my_name\" undefinded. See ${HERE}/${CMD}-config file." 1>&2
    exit 1
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

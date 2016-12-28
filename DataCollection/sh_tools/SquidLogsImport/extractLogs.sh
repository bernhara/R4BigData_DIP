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


: ${import_logs_dir:=${HERE}/ClonedLogs/imported}

: ${remove_tmp:=true}
: ${tmp_dir:=ClonedLogs/tmp}

date

if ${remove_tmp}
then
    trap 'rm -rf "${tmp_dir}"' 0
fi

# import_logs_dir is supposed to exist
mkdir -p "${tmp_dir}"

cat - > "${tmp_dir}/extractLogs_source_squid_logs.txt"

(
    echo "${end_date_since_epoch} =====EXTRACT====END===="
    echo "${start_date_since_epoch} =====EXTRACT====START===="
) >> "${tmp_dir}/extractLogs_source_squid_logs.txt"

sort -g --output="${tmp_dir}/extractLogs_marked_squid_logs.txt" "${tmp_dir}/extractLogs_source_squid_logs.txt"
sed -n '/=====EXTRACT====START====/,/=====EXTRACT====END====/p' "${tmp_dir}/extractLogs_marked_squid_logs.txt" > "${tmp_dir}/extractLogs_extracted_subset.txt"
sed \
    -e '1d' \
    -e '$d' "${tmp_dir}/extractLogs_extracted_subset.txt" > "${tmp_dir}/extractLogs_bounded_logs.txt"


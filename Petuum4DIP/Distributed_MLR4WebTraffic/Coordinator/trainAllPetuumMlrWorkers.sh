#! /bin/bash

HERE=`dirname $0`
CMD=`basename $0`

ARGarray=( "$@" )

if [ -r "${HERE}/${CMD}-config" ]
then
    . "${HERE}/${CMD}-config"
fi


: ${WORKER_DEFAULT_INSTALL_DIR:=R4BigData_DIP/Petuum4DIP/Distributed_MLR4WebTraffic/Worker}

Usage ()
{
    if [ -n "$1" ]
    then
	echo "ERROR: $1" 1>&2
    fi
    echo "Usage: ${CMD} [--dryrun] <worker specification> [<worker specification>]*" 1>&2
    echo "with <worker specification> having the following form: [<remote user>@]<worker hostname>[:<mlr remote folder installation dir if differs from default>]" 1>&2
    echo "NOTES: workers are indexed in appearing order (first specified worker has index 0)" 1>&2
    exit 1
}

realpath () {
    readlink --canonicalize "$1"
}

set -- "${ARGarray[@]}"

dryrun=false
if [ "$1" = "--dryrun" ]
then
    dryrun=true
    shift 1
fi

declare -a petuum_workers_specification_list

list_index=0
while [ -n "$1" ]
do
    worker_specification="$1"

    worker_index="${list_index}"

    worker_ssh_specification="${worker_specification%:*}"
    worker_ssh_hostname="${worker_ssh_specification#*@}"
    worker_ssh_remote_user="${worker_ssh_specification%@*}"
    if [ "${worker_ssh_remote_user}" = "${worker_ssh_specification}" ]
    then
	# no remote user specified
	worker_ssh_remote_user=""
    fi

    worker_ssh_remote_path_specification="${worker_specification#*:}"
    if [ "${worker_ssh_remote_path_specification}" = "${worker_specification}" ]
    then
	# no remote path specified => same path
	worker_ssh_remote_path_specification="${WORKER_DEFAULT_INSTALL_DIR}"
    fi

    petuum_workers_specification_list[${worker_index}]="'${list_index}' '${worker_ssh_remote_user}' '${worker_ssh_hostname}' '${worker_ssh_remote_path_specification}'"
    list_index=$(( ${list_index} + 1 ))

    shift

done

if [ ${#petuum_workers_specification_list[@]} -eq 0 ]
then
    Usage "Missing worker specification"
fi

##############################################################################################


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
# Launch MLR on all workerd
#


: ${petuum_interworker_tcp_port:=9999}
num_clients=${#petuum_workers_specification_list[@]}

build_worker_launcher_common_args () {

    worker_launcher_common_args=''

    for worker_specification in "${petuum_workers_specification_list[@]}"
    do
        # transform the list into an array (all elements are quoted to handle empty elements (=> eval)
	eval worker_specification_array=( ${worker_specification} )
	worker_index="${worker_specification_array[0]}"
	worker_ssh_remote_user="${worker_specification_array[1]}"
	worker_ssh_hostname="${worker_specification_array[2]}"
	worker_ssh_remote_path_specification="${worker_specification_array[3]}"

	worker_launcher_common_args="${worker_launcher_common_args} ${worker_ssh_hostname}:${petuum_interworker_tcp_port}"
    done

    echo "${worker_launcher_common_args}"

}

worker_launcher_common_args=$( build_worker_launcher_common_args )

build_worker_mlr_cmd () {

    worker_index="${worker_specification_array[0]}"
    worker_ssh_remote_user="${worker_specification_array[1]}"
    worker_ssh_hostname="${worker_specification_array[2]}"
    worker_ssh_remote_path_specification="${worker_specification_array[3]}"

    if [ -n "${worker_ssh_remote_user}" ]
    then
	worker_ssh_remote_specification="${worker_ssh_remote_user}@${worker_ssh_hostname}"
    else
	worker_ssh_remote_specification="${worker_ssh_hostname}"
    fi

    local_worker_command="\
${worker_ssh_remote_path_specification}/trainWorker.sh ${worker_index} ${worker_launcher_common_args} \
"

    remote_command="ssh \
-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
${worker_ssh_remote_specification} \
\
${local_worker_command}\
\
"

    echo "${remote_command}"
}

# lauch all workers

for worker_specification in "${petuum_workers_specification_list[@]}"
do
    # transform the list into an array (all elements are quoted to handle empty elements (=> eval)
    eval worker_specification_array=( ${worker_specification} )
    worker_index="${worker_specification_array[0]}"
    worker_ssh_remote_user="${worker_specification_array[1]}"
    worker_ssh_hostname="${worker_specification_array[2]}"
    worker_ssh_remote_path_specification="${worker_specification_array[3]}"

    launch_command=$( build_worker_mlr_cmd "${worker_index}" "${worker_ssh_remote_user}" "${worker_ssh_hostname}" "${worker_ssh_remote_path_specification}" )

    if $dryrun
    then
	echo "** would execute **: ${launch_command}"
    else
	(
	    ${launch_command}
	    echo "$? ${worker_index} ${worker_ssh_hostname}">${tmp_dir}/worker-${worker_index}-${worker_ssh_hostname}.exit_status
	) 2>${tmp_dir}/worker-${worker_index}-${worker_ssh_hostname}.stderr.log  1>${tmp_dir}/worker-${worker_index}-${worker_ssh_hostname}.stdout.log

    fi

    
done

# wait for termination af all lauched workers
wait

# test if some failed
exit_status_file_list=$( ls -1 ${tmp_dir}/worker-*.exit_status  2>/dev/null )
for exit_status_file in ${exit_status_file_list}
do
    set -- $( cat "${exit_status_file}" )
    exit_status=$1
    worker_index=$2
    woker_ssh_hostname=$3
    if [ "${exit_status}" -ne "0" ]
    then
	(
	    echo "ERROR: worker #${worker_index} ($worker_ssh_hostname) FAILED"
	    echo
	    echo "STDOUT:"
	    echo
	    echo "================================================================================="
	    cat "${tmp_dir}/worker-${worker_index}-${worker_ssh_hostname}.stdout.log"
	    echo "================================================================================="
	    echo
	    echo "STDERR:"
	    echo
	    echo "================================================================================="
	    cat "${tmp_dir}/worker-${worker_index}-${worker_ssh_hostname}.stderr.log"
	    echo "================================================================================="
	) 1>&2
    fi
done

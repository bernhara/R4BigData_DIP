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
    echo "Usage: ${CMD} <worker hostname> [<worker hostname>]*" 1>&2
    echo "NOTES: workers are indexed in appearing order (first specified worker has index 0)" 
    exit 1
}

set -- "${ARGarray[@]}"

declare -a petuum_workers_specification_list

list_index=0
while [ -n "$1" ]
do
    worker_hostname="$1"

    petuum_workers_specification_list[${list_index}]="${list_index} ${worker_hostname}"
    list_index=$(( ${list_index} + 1 ))

    shift

done

if [ ${#petuum_workers_specification_list[@]} -eq 0 ]
then
    Usage "Missing worker specification"
fi

##############################################################################################


: ${DIP_ROOT_DIR:="${HERE}/../.."}

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

build_worker_mlr_cmd () {

    worker_index="$1"
    worker_name="$2"

    remote_here=$( realpath "${HERE}" ) 


    local_generate_learning_data_command="./generateMLRLearningData.sh ${tmp_dir}/libsvm_access_log.txt -l ${tmp_dir}/labels.txt"
    local_worker_mlr_command="\
GLOG_logtostderr=true GLOG_v=-1 GLOG_minloglevel=0 \
/share/Petuum/bosen/app/mlr/bin/mlr_main \
--num_comm_channels_per_client=1 \
--staleness=2 --client_id=0 --num_app_threads=1 \
--num_clients=${num_clients} \
--use_weight_file=false --weight_file= \
--num_batches_per_epoch=10 --num_epochs=40 \
--output_file_prefix=${tmp_dir}/rez \
--lr_decay_rate=0.99 --num_train_eval=10000 \
--global_data=true \
--init_lr=0.01 \
--num_test_eval=20 --perform_test=false --num_batches_per_eval=10 --lambda=0 \
--hostfile=${tmp_dir}/localserver \
--train_file=${tmp_dir}/libsvm_access_log.txt \
"

    remote_command="ssh \
-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
${worker_name} \
\
/bin/bash -c \"\
cd ${remote_here} && \
\
${local_generate_learning_data_command} && \
\
${local_worker_mlr_command}
\"\
"

    echo "${remote_command}"
}

# generate server file
(
    for worker_specification in "${petuum_workers_specification_list[@]}"
    do
	set -- ${worker_specification}
	worker_index="$1"
	worker_hostname="$2"
	echo ${worker_index} ${worker_hostname} ${petuum_interworker_tcp_port}
    done
) > ${tmp_dir}/localserver

# lauch all workers

for worker_specification in "${petuum_workers_specification_list[@]}"
do
    set -- ${worker_specification}
    worker_index="$1"
    worker_hostname="$2"
    launch_command=$( build_worker_mlr_cmd "${worker_index}" "${worker_hostname}" )
    ( ${launch_command}; echo "$? ${worker_index} ${worker_hostname}">${tmp_dir}/worker-${worker_index}-${worker_hostname}.exit_status ) 2>${tmp_dir}/worker-${worker_index}-${worker_hostname}.stderr.log  1>${tmp_dir}/worker-${worker_index}-${worker_hostname}.stdout.log &
done

# wait for termination af all lauched workers
wait

# test if some failed
exit_status_file_list=${tmp_dir}/worker-*.exit_status
for exit_status_file in ${exit_status_file_list}
do
    set -- $( cat "${exit_status_file}" )
    exit_status=$1
    worker_index=$2
    woker_hostname=$3
    if [ "${exit_status}" -ne "0" ]
    then
	(
	    echo "ERROR: worker #${worker_index} ($worker_hostname) FAILED"
	    echo
	    echo "STDOUT:"
	    echo
	    echo "================================================================================="
	    cat "${tmp_dir}/worker-${worker_index}-${worker_hostname}.stdout.log"
	    echo "================================================================================="
	    echo
	    echo "STDERR:"
	    echo
	    echo "================================================================================="
	    cat "${tmp_dir}/worker-${worker_index}-${worker_hostname}.stderr.log"
	    echo "================================================================================="
	) 1>&2
    fi
done

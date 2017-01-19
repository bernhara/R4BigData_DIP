#! /bin/bash

HERE=`dirname $0`
CMD=`basename $0`

ARGarray=( "$@" )

if [ -r "${HERE}/${CMD}-config" ]
then
    . "${HERE}/${CMD}-config"
fi

# Globals
: ${PETUUM_INSTALL_DIR:=/share/Petuum}
: ${MLR_MAIN:="${PETUUM_INSTALL_DIR}/bosen/app/mlr/bin/mlr_main"}

Usage ()
{
    if [ -n "$1" ]
    then
	echo "ERROR: $1" 1>&2
    fi
    echo "Usage: ${CMD} [--dryrun] <this worker index> <worker specification> [<worker specification>]*" 1>&2
    echo "with <worker specification> having the following form: <worker hostname>:<petuum interworker tcp port>" 1>&2
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

this_worker_index="$1"
shift 1

if [ -z ${this_worker_index} ]
then
    Usage "Missing <this worker index> argument"
fi

declare -a petuum_workers_specification_list

list_index=0
while [ -n "$1" ]
do
    worker_specification="$1"

    worker_index="${list_index}"

    worker_hostname="${worker_specification%:*}"
    petuum_interworker_tcp_port="${worker_specification#*:}"

    petuum_workers_specification_list[${worker_index}]="'${list_index}' '${worker_hostname}' '${petuum_interworker_tcp_port}'"
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

# generate server file
(
    for worker_specification in "${petuum_workers_specification_list[@]}"
    do

        # transform the list into an array (all elements are quoted to handle empty elements (=> eval)
        eval worker_specification_array=( ${worker_specification} )
        worker_index="${worker_specification_array[0]}"
        worker_hostname="${worker_specification_array[1]}"
        petuum_interworker_tcp_port="${worker_specification_array[2]}"

        echo ${worker_index} ${worker_hostname} ${petuum_interworker_tcp_port}
    done
) > ${tmp_dir}/localserver

#
# Launch MLR on all workerd
#


"${HERE}/generateMLRLearningData.sh" ${tmp_dir}/libsvm_access_log.txt -l ${tmp_dir}/labels.txt

# TODO: which args should be parametrized

num_clients=${#petuum_workers_specification_list[@]}

GLOG_logtostderr=true GLOG_v=-1 GLOG_minloglevel=0 \
"${MLR_MAIN}" \
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

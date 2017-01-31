#! /bin/bash

HERE=`dirname $0`
CMD=`basename $0`

ARGarray=( "$@" )

if [ -r "${HERE}/${CMD}-config" ]
then
    . "${HERE}/${CMD}-config"
fi

# Globals
: ${PETUUM_INSTALL_DIR:=/share/PLMS}
: ${MLR_MAIN:="${PETUUM_INSTALL_DIR}/bosen/app/mlr/bin/mlr_main"}
: ${PARTITION_DEFAULT_SIZE_IN_PARTITIONED_MODE:=500}


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
    if [ "${worker_hostname}" = "${worker_specification}" ]
    then
	Usage "Missing port in <worker specification>"
    fi

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
# Utils
#

globalDataFormatToWorkerLocalDataFormat ()
{
    global_data_libsvm_file="$1"
    nb_workers="$2"
    local_sample_size="$3"
    local_data_libsvm_file="$4"

    global_data_libsvm_meta_file="$1.meta"
    local_data_libsvm_meta_file="$4.meta"

    global_sample_size=$(( ${nb_workers} * ${local_sample_size} ))

    tmp_array=( $( grep 'num_train_this_partition' "${global_data_libsvm_meta_file}"  ) )
    global_data_num_train_this_partition=${tmp_array[1]}

    if [ "${global_data_num_train_this_partition}" -lt "${local_sample_size}" ]
    then
	# not enough data in provided sample
	Usage "Requested sample size is ${sample_size} but they are only ${global_data_num_train_this_partition} currently available"
	# not reached
    fi

    # generate sample subset
    tail --lines="${local_sample_size}" "${global_data_libsvm_file}" > "${local_data_libsvm_file}"

    # generate the corresponding meta file
    sed \
	-e "/num_train_total/s/:.*/: ${global_sample_size}/" \
	-e "/num_train_this_partition/s/:.*/: ${local_sample_size}/" \
	"${global_data_libsvm_meta_file}" \
	> "${local_data_libsvm_meta_file}"

}

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

nb_workers=${#petuum_workers_specification_list[@]}

#
# generating
# - ${tmp_dir}/libsvm_access_log.txt
# - ${tmp_dir}/libsvm_access_log.txt.meta
# - ${tmp_dir}/labels.txt
"${HERE}/generateMLRLearningData.sh" ${tmp_dir}/libsvm_access_log.txt -l ${tmp_dir}/labels.txt

#
# SWITCH between single worker and distributed learning with _multiple workers_ and _split input data_
#

if [ ${nb_workers} -ge 2 ]
then
    # Distributed version
    partitioned_mode=true
else
    partitioned_mode=false
fi



if ${partitioned_mode}
then
    # Distributed version
    globalDataFormatToWorkerLocalDataFormat \
	"${tmp_dir}/libsvm_access_log.txt" \
	${nb_workers} \
	${PARTITION_DEFAULT_SIZE_IN_PARTITIONED_MODE} \
	"${tmp_dir}/libsvm_access_log.txt.${this_worker_index}"
	
    
    mlr_arg_global_data=false

else
    mlr_arg_global_data=true

fi


# TODO: which args should be parametrized

command='GLOG_logtostderr=true GLOG_v=-1 GLOG_minloglevel=0 \
"${MLR_MAIN}" \
   --num_comm_channels_per_client=1 \
   --staleness=2 \
   --client_id="${this_worker_index}" \
   --num_app_threads=1 \
   --num_clients=${nb_workers} \
   --use_weight_file=false --weight_file= \
   --num_batches_per_epoch=10 --num_epochs=40 \
   --output_file_prefix=${tmp_dir}/rez \
   --lr_decay_rate=0.99 --num_train_eval=10000 \
   --global_data=${mlr_arg_global_data} \
   --init_lr=0.01 \
   --num_test_eval=20 --perform_test=false --num_batches_per_eval=10 --lambda=0 \
   --hostfile=${tmp_dir}/localserver \
   --train_file=${tmp_dir}/libsvm_access_log.txt \
'

if ${dryrun}
then
    echo "${command}"
else
    eval "${command}"
fi

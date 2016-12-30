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
${squidGuard_cmd} > "${tmp_dir}/squidGuardClassifiedLogs.txt"

${python} "${squidGuardToSVM_py}" \
    --squidAccessLogFile "${tmp_dir}/access.log" \
    --squidGuardFile "${tmp_dir}/squidGuardClassifiedLogs.txt" \
    --libSVMFile "${tmp_dir}/access_libsvm.txt" \
    --squidGuardConf "${squidGuard_conf}" \
    --categoriesDump "${tmp_dir}/labels.txt"


exit 1

declare -a petuum_workers
petuum_workers_specification_table[0]="0 petuum-01"
# petuum_workers_specification_table[1]="1 petuum-02"

: ${petuum_interworker_tcp_port:=9999}
num_clients=${#petuum_workers[@]}
_last_petuum_workers_tab

build_worker_mlr_cmd () {

    worker_index="$1"
    worker_name="$2"

    worker_command=$( echo "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${worker_name} GLOG_logtostderr=true GLOG_v=-1 GLOG_minloglevel=0  /share/Petuum/bosen/app/mlr/bin/mlr_main --num_comm_channels_per_client=1 --hostfile=${tmp}/localserver --staleness=2 --client_id=0 --num_app_threads=1 --num_clients=${num_clients} --use_weight_file=false --weight_file= --num_batches_per_epoch=10 --num_epochs=40 --output_file_prefix=${tmp_dir}/rez --lr_decay_rate=0.99 --num_train_eval=10000 --global_data=true --init_lr=0.01 --train_file=${tmp_dir}/access_libsvm.txt --num_test_eval=20 --perform_test=false --num_batches_per_eval=10 --lambda=0" )

    echo "${worker_comman}"
}

# generate server file
(
    for worker_specification in petuum_workers_specification_table
    do
	echo ${worker_specification} | read worker_index worker_hostname
	echo ${worker_index} ${worker_hostname} ${petuum_interworker_tcp_port}
    done
) > ${tmp}/localserver

# lauch all workers


    








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

#! /bin/bash

HERE=`dirname "$0"`

libSvmLearningFile="$1"
nb_workers="$2"
worker_libSvmLearningFile_prefix="$3"

libsvm_meta_source_file="${libSvmLearningFile}.meta"

: ${_max_workers:=20}

Usage ()
{
    msg="$1"

    echo "${msg}" 1>&2
    echo "Usage: <cmd> <libSvm learning file name> <amount of wanted workers> [<generated libSvm learning file name prefix>]" 1>&2
    exit 1
}

: ${tmp_dir:="/tmp/ZZ"}

if [ ! -r "${libSvmLearningFile}" ]
then
    Usage "Cannot read LIBSvm file: \"${libSvmLearningFile}\""
fi

if [ ! -r "${libsvm_meta_source_file}" ]
then
    Usage "Missing associated meta file for \"${libsvm_meta_source_file}\""
fi

if [ -z "${nb_workers}" ]
then
    Usage "Missing anount of wanted workers"
fi


if [ -z "${nb_workers##[0-9]*}" ]
then
    if [ ${nb_workers} -le 0 -o ${nb_workers} -gt "${_max_workers}" ]
    then
	Usage "\"${nb_workers}\" should be in range [2..${_max_workers}]" 1>&2
    fi
else
    Usage "\"${nb_workers}\" should be an integer value" 1>&2
fi


if [ -z "${worker_libSvmLearningFile_prefix}" ]
then
    worker_libSvmLearningFile_prefix="${libSvmLearningFile}.partition"
fi


function ShuffleFile ()
{
    file_to_shuffle="$1"

    cp "${file_to_shuffle}" "${tmp_dir}/to_shuffle"
    shuf --output="${file_to_shuffle}" "${tmp_dir}/to_shuffle"
}



mkdir -m 777 -p "${tmp_dir}"

cp "${libSvmLearningFile}" "${tmp_dir}/src.libsvm"
cp "${libSvmLearningFile}.meta" "${tmp_dir}/src.libsvm.meta"

ShuffleFile "${tmp_dir}/src.libsvm"

split --suffix-length=1 --numeric-suffixes=1 --number=l/${nb_workers} "${tmp_dir}/src.libsvm" "${tmp_dir}/src.libsvm.part."

for part_number in `seq 1 ${nb_workers}`
do
    # generated "meta" files for each part

    # recompute "num_train_this_partition"
    nb_samples=`wc -l < "${tmp_dir}/src.libsvm.part.${part_number}"`

    (
	# remove "num_train_this_partition" if present
	grep -v 'num_train_this_partition:' "${tmp_dir}/src.libsvm.meta"

	echo "num_train_this_partition: ${nb_samples}"
    ) > "${tmp_dir}/src.libsvm.part.${part_number}.meta"
done

#
# produce target files
#

for part_number in `seq 1 ${nb_workers}`
do
    petuum_worker_id=$(( part_number - 1 ))
    cp "${tmp_dir}/src.libsvm.part.${part_number}" "${worker_libSvmLearningFile_prefix}${petuum_worker_id}"
    cp "${tmp_dir}/src.libsvm.part.${part_number}.meta" "${worker_libSvmLearningFile_prefix}${petuum_worker_id}.meta"
done

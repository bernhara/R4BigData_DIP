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

if [ ! -r "${fullKhiopsSrcFile}" ]
then
    Usage "I need a Khiops formated input file"
fi

if [ ! -r "${libsvm_meta_source_file}" ]
then
    Usage "Missing associated meta file for \"${libsvm_meta_source_file}\""
fi

if [ -z "${nb_workers}" ]
then
    Usage "Missing anount of wanted workers"
fi


if [ -z "${nb_workers##+([0-9])}" ]
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
    sample_output_file_prefix="${libSvmLearningFile}.partial_data."
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

for worker_index in `seq 2 ${nb_workers}`
do
    # generated "meta" files for each part
    cp "${tmp_dir}/src.libsvm.meta" "${tmp_dir}/tmp_meta"

    # recompute "num_train_this_partition"
    nb_samples=`wc -l "${tmp_dir}/src.libsvm.part.${worker_index}"`

    (
	# remove "num_train_this_partition" if present
	sed -e \
	    '/num_train_this_partition:/d' \
	"${tmp_dir}/src.libsvm.part"

	echo "num_train_this_partition: ${nb_samples}"
    ) > "${tmp_dir}/src.libsvm.part.${worker_index}.meta"
done

#
# produce target files
#

for worker_index in `seq 2 ${nb_workers}`
do
    cp "${tmp_dir}/src.libsvm.part.${worker_index}" "${sample_output_file_prefix}.${worker_index}"
    cp "${tmp_dir}/src.libsvm.part.${worker_index}.meta" "${sample_output_file_prefix}.${worker_index}.meta"
done

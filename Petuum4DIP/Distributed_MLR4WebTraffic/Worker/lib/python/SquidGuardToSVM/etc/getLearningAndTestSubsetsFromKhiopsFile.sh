#! /bin/bash

HERE=`dirname "$0"`

khiopsSrcFile="$1"
sample_output_file_prefix="$2"


#
# declare amount of data
#

: ${proportion_for_learning=5} # 1 tenth
: ${proportion_for_test_during_learning=3} # 7 tenth
: ${proportion_to_predict_on=2} # 2 tenth

: ${splitter:="${HERE}/splitKhiopsSampleFile.sh"}

if [ -z "${nb_splits}" ]
then
    nb_splits=1
fi

: ${tmp_dir:="/tmp/ZZ"}

if [ ! -r "${khiopsSrcFile}" ]
then
    echo "I need a Khiops formated input file" 1>&2
    exit 1
fi

if [ -z "${sample_output_file_prefix}" ]
then
    sample_output_file_prefix="${khiopsSrcFile}.LEARN_AND_TEST.}"
fi

mkdir -m 777 -p "${tmp_dir}"

#
# Get header
#

khiopsSrcFileHead=`head -1 "${khiopsSrcFile}"`

#
# compute the amount of splits we have to generate
#

nb_quantums=$(( ${proportion_for_learning} + ${proportion_for_test_during_learning} + ${proportion_to_predict_on} ))

#
# split into quantums
#

"${splitter}" "${khiopsSrcFile}" $nb_splits "${tmp_dir}/quantums."

#
# assemble the needed amount of quantums to get the correct proportion
#

function getTheNthQuantumsContent ()
{
    first_quantum_index=$1
    last_quantun_index$2

    shift 2

    file_name_list="$@"

    echo "${khiopsSrcFileHead}"
    for quantum_index in `seq ${first_quantum_index} ${last_quantun_index}`
    do
	# get content of that quantum
	sed -e \
	    '1d' \
	    "${file_name_list[$quantum_index]}"
    done
}

quantum_file_list=$( ls -1 ${tmp_dir}/quantums.* )

first_quantum_index=1
last_quantun_index=$(( ${first_quantum_index} + ${proportion_for_learning} ))

getTheNthQuantumsContent ${first_quantum_index} ${last_quantun_index} ${quantum_file_list} \
   >  "${sample_output_file_prefix}.PART_FOR_LEARNING"

first_quantum_index=${last_quantun_index}
last_quantun_index=$(( ${first_quantum_index} + ${proportion_for_test_during_learning} ))

getTheNthQuantumsContent ${first_quantum_index} ${last_quantun_index} ${quantum_file_list} \
   >  "${sample_output_file_prefix}.PART_FOR_TEST_DURING_LEARNING"

first_quantum_index=${last_quantun_index}
last_quantun_index=$(( ${first_quantum_index} + ${proportion_to_predict_on} ))

getTheNthQuantumsContent ${first_quantum_index} ${last_quantun_index} ${quantum_file_list} \
   >  "${sample_output_file_prefix}.PART_TO_PREDICT_ON"

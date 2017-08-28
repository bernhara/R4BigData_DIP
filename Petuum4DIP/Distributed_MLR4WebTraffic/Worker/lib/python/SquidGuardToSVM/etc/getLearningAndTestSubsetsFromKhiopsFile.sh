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

function zeroPadIntValue ()
{
    string_to_pad_with_zero="$1"

    tmp="00000${string_to_pad_with_zero}"
    padded_string="${tmp: -3}"

    echo "${padded_string}"
}


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

"${splitter}" "${khiopsSrcFile}" $nb_quantums "${tmp_dir}/quantums."

#
# assemble the needed amount of quantums to get the correct proportion
#

function getTheNthQuantumsContent ()
{
    first_quantum_index=$1
    last_quantum_index$2
    split_filename_prefix="$3"

    echo "${khiopsSrcFileHead}"
    for quantum_index in `seq ${first_quantum_index} ${last_quantum_index}`
    do
	# get content of that quantum
	split_suffix=`zeroPadIntValue $quantum_index`
	sed -e \
	    '1d' \
	    "${split_filename_prefix}${split_suffix}"
    done
}

first_quantum_index=1
last_quantum_index=$(( ${first_quantum_index} + ${proportion_for_learning} - 1 ))

getTheNthQuantumsContent ${first_quantum_index} ${last_quantum_index} "${tmp_dir}/quantums." \
   >  "${sample_output_file_prefix}.PART_FOR_LEARNING"

first_quantum_index=$(( ${last_quantum_index} + 1 ))
last_quantum_index=$(( ${first_quantum_index} + ${proportion_for_test_during_learning} - 1 ))

getTheNthQuantumsContent ${first_quantum_index} ${last_quantum_index} "${tmp_dir}/quantums." \
   >  "${sample_output_file_prefix}.PART_FOR_TEST_DURING_LEARNING"

first_quantum_index=$(( ${last_quantum_index} + 1 ))
last_quantum_index=$(( ${first_quantum_index} + ${proportion_to_predict_on} - 1 ))

getTheNthQuantumsContent ${first_quantum_index} ${last_quantum_index} "${tmp_dir}/quantums." \
   >  "${sample_output_file_prefix}.PART_TO_PREDICT_ON"

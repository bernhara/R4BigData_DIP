#! /bin/bash

HERE=`dirname "$0"`

khiopsSrcFile="$1"
sample_output_file_prefix="$2"

shift 2

slices_size_list="$@"


: ${splitter:="${HERE}/splitEqualyKhiopsSampleFile.sh"}

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

if [ -z "${slices_size_list}" ]
then
    echo "I need a slice size specification" 1>&2
    exit 1
fi

for slice_size in ${slices_size_list}
do
    if [ -z "${varname##+([0-9])}" ]
    then
	if [ ${slice_size} -le 0 -o ${slice_size} -gt 20 ]
	then
	    echo "Slice specification out of range" 1>&2
	    exit 1
	fi
    else
	echo "Slice specification must be an integer" 1>&2
	exit 1
    fi
done
    

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

nb_quantums=0
for slice_size in ${slices_size_list}
do
    nb_quantums=$(( ${nb_quantums} + ${slice_size} ))
done

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
    last_quantum_index=$2
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

last_quantum_index=0

for slice_size in ${slices_size_list}
do
    first_quantum_index=$(( ${last_quantum_index} + 1 ))
    last_quantum_index=$(( ${first_quantum_index} + ${slice_size} - 1 ))

    getTheNthQuantumsContent ${first_quantum_index} ${last_quantum_index} "${tmp_dir}/quantums." \
			     >  "${sample_output_file_prefix}.slice.${slice_size}"
done

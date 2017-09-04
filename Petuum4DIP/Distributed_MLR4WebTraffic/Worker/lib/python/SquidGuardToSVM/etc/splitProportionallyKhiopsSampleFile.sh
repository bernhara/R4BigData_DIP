#! /bin/bash

HERE=`dirname "$0"`

khiopsSrcFile="$1"
sample_output_file_prefix="$2"

shift 2

slices_size_list="$@"


: ${splitter:="${HERE}/splitEqualyKhiopsSampleFile.sh"}

: ${tmp_dir:="/tmp/ZZ"}

Usage ()
{
    msg="$1"

    echo "${msg}" 1>&2
    echo "Usage: <cmd> <Khiops input format compliant file (csv)> <generated samples output prefix path> <slice size> [<slice size>...] " 1>&2
    echo "	A slice sice is an integer. Ex: 3 5 2 will generate 3 files containing respectively 30%, 50% and 20% of the input file" 1>&2
    echo "	The content of the file is randomly shuffled before being split" 1>&2
    exit 1
}

if [ ! -r "${khiopsSrcFile}" ]
then
    Usage "I need a Khiops formated input file"
fi

if [ -z "${slices_size_list}" ]
then
    Usage "I need a slice size specification"
fi

for slice_size in ${slices_size_list}
do
    if [ -n "${slice_size}" -a -z "${slice_size##[0-9]*}" ]
    then
	if [ ${slice_size} -le 0 -o ${slice_size} -gt 20 ]
	then
	    Usage "Slice specification out of range"
	fi
    else
	Usage "Slice specification must be an integer"
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

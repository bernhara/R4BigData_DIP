#! /bin/bash

HERE=`dirname "$0"`

fullKhiopsSrcFile="$1"
column_title_to_balance="$2"
nb_splits="$3"

sample_output_file_prefix="$4"

: ${tmp_dir:="/tmp/ZZ"}

Usage ()
{
    msg="$1"

    echo "${msg}" 1>&2
    echo "Usage: <cmd> <Khiops input format compliant file (csv)> <column title to balance to splitted files> <number of equal sized splits of input file> [<output file path prefix>]" 1>&2
    echo "	<output file path prefix> is not defaults to \"<Khiops input file name>.SAMPLE.\"" 1>&2
    exit 1
}

if [ ! -r "${fullKhiopsSrcFile}" ]
then
    Usage "I need a Khiops formated input file"
fi

if [ -n "${nb_splits}" -a -z "${nb_splits##[0-9]*}" ]
then
    :
else
    Usage "${nb_splits}: wrong numbre for Slice specification out of range"
fi

if [ -z "${sample_output_file_prefix}" ]
then
    sample_output_file_prefix="${fullKhiopsSrcFile}.SAMPLE.}"
fi

function ShuffleFile ()
{
    file_to_shuffle="$1"

    cp "${file_to_shuffle}" "${tmp_dir}/to_shuffle"
    shuf --output="${file_to_shuffle}" "${tmp_dir}/to_shuffle"
}

function zeroPadIntValue ()
{
    string_to_pad_with_zero="$1"

    tmp="00000${string_to_pad_with_zero}"
    padded_string="${tmp: -3}"

    echo "${padded_string}"
}

mkdir -m 777 -p "${tmp_dir}"

fullKhiopsSrcFileBasename=`basename "${fullKhiopsSrcFile}"`

#
# Get header
#

fullKhiopsSrcFileHead=`head -1 "${fullKhiopsSrcFile}"`

#
# Generate file containing the body only
#

bodyFile="${tmp_dir}/body"

sed -e \
    '1d' \
    "${fullKhiopsSrcFile}" > "${bodyFile}"

#
# Seperate classes
#

# ... compute the label list of the column to distribube equaliy

column_index_to_balance=1

for column_title in ${fullKhiopsSrcFileHead} "_COLUMN_TITLE_NOT_FOUND_"
do
    if [ "${column_title}" = "${column_title_to_balance}" ]
    then
	break
    fi
    (( column_index_to_balance++ ))
done

if [ "${column_title}" = "_COLUMN_TITLE_NOT_FOUND_" ]
then
    Usage "${column_title_to_balance} not found in the list of column titles"
fi

label_list=$(
    cut -f${column_index_to_balance} "${bodyFile}" | \
	sort -u
)

for label in ${label_list}
do
    grep "${label}" "${bodyFile}" > "${tmp_dir}/split.ONLY.${label}"
done

#
# Shuffle each file
#

for label in ${label_list}
do
    ShuffleFile "${tmp_dir}/split.ONLY.${label}"
done

#
# Split each seperate file
#

for label in ${label_list}
do
    split --suffix-length=3 --numeric-suffixes=1 --number=l/${nb_splits} "${tmp_dir}/split.ONLY.${label}" "${tmp_dir}/split.ONLY.${label}."
done

#
# create the samples
#

# should place on each split an equivalent proportion on each ONLY file.

for i in `seq 1 $nb_splits`
do

    split_suffix=`zeroPadIntValue $i`
    (
	echo "${fullKhiopsSrcFileHead}"

	for label in ${label_list}
	do
	    cat "${tmp_dir}/split.ONLY.${label}.$split_suffix"
	done
    ) > "${sample_output_file_prefix}$split_suffix"
done



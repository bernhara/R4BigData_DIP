#! /bin/bash

HERE=`dirname "$0"`

fullLibsvmSrcFile="$1"
nb_splits="$2"

sample_output_file_prefix="$3"

: ${tmp_dir:="/tmp/ZZ"}

Usage ()
{
    msg="$1"

    echo "${msg}" 1>&2
    echo "Usage: <cmd> <Libsvm input format compliant file (csv)> <column title to balance to splitted files> <number of equal sized splits of input file> [<output file path prefix>]" 1>&2
    echo "	<output file path prefix> is not defaults to \"<Libsvm input file name>.SAMPLE.\"" 1>&2
    exit 1
}

if [ ! -r "${fullLibsvmSrcFile}" ]
then
    Usage "I need a Libsvm formated input file"
fi

if [ -n "${nb_splits}" -a -z "${nb_splits##[0-9]*}" ]
then
    :
else
    Usage "${nb_splits}: wrong numbre for Slice specification out of range"
fi

if [ -z "${sample_output_file_prefix}" ]
then
    sample_output_file_prefix="${fullLibsvmSrcFile}.SAMPLE.}"
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

fullLibsvmSrcFileBasename=`basename "${fullLibsvmSrcFile}"`

#
# Remove blank lines
#
grep -v '^[[:space:]]*$' "${fullLibsvmSrcFile}" > "${tmp_dir}/input_file_without_blank_lines"


#
# Generate file containing the body only
#

bodyFile="${tmp_dir}/body"

cat "${fullLibsvmSrcFile}" \
    "${tmp_dir}/input_file_without_blank_lines" > "${bodyFile}"

#
# Seperate classes
#

# ... compute the label list of the column to distribube equaliy

label_list=$(
    cut '-d ' -f1 "${bodyFile}" | \
	sort -u
)

# ... generate a separate file for each label

for label in ${label_list}
do
    grep "^${label} " "${bodyFile}" > "${tmp_dir}/split.ONLY.${label}"
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
	echo "${fullLibsvmSrcFileHead}"

	for label in ${label_list}
	do
	    cat "${tmp_dir}/split.ONLY.${label}.$split_suffix"
	done
    ) > "${sample_output_file_prefix}$split_suffix"
done

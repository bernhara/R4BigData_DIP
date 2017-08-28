#! /bin/bash

HERE=`dirname "$0"`

fullKhiopsSrcFile="$1"
nb_splits="$2"

sample_output_file_prefix="$3"

if [ -z "${nb_splits}" ]
then
    nb_splits=1
fi


: ${label_list="EDIBLE POISONOUS"}
: ${tmp_dir:="/tmp/ZZ"}

if [ ! -r "${fullKhiopsSrcFile}" ]
then
    echo "I need a Khiops formated input file" 1>&2
    exit 1
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



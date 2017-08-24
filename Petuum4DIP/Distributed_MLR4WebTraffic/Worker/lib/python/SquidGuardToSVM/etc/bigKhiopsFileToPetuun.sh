#! /bin/bash

HERE=`dirname "$0"`

fullKhiopsSrcFile="$1"

: ${label_list="EDIBLE POISONOUS"}
: ${tmp_dir:="/tmp/ZZ"}

if [ ! -r "${fullKhiopsSrcFile}" ]
then
    echo "I need a Khiops formated input file" 1>&2
    exit 1
fi

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
    grep "${label}" "${bodyFile}" > "${tmp_dir}/${fullKhiopsSrcFileBasename}.ONLY.${label}"
done

function spltAndGenerateLearnTestValidateFiles ()
{
    #
    # count the label distribution
    #

    src_file_prefix="$1"
    dst_file_prefix="$2"
    nb_splits=$3

    for label in ${label_list}
    do
	in_file="${file_prefix}.${label}"
	count=`wc -l "${in_file}"`
	split_size=$(( $count / $nb_split ))

	split --numeric-suffixes=1 --number=l/${nb_split} "${in_file}" "${dst_file_prefix}.${label}."
    done

}








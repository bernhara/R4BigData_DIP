#! /bin/bash

HERE=`dirname "$0"`

fullKhiopsSrcFile="$1"
nb_splits="$2"

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

#
# Shuffle each file
#

for label in ${label_list}
do
    cp "${tmp_dir}/${fullKhiopsSrcFileBasename}.ONLY.${label}" "${tmp_dir}/to_shuffle"
    shuf "${tmp_dir}/to_shuffle" > "${tmp_dir}/${fullKhiopsSrcFileBasename}.ONLY.${label}"
done

#
# Split each seperate file
#

for label in ${label_list}
do
    split --suffix-length=1 --numeric-suffixes=1 --number=l/${nb_splits} "${tmp_dir}/${fullKhiopsSrcFileBasename}.ONLY.${label}" "${tmp_dir}/${fullKhiopsSrcFileBasename}.ONLY.${label}."
done

#
# create the samples
#

# should place on each split an equivalent proportion on each ONLY file.

for i in `seq 1 $nb_splits`
do
    (
	for label in ${label_list}
	do
	    cat "${tmp_dir}/${fullKhiopsSrcFileBasename}.ONLY.${label}.$i"
	done
    ) > "${tmp_dir}/${fullKhiopsSrcFileBasename}.SAMPLE.$i"
done



#! /bin/bash

HERE=`dirname $0`
CMD=`basename $0`

ARGarray=( "$@" )

if [ -r "${HERE}/${CMD}-config" ]
then
    . "${HERE}/${CMD}-config"
fi

: ${BLACKLIST_DIR:="${HERE}"}
: ${SHALLALIST_BLACKLIST_DIR:="${BLACKLIST_DIR}/BL"}
: ${SHALLALIST_SRC_ARCHIVE:="${HERE}/shallalist.tar.gz"}

#
# Manage tmp storage

: ${remove_tmp:=true}
: ${tmp_dir:=`mktemp -u -p "${HERE}/tmp"`}

if ${remove_tmp}
then
    trap 'rm -rf "${tmp_dir}"' 0
fi

# import_logs_dir is supposed to exist
mkdir -p "${tmp_dir}"

######################################################################

#
# rebuild Black list folder and database from shallalist obtained from http://www.shallalist.de/Downloads/shallalist.tar.gz
#

if [ -d "${SHALLALIST_BLACKLIST_DIR}" ]
then
    mv "${SHALLALIST_BLACKLIST_DIR}" "${tmp_dir}"
fi
mkdir -p "${BLACKLIST_DIR}"
tar zxf "${SHALLALIST_SRC_ARCHIVE}" -C "${BLACKLIST_DIR}"

classe_dirs=`
	cd "${SHALLALIST_BLACKLIST_DIR}" >/dev/null
#	echo */
	find . -type d
`

categories=""

for class_dir in ${classe_dirs}
do
    # exluded paths

    case "${class_dir}" in
	"." )
	    # skip, got next
	    continue
	    ;;
	*)
	    ;;
    esac

    category="${class_dir%/}"
    category="${category#./}"
    categories="${categories} ${category}"
    
done

dbhome=$(realpath "${SHALLALIST_BLACKLIST_DIR}")

echo "dbhome ${dbhome}"
echo "logdir /tmp"

for category in ${categories}
do
    if [ -f "${SHALLALIST_BLACKLIST_DIR}/${category}/domains" ]
    then
	domains_clause="domainlist ${category}/domains"
    fi
    if [ -f "${SHALLALIST_BLACKLIST_DIR}/${category}/urls" ]
    then
	urls_clause="urllist ${category}/urls"
    fi

    if [ -n "${domains_clause}" -o -n "${urls_clause}" ]
    then
	printf "dest %s {\n\t%s\n\t%s\n}\n\n" "${category}" "${urls_clause}" "${domains_clause}"
    fi
done

echo "acl {"
echo "   default {"
echo -n "      pass "
for category in ${categories}
do
    echo -n " !${category}"
done
echo " none"
echo "      redirect clientaddr=%a&clientname=%n&clientuser=%i&clientgroup=%s&targetgroup=%t&url=%u"
echo "   }"
echo "}"

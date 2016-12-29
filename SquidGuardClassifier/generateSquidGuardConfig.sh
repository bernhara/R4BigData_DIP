#! /bin/bash

: ${BLACKLIST_DIR:=BL}

classe_dirs=`
	cd "${BLACKLIST_DIR}" >/dev/null
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

dbhome=$(realpath "${BLACKLIST_DIR}")

echo "dbhome ${dbhome}"
echo "logdir /tmp"

for category in ${categories}
do
    if [ -f "${BLACKLIST_DIR}/${category}/domains" ]
    then
	domains_clause="domainlist ${category}/domains"
    fi
    if [ -f "${BLACKLIST_DIR}/${category}/urls" ]
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

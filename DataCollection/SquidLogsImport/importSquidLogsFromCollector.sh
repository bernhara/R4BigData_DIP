#! /bin/bash

HERE=`dirname $0`
CMD=`basename $0`

if [ -r "${HERE}/${CMD}-config" ]
then
    . "${HERE}/${CMD}-config"
fi

#
# script must be run here (for ssh config path)
#
: ${import_logs_dir:=${HERE}/ClonedLogs/imported}

: ${collector_ssh_remote_host_spec:="log-collector-wan"}

: ${ssh_verbose_flag:=""}
: ${SSH_CONFIG_FILE:="${HERE}/ssh-config"}
: ${SSH_PRIVATE_KEY_FILE:="${HERE}/ssh-key-to-s-proxetnet"}
: ${ssh_command:=ssh ${ssh_verbose_flag} -F "${SSH_CONFIG_FILE}" -i "${SSH_PRIVATE_KEY_FILE}"}


# check if provided environment contains the required information

if [ -z "${my_name}" ]
then
    echo "ERROR: shell variable \"my_name\" undefinded. See ${HERE}/${CMD}-config file." 1>&2
    exit 1
fi

if [ -z "${remote_source_dir}" ]
then
    echo "ERROR: shell variable \"remote_source_dir\" undefined.
	You should provide an existing folder on logs collector (eg. using the $HERE/myId.sh)" 1>&2
    exit 1
fi

date

mkdir -p "${import_logs_dir}"

chmod go-rwx ${HERE}/ssh-key-*

set -vx
export SSH_CONFIG_FILE
export SSH_PRIVATE_KEY_FILE
rsync -vv -a -e "${ssh_command}" ${collector_ssh_remote_host_spec}:${remote_source_dir} ${import_logs_dir}
set +vx

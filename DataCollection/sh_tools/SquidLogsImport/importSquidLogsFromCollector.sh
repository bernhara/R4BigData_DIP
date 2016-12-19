#! /bin/bash

HERE=`dirname $0`
CMD=`basename $0`

#
# script must be run here (for ssh config path)
#
cd "${HERE}"


: ${stdout_log_file:="${CMD}.stdout.log"}
: ${stderr_log_file:="${CMD}.stderr.log"}


: ${redirect_output:=true}

: ${import_logs_dir:=ClonedLogs}

: ${collector_ssh_remote_host_spec:="log-collector-wan"}

: ${ssh_verbose_flag:=""}
: ${ssh_command:=ssh ${ssh_verbose_flag} -F ssh-config}

if ${redirect_output}
then
    exec 1>"${stdout_log_file}" 2>"${stderr_log_file}"
fi

if [ -r "myId.sh" ]
then
   # to prevent bad X flag
   chmod +x "myId.sh"

   . ./myId.sh
fi

# check if provided environment contains the required information
if [ -z "${squid_host_dns_name}" ]
then
    echo "ERROR: shell variable \"squid_host_dns_name\" undefined.
	You should provide a known name of a known squid collector (eg. using the $HERE/myId.sh)" 1>&2
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

chmod go-rwx ssh-key-*

rsync -a -v -z -e "${ssh_command}" ${collector_ssh_remote_host_spec}:${remote_source_dir} ${import_logs_dir}

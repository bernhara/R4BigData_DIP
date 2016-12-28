#! /bin/bash

awk '
    $6 == "POST" {print $7" "$3"/ - - "$6}
    $6 == "GET" {print $7" "$3"/ - - "$6}
    $6 == "CONNECT" {print "https://"$7" "$3"/ - - GET"}
'

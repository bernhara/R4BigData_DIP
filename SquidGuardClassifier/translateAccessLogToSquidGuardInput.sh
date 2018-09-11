#! /bin/bash

# -*- mode: awk -*-

awk '

{
    gsub ("%0A", "_0A_")
}

{
    matched=0
}

$6 == "POST" {
    print $7" "$3"/ - - "$6; matched=1
}
$6 == "GET" {
    print $7" "$3"/ - - "$6; matched=1
}
$6 == "PROPFIND" {
    print $7" "$3"/ - - "$6; matched=1
}
$6 == "HEAD" {
    print $7" "$3"/ - - "$6; matched=1
}
$6 == "OPTIONS" {
    print $7" "$3"/ - - "$6; matched=1
}
$6 == "REPORT" {
    print $7" "$3"/ - - "$6; matched=1
}
$6 == "CONNECT" {
    print "https://"$7" "$3"/ - - GET"; matched=1
}
$6 == "NONE" {
    print "http://_bad_request_ "$3"/ - - GET"; matched=1
}

matched==0 {
    print "http://_bad_input_log_ "$3"/ - - GET"; matched=1
}
'

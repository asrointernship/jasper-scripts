#!/bin/bash

if [ "$1" = "" ]; then
    echo -n "Everything will be backed up. Are you sure?(y/n) "
    read ok
    if [ "$ok" = "y" ]; then
        mongodump -d socialmap -o db_backup/
    else
        echo "Nothing was backed up."
    fi
else
    echo -n "$1 will be backed up. Are you sure?(y/n) "
    read ok
    if [ "$ok" = "y" ]; then
        mongodump -d socialmap -c $1 -o db_backup/
    else
        echo "Nothing was backed up."
    fi
fi

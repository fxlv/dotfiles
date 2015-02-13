#!/bin/bash

cat default_config > ssh_config
for hostsfile in *.hosts
do  
    if file $hostsfile|grep -q ASCII; then
        echo "Adding $hostsfile to ssh_config"
        cat $hostsfile >> ssh_config
        chmod 640 ssh_config
    else
        echo "Skipping non-decrypted file $hostsfile"
    fi
done

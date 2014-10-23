#!/bin/bash
cd ../ssh
if [ ! -e config ]; then
    echo "Decrypting ssh_config file"
    gpg -o config -d config.gpg
fi
cd -
ansible-playbook -i hosts deploy.yml

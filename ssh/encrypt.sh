#!/bin/bash
# encrypt with 'secrets' pub key 
if gpg --default-recipient secrets -e config; then
    rm -v config
else
    echo "Encryption somehow failed"
fi

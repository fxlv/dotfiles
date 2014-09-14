#!/bin/bash

function symlink {
    dotfile_source=$1
    dotfile_destination=$2
    if [ -L $dotfile_destination ]; then
        echo "Destination file $dotfile_destination already exists, skipping."
    else
        echo "Symlinking $dotfile_source -> $dotfile_destination"
        ln -sv ${PWD}/${dotfile_source} ${dotfile_destination}
    fi
}

# assume linux by default
flavor=linux

if [ "$(uname -s)" == "Darwin" ];then
    echo "Installing dotfiles for OSX"
    flavor=osx
fi

cd $flavor
# ssh_config contains some hostnames which I'd prefer not to share
gpg -o ssh_config -d ssh_config.gpg
symlink bash_profile ${HOME}/.bash_profile
symlink Xmodmap ${HOME}/.Xmodmap
symlink ssh_config ${HOME}/.ssh/config
cd ..

echo "All done"

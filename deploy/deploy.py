#!/usr/bin/env python
import os
import sys

cwd = os.getcwd()
dotfiles_directory = os.path.dirname(cwd)
home = os.environ.get("HOME")

def deploy_file(src, dst, name=None):
    if home not in dst:
        print "Appending {0} to {1}".format(home, dst) 
        dst = "{0}/{1}".format(home, dst)
    # prepend 'dotfiles_directory' to the dotfile source
    src = "{0}/{1}".format(dotfiles_directory, src)
    if os.path.exists(dst):
        if os.path.islink(dst):
            if os.readlink(dst) == src:
                print "{0} is already correclty symlinked".format(dst)
        print "Skipping {0} as it already exists".format(dst)
        return False
    print "Symlinking {0} -> {1}".format(src, dst)
    os.symlink(src, dst)


if __name__ == "__main__":
    deploy_file("vim/vimrc",".vimrc")






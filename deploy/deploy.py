#!/usr/bin/env python
#
#
import os
from platform import uname
import sys

uname = uname()[0]
if uname == "Darwin":
    platform = "OSX"
elif uname == "Linux":
    platform = "Linux"
else:
    print "Unsupported platform"
    sys.exit(1)

print "Platform:", platform


class Dotfile:

    def __init__(self, name, src, dst, compile_dotfile_script=None):
        self.name = name
        self.src = src
        self.dst = dst
        cwd = os.getcwd()
        self.dotfiles_directory = os.path.dirname(cwd)
        self.home = os.environ.get("HOME")
        # prepend 'dotfiles_directory' to the dotfile source
        self.src = "{0}/{1}".format(self.dotfiles_directory, self.src)
        self.debug = True
        self.compile_dotfile_script = compile_dotfile_script

    def compile_dotfile(self):
        if self.debug: 
            print "Compiling {0} dotfile by executing {1}".format(self.name, self.compile_dotfile_script)
        dotfile_path = os.path.dirname(self.src)
        os.chdir(dotfile_path)
        compile_script = "./{0}".format(self.compile_dotfile_script)
        os.system(compile_script)

    def __repr__(self):
        return "Dotfile: {0}".format(self.name)
 
    def __str__(self):
        return self.name
   
    def exists(self):
        "Check if the destination file exists"
        if os.path.exists(self.dst):
            return True
        return False

    def is_deployed(self):
        "Check if the dotfile is correctly symlinked"
        if os.path.exists(self.dst):
            if os.path.islink(self.dst):
                if os.readlink(self.dst) == self.src:
                    print "Valid link: {0} -> {1}".format(self.src, self.dst)
                    return True
                else:
                    print "Invalid link for {0}".format(self.dst)
                    return False

            else:
                print "The file {0} exists but it is not a symlink".format(self.dst)
                return False
        else:
            return False


    def deploy(self):
        if self.compile_dotfile_script:
            self.compile_dotfile()
        # we can handle both relative and absolute path in home directory
        if self.home not in self.dst:
            if self.debug: print "DEBUG: Appending {0} to {1}".format(self.home, self.dst)
            self.dst = "{0}/{1}".format(self.home, self.dst)
        # check if the dotfile is already deployed
        if self.is_deployed():
            print "Dotfile {0} is already deployed.".format(self.name)
            return
        # if the destination file already exists but it is not
        # our symlink then print out a warning to the user and skip it
        if self.exists():
            print "File {0} already exists but it is not the correct dotfile".format(self.dst)
            print "Please remove it and re-run this script."
            print "Skipping {0}".format(self.name)
            return

        # finally symlink the dotfile
        print "Symlinking {0} -> {1}".format(self.src, self.dst)
        os.symlink(self.src, self.dst)

if __name__ == "__main__":
    vimrc = Dotfile("virmc", "vim/vimrc", ".vimrc")
    vimrc.deploy()
    ssh_config = Dotfile("ssh config", "ssh/ssh_config", ".ssh/config",
                         compile_dotfile_script="compile.sh")
    ssh_config.deploy()
    if platform == "OSX":
        xmodmap = Dotfile("Xmodmap", "osx/Xmodmap", ".Xmodmap")
        xmodmap.deploy()



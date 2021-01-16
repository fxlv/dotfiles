#!/usr/bin/env python
#
#
import os
from platform import uname
import sys


class Dotfile:
    def __init__(self, name, src, dst, compile_dotfile_script=None):
        self.name = name
        self.src = src
        self.dst = dst
        script_dir = os.path.dirname(os.path.realpath(__file__))
        self.dotfiles_directory = os.path.dirname(script_dir)
        self.home = os.environ.get("HOME")
        print "DEBUG: PRE self.src: {0}".format(self.src)
        print "DEBUG: PRE self.dst: {0}".format(self.dst)
        # prepend 'dotfiles_directory' to the dotfile source
        self.src = "{0}/{1}".format(self.dotfiles_directory, self.src)
        # we can handle both relative and absolute path in home directory
        if self.home not in self.dst:
            print "DEBUG: Appending {0} to {1}".format(self.home, self.dst)
            self.dst = "{0}/{1}".format(self.home, self.dst)
        self.dst_parent_dir = os.path.dirname(self.dst)
        self.debug = True
        self.compile_dotfile_script = compile_dotfile_script
        print "DEBUG: self.src: {0}".format(self.src)
        print "DEBUG: self.dst: {0}".format(self.dst)
        print "DEBUG: self.dst_parent_dir: {0}".format(self.dst_parent_dir)

    def compile_dotfile(self):
        if self.debug:
            msg = "Compiling {0} dotfile by executing {1}"
            print msg.format(self.name, self.compile_dotfile_script)
        dotfile_path = os.path.dirname(self.src)
        cur_dir = os.getcwd()
        os.chdir(dotfile_path)
        if os.path.exists(self.compile_dotfile_script):
            compile_script = "./{0}".format(self.compile_dotfile_script)
            os.system(compile_script)
        else:
            print "Warning"
            warn_msg = "Compile script {0} does not exist!"
            print warn_msg.format(self.compile_dotfile_script)
        # return to the original directory
        os.chdir(cur_dir)

    def __repr__(self):
        return "Dotfile: {0}".format(self.name)

    def __str__(self):
        return self.name

    def is_broken_link(self):
        """
        Return True for broken links.
        If file exists() reports False but lexists() reports True,
        then most likely this is a broken symlink
        """
        if not os.path.exists(self.dst):
            if os.path.lexists(self.dst):
                return True
        return False

    def exists(self):
        "Check if the destination file exists"
        if os.path.exists(self.dst):
            print "{} exists".format(self.dst)
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
                msg = "The file {0} exists but it is not a symlink"
                print msg.format(self.dst)
                return False
        else:
            return False

    def backup(self):
        "Back up the destination file if possible"
        backup_dst = "{0}.backup".format(self.dst)
        if os.path.exists(backup_dst):
            msg = "{0} already exists, cannot create a backup."
            print msg.format(backup_dst)
            return False
        if not os.path.isfile(self.dst):
            msg = "{0} is not a file, cannot create a backup"
            print msg.format(backup_dst)
            return False
        # proceed with backin up the file
        print "Backing up {0} -> {1}".format(self.dst, backup_dst)
        os.rename(self.dst, backup_dst)
        self.backup_dst = backup_dst
        return True

    def parent_dir_exists(self):
        if os.path.exists(self.dst_parent_dir):
            return True
        return False

    def create_parent_dir(self):
        print "DEBUG: creating parent dir {0}".format(self.dst_parent_dir)
        parent_of_parent = os.path.dirname(self.dst_parent_dir)
        if not os.path.exists(parent_of_parent):
            os.mkdir(parent_of_parent)
        os.mkdir(self.dst_parent_dir)

    def deploy(self):
        if not self.parent_dir_exists():
            self.create_parent_dir()
        if self.compile_dotfile_script:
            self.compile_dotfile()
        # check if the dotfile is already deployed
        if self.is_deployed():
            print "Dotfile {0} is already deployed.".format(self.name)
            return
        # if the destination file already exists but it is not
        # our symlink then print out a warning to the user and skip it
        if self.exists():
            if self.backup():
                print "Backup file {0} created".format(self.backup_dst)
            else:
                msg = "File {0} already exists "\
                      "but it is not the correct dotfile"
                print msg.format(self.dst)
                print "Backing up also failed."
                print "Please remove it and re-run this script."
                print "Skipping {0}".format(self.name)
                return

        else:
            if self.is_broken_link():
                print "Broken symlink found for {}".format(self.dst)
                os.unlink(self.dst)
        # finally symlink the dotfile
        print "Symlinking {0} -> {1}".format(self.src, self.dst)
        os.symlink(self.src, self.dst)


def main():
    uname_string = uname()[0]
    if uname_string == "Darwin":
        platform = "OSX"
    elif uname_string == "Linux":
        platform = "Linux"
    elif uname_string == "FreeBSD":
        platform = "FreeBSD"
    elif uname_string == "CYGWIN_NT-10.0-WOW":
        platform = "Cygwin"
    else:
        print "Unsupported platform"
        sys.exit(1)
    print "Platform:", platform
    curlrc = Dotfile("curlrc", "curl/curlrc", ".curlrc")
    curlrc.deploy()
    mostrc = Dotfile("mostrc", "most/mostrc", ".mostrc")
    mostrc.deploy()
    vimrc = Dotfile("vimrc", "vim/vimrc", ".vimrc")
    vimrc.deploy()
    screen = Dotfile("screen", "screen/screenrc", ".screenrc")
    screen.deploy()
    git = Dotfile("gitconfig", "git/gitconfig", ".gitconfig")
    git.deploy()
    bash_profile = Dotfile("bash_profile", "bash/bash_profile",
                           ".bash_profile")
    bash_profile.deploy()
    colors = Dotfile("colors", "bash/colors", ".colors")
    colors.deploy()
    functions = Dotfile("functions", "bash/functions", ".functions")
    functions.deploy()
    bashrc = Dotfile("bashrc", "bash/bashrc", ".bashrc")
    bashrc.deploy()
    bash_aliases = Dotfile("bash_aliases", "bash/bash_aliases",
                           ".bash_aliases")
    bash_aliases.deploy()
    ssh_config = Dotfile("ssh config",
                         "ssh/ssh_config",
                         ".ssh/config",
                         compile_dotfile_script="compile.sh")
    ssh_config.deploy()
    # Ansiblerc is the same on all platforms
    ansiblerc = Dotfile("ansiblerc", "bash/ansiblerc", ".ansiblerc")
    ansiblerc.deploy()
    # Tmux config is the same everywhere
    tmux = Dotfile("tmux", "tmux/tmux.conf", ".tmux.conf")
    tmux.deploy()
    tmux = Dotfile("tmuxp", "tmuxp/dev.yaml", ".tmuxp/dev.yaml")
    tmux.deploy()
    mc = Dotfile("mc", "mc/ini", ".config/mc/ini")
    mc.deploy()
    # OSX will have some specifics
    if platform == "OSX":
        xmodmap = Dotfile("Xmodmap", "osx/Xmodmap", ".Xmodmap")
        xmodmap.deploy()
        bash_mac = Dotfile("bash_mac", "bash/bash_mac", ".bash_mac")
        bash_mac.deploy()
        # I use powerline on OSX only, for now
        tmuxpowerline = Dotfile("tmuxpowerline",
                                "tmux/tmux.powerline.osx.conf",
                                ".tmux.powerline.osx.conf")
        tmuxpowerline.deploy()
    elif platform == "Linux" or platform == "FreeBSD":
        # on FreeBSD I use .xinitrc to start up x
        if platform == "FreeBSD":
            xinitrc = Dotfile("xinitrc", "x/xinitrc", ".xinitrc")
            xinitrc.deploy()


if __name__ == "__main__":
    main()

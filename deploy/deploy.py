#!/usr/bin/env python3
"""
Dotfiles deployment script

Deployments dotfiles by creating symlinks from the repository to the home directory.
Supports compilation of configuration files and automatic backups.
"""

import argparse
import os
import stat
import subprocess
import sys
from pathlib import Path
from platform import uname


class Dotfile:
    def __init__(self, name, src, dst, compile_dotfile_script=None, permissions=None, verbose=False, dry_run=False):
        self.name = name
        self.src = src
        self.dst = dst
        self.verbose = verbose
        self.dry_run = dry_run
        self.permissions = permissions
        
        script_dir = Path(__file__).parent.absolute()
        self.dotfiles_directory = script_dir.parent
        self.home = Path.home()
        
        # Convert to Path objects for better handling
        self.src = self.dotfiles_directory / self.src
        if not self.dst.startswith('/'):
            self.dst = self.home / self.dst
        else:
            self.dst = Path(self.dst)
            
        self.dst_parent_dir = self.dst.parent
        self.compile_dotfile_script = compile_dotfile_script
        
        if self.verbose:
            print(f"Dotfile {self.name}: {self.src} -> {self.dst}")

    def compile_dotfile(self):
        """Compile dotfile using specified script"""
        if self.verbose:
            print(f"Compiling {self.name} dotfile by executing {self.compile_dotfile_script}")
            
        if self.dry_run:
            print(f"[DRY RUN] Would compile {self.name} using {self.compile_dotfile_script}")
            return True
            
        dotfile_path = self.src.parent
        compile_script_path = dotfile_path / self.compile_dotfile_script
        
        if not compile_script_path.exists():
            print(f"Warning: Compile script {compile_script_path} does not exist!")
            return False
            
        try:
            result = subprocess.run(
                [str(compile_script_path)],
                cwd=dotfile_path,
                capture_output=True,
                text=True,
                check=True
            )
            if self.verbose and result.stdout:
                print(f"Compile output: {result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error compiling {self.name}: {e}")
            if e.stderr:
                print(f"Error output: {e.stderr}")
            return False

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
        return self.dst.is_symlink() and not self.dst.exists()

    def exists(self):
        "Check if the destination file exists"
        exists = self.dst.exists()
        if exists and self.verbose:
            print(f"{self.dst} exists")
        return exists

    def is_deployed(self):
        "Check if the dotfile is correctly symlinked"
        if not self.dst.exists():
            return False
            
        if not self.dst.is_symlink():
            if self.verbose:
                print(f"The file {self.dst} exists but it is not a symlink")
            return False
            
        try:
            actual_target = self.dst.readlink().resolve()
            expected_target = self.src.resolve()
            
            if actual_target == expected_target:
                if self.verbose:
                    print(f"Valid link: {self.src} -> {self.dst}")
                return True
            else:
                if self.verbose:
                    print(f"Invalid link for {self.dst}: points to {actual_target}, expected {expected_target}")
                return False
        except OSError as e:
            print(f"Error checking symlink {self.dst}: {e}")
            return False

    def backup(self):
        "Back up the destination file if possible"
        backup_dst = Path(f"{self.dst}.backup")
        
        if backup_dst.exists():
            print(f"{backup_dst} already exists, cannot create a backup.")
            return False
            
        if not self.dst.is_file():
            print(f"{self.dst} is not a file, cannot create a backup")
            return False
            
        if self.dry_run:
            print(f"[DRY RUN] Would backup {self.dst} -> {backup_dst}")
            return True
            
        try:
            print(f"Backing up {self.dst} -> {backup_dst}")
            self.dst.rename(backup_dst)
            self.backup_dst = backup_dst
            return True
        except OSError as e:
            print(f"Error creating backup: {e}")
            return False

    def parent_dir_exists(self):
        return self.dst_parent_dir.exists()

    def create_parent_dir(self):
        """Create parent directories with proper permissions"""
        if self.verbose:
            print(f"Creating parent directory {self.dst_parent_dir}")
            
        if self.dry_run:
            print(f"[DRY RUN] Would create directory {self.dst_parent_dir}")
            return True
            
        try:
            self.dst_parent_dir.mkdir(parents=True, exist_ok=True, mode=0o755)
            return True
        except OSError as e:
            print(f"Error creating directory {self.dst_parent_dir}: {e}")
            return False

    def set_permissions(self):
        """Set file permissions if specified"""
        if not self.permissions or self.dry_run:
            return True
            
        try:
            self.dst.chmod(self.permissions)
            if self.verbose:
                print(f"Set permissions {oct(self.permissions)} on {self.dst}")
            return True
        except OSError as e:
            print(f"Error setting permissions on {self.dst}: {e}")
            return False

    def deploy(self):
        """Deploy the dotfile by creating symlink"""
        # Validate source file exists
        if not self.src.exists():
            print(f"Error: Source file {self.src} does not exist")
            return False
            
        # Create parent directory if needed
        if not self.parent_dir_exists():
            if not self.create_parent_dir():
                return False
                
        # Compile dotfile if needed
        if self.compile_dotfile_script:
            if not self.compile_dotfile():
                print(f"Warning: Compilation failed for {self.name}")
                
        # Check if already deployed
        if self.is_deployed():
            if self.verbose:
                print(f"Dotfile {self.name} is already deployed.")
            self.set_permissions()
            return True
            
        # Handle existing files
        if self.exists():
            if not self.backup():
                print(f"File {self.dst} already exists but backup failed.")
                print(f"Please remove it manually and re-run. Skipping {self.name}")
                return False
        elif self.is_broken_link():
            print(f"Removing broken symlink: {self.dst}")
            if not self.dry_run:
                self.dst.unlink()
                
        # Create the symlink
        if self.dry_run:
            print(f"[DRY RUN] Would symlink {self.src} -> {self.dst}")
        else:
            try:
                print(f"Symlinking {self.src} -> {self.dst}")
                self.dst.symlink_to(self.src)
                self.set_permissions()
            except OSError as e:
                print(f"Error creating symlink {self.dst}: {e}")
                return False
                
        return True


def detect_platform():
    """Detect the current platform"""
    uname_string = uname()[0]
    if uname_string == "Darwin":
        return "OSX"
    elif uname_string == "Linux":
        return "Linux"
    elif uname_string == "FreeBSD":
        return "FreeBSD"
    elif uname_string.startswith("CYGWIN"):
        return "Cygwin"
    else:
        print(f"Unsupported platform: {uname_string}")
        sys.exit(1)

def create_dotfile(name, src, dst, compile_script=None, permissions=None, verbose=False, dry_run=False):
    """Helper function to create dotfile with global options"""
    return Dotfile(name, src, dst, compile_script, permissions, verbose, dry_run)

def main():
    parser = argparse.ArgumentParser(
        description="Deploy dotfiles by creating symlinks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Deploy all dotfiles
  %(prog)s --dry-run          # Show what would be deployed
  %(prog)s --verbose          # Show detailed output
        """
    )
    parser.add_argument('-n', '--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Show detailed output')
    
    args = parser.parse_args()
    
    platform = detect_platform()
    if args.verbose:
        print(f"Platform: {platform}")
        print(f"Home directory: {Path.home()}")
        print(f"Dotfiles directory: {Path(__file__).parent.parent}")
    # Common dotfiles for all platforms
    dotfiles = [
        ("curlrc", "curl/curlrc", ".curlrc"),
        ("mostrc", "most/mostrc", ".mostrc"),
        ("vimrc", "vim/vimrc", ".vimrc"),
        ("nvimrc", "vim/vimrc", ".config/nvim/init.vim"),
        ("screen", "screen/screenrc", ".screenrc"),
        ("gitconfig", "git/gitconfig", ".gitconfig"),
        ("bash_profile", "bash/bash_profile", ".bash_profile"),
        ("colors", "bash/colors", ".colors"),
        ("functions", "bash/functions", ".functions"),
        ("bashrc", "bash/bashrc", ".bashrc"),
        ("bash_aliases", "bash/bash_aliases", ".bash_aliases"),
        ("ansiblerc", "bash/ansiblerc", ".ansiblerc"),
        ("tmux", "tmux/tmux.conf", ".tmux.conf"),
        ("tmuxp", "tmuxp/dev.yaml", ".tmuxp/dev.yaml"),
        ("mc", "mc/ini", ".config/mc/ini"),
    ]
    
    # SSH config with compilation and specific permissions
    ssh_config = create_dotfile(
        "ssh config", "ssh/ssh_config", ".ssh/config",
        compile_script="compile.sh", permissions=0o640,
        verbose=args.verbose, dry_run=args.dry_run
    )
    
    # Deploy common dotfiles
    failed_count = 0
    for name, src, dst in dotfiles:
        dotfile = create_dotfile(name, src, dst, verbose=args.verbose, dry_run=args.dry_run)
        if not dotfile.deploy():
            failed_count += 1
    
    # Deploy SSH config
    if not ssh_config.deploy():
        failed_count += 1
    # Platform-specific dotfiles
    if platform == "OSX":
        osx_dotfiles = [
            ("Xmodmap", "osx/Xmodmap", ".Xmodmap"),
            ("bash_mac", "bash/bash_mac", ".bash_mac"),
            ("tmuxpowerline", "tmux/tmux.powerline.osx.conf", ".tmux.powerline.osx.conf"),
        ]
        for name, src, dst in osx_dotfiles:
            dotfile = create_dotfile(name, src, dst, verbose=args.verbose, dry_run=args.dry_run)
            if not dotfile.deploy():
                failed_count += 1
                
    elif platform == "FreeBSD":
        xinitrc = create_dotfile("xinitrc", "x/xinitrc", ".xinitrc", verbose=args.verbose, dry_run=args.dry_run)
        if not xinitrc.deploy():
            failed_count += 1
    
    # Summary
    if failed_count > 0:
        print(f"\nDeployment completed with {failed_count} failures.")
        sys.exit(1)
    else:
        action = "would be deployed" if args.dry_run else "deployed successfully"
        print(f"\nAll dotfiles {action}.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDeployment interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

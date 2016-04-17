#!/bin/bash
# Install Powerline and fonts in order 
# to make the Tmux experience much nicer
# Read the docs: https://powerline.readthedocs.org/en/latest/installation/linux.html

wget https://github.com/powerline/powerline/raw/develop/font/PowerlineSymbols.otf 
wget https://github.com/powerline/powerline/raw/develop/font/10-powerline-symbols.conf 

mkdir ~/.fonts
mv PowerlineSymbols.otf ~/.fonts/

fc-cache -vf ~/.fonts/ 

mkdir ~/.config/fontconfig/conf.d/ -p 

mv 10-powerline-symbols.conf ~/.config/fontconfig/conf.d/

#!/bin/bash
# ghostty_setup.sh - Script to set up Ghostty terminal support on remote systems
# Add this to your dotfiles and run it on remote systems to enable Ghostty support

# Check if we're running in a Ghostty terminal
if [[ "$TERM_PROGRAM" == "ghostty" ]]; then
    echo "Setting up Ghostty terminal support..."
    
    # Create Ghostty config directory
    GHOSTTY_RESOURCES_DIR=${GHOSTTY_RESOURCES_DIR:-"$HOME/.config/ghostty"}
    mkdir -p "$GHOSTTY_RESOURCES_DIR"
    
    # Set up environment variables
    cat << 'EOF' > "$HOME/.ghosttyrc"
# Ghostty terminal configuration
export TERM=xterm-256color
export COLORTERM=truecolor
export GHOSTTY_RESOURCES_DIR=${GHOSTTY_RESOURCES_DIR:-"$HOME/.config/ghostty"}
export GHOSTTY_ENABLE_CLIPBOARD=1

# If using tmux, ensure proper color support
if [[ -n "$TMUX" ]]; then
    tmux set-option -ga terminal-overrides ",xterm-256color:Tc"
fi
EOF
    
    # Add to bashrc if not already there
    if ! grep -q "source.*\.ghosttyrc" "$HOME/.bashrc"; then
        echo -e "\n# Ghostty terminal support" >> "$HOME/.bashrc"
        echo 'if [[ "$TERM_PROGRAM" == "ghostty" ]]; then' >> "$HOME/.bashrc"
        echo '    [ -f "$HOME/.ghosttyrc" ] && source "$HOME/.ghosttyrc"' >> "$HOME/.bashrc"
        echo 'fi' >> "$HOME/.bashrc"
        echo "Added Ghostty configuration to .bashrc"
    fi
    
    # Add to zshrc if it exists
    if [ -f "$HOME/.zshrc" ]; then
        if ! grep -q "source.*\.ghosttyrc" "$HOME/.zshrc"; then
            echo -e "\n# Ghostty terminal support" >> "$HOME/.zshrc"
            echo 'if [[ "$TERM_PROGRAM" == "ghostty" ]]; then' >> "$HOME/.zshrc"
            echo '    [ -f "$HOME/.ghosttyrc" ] && source "$HOME/.ghosttyrc"' >> "$HOME/.zshrc"
            echo 'fi' >> "$HOME/.zshrc"
            echo "Added Ghostty configuration to .zshrc"
        fi
    fi
    
    echo "Ghostty terminal setup complete!"
    echo "Please restart your shell or run: source ~/.ghosttyrc"
else
    echo "Error: Not running in a Ghostty terminal."
    echo "This script should be run from a Ghostty terminal session."
    exit 1
fi 
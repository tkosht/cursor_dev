#!/usr/bin/sh

curl -sSL -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash

. $HOME/.nvm/nvm.sh

nvm install --lts
npm install

# First, save a list of your existing global packages for later migration
npm list -g --depth=0 > ~/workspace/.npm-global-packages.txt

# Create a directory for your global packages
mkdir -p ~/workspace/.npm-global

# Configure npm to use the new directory path
npm config set prefix ~/workspace/.npm-global

# Note: Replace ~/.bashrc with ~/.zshrc, ~/.profile, or other appropriate file for your shell
echo 'export PATH=~/workspace/.npm-global/bin:$PATH' >> ~/.bashrc

# Apply the new PATH setting
source ~/.bashrc

# Now reinstall Claude Code in the new location
npm install -g @anthropic-ai/claude-code

# Optional: Reinstall your previous global packages in the new location
# Look at ~/workspace/.npm-global-packages.txt and install packages you want to keep



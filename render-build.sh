#!/usr/bin/env bash
# exit on error
set -o errexit

# Update dependencies
pip install -r requirements.txt

# --- Install Google Chrome for Render ---
STORAGE_DIR=/opt/render/project/.render

if [[ ! -d $STORAGE_DIR/chrome ]]; then
  echo "...Downloading Google Chrome..."
  mkdir -p $STORAGE_DIR/chrome
  cd $STORAGE_DIR/chrome
  # Download the latest stable Chrome package
  wget -q -P ./ https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  echo "...Extracting Chrome..."
  dpkg -x ./google-chrome-stable_current_amd64.deb $STORAGE_DIR/chrome
  rm ./google-chrome-stable_current_amd64.deb
  echo "...Google Chrome setup complete!"
else
  echo "...Using Google Chrome from Render cache."
fi

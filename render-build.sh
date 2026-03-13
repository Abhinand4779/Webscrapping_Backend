#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# You might need to install chrome here if using selenium on a custom environment
# But Render's native python environment makes this difficult without a Dockerfile.

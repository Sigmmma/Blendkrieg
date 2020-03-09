#!/bin/bash

# Installs the required libraries to the ./lib folder.
# This makes it so no additional steps are required to run the project in
# blender. And it avoids the need to install reclaimer and its deps into
# site-packages.
python3 -m pip install -r dependencies.txt --target="./lib" --no-deps

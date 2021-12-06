#!/bin/bash -e

python_version=3.6.8
pyenv install -s "${python_version:?}"
pyenv virtualenv "${python_version:?}" terraforming-mars-stats-"${python_version:?}" || true
pyenv local terraforming-mars-stats-"${python_version:?}"

pip3 install --upgrade pip

pip3 install -r requirements.txt

python -m ipykernel install --user --name=terraforming-mars-stats-"${python_version:?}"
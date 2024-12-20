#!/usr/bin/sh

d=$(cd $(dirname $0) && pwd)
cd $d/../

export PATH="$HOME/.local/bin:$PATH" 

# for llama-cpp-python
export CMAKE_ARGS="-DLLAMA_CUBLAS=ON"
export FORCE_CMAKE=1

poetry config virtualenvs.in-project true
poetry install

poetry add matplotlib
poetry run sed -i -e 's/^#font.family:\s*sans-serif/#font.family: IPAexGothic/' $(poetry run python -c 'import matplotlib as m; print(m.matplotlib_fname())')


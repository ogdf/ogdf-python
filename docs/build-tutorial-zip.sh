#!/bin/bash

set -e

if ! command -v jupytext &> /dev/null; then
    echo "Error: jupytext not found." >&2
    exit 1
fi

rm -f tutorial.zip
latexmk tutorial

for f in {examples,exercises,tutorial}/*.py; do
	jupytext -o "${f%.*}.ipynb" "$f"
done

zip -r tutorial.zip data examples/*.ipynb exercises/*.ipynb tutorial/*.ipynb tutorial/img build-ogdf.sh tutorial.pdf

rm -f {examples,exercises,tutorial}/*.ipynb

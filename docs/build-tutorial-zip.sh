#!/bin/bash

rm tutorial.zip
latexmk tutorial

for f in {examples,exercises,tutorial}/*.py; do
	jupytext -o "${f%.*}.ipynb" "$f"
done

zip -r tutorial.zip data examples/*.ipynb exercises/*.ipynb tutorial/*.ipynb build-ogdf.sh tutorial.pdf

rm {examples,exercises,tutorial}/*.ipynb

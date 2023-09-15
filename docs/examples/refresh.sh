#!/bin/bash

find -maxdepth 1 -name "*.ipynb" -exec jupyter nbconvert --to=notebook --inplace --ExecutePreprocessor.enabled=True {} \;

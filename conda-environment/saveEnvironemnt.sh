#!/bin/sh

source ~/anaconda3/etc/profile.d/conda.sh
conda activate chatbot
conda env export > environment.yml

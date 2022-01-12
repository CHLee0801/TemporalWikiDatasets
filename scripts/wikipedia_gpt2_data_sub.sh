#!/bin/bash

if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <old_date> <new_data> "
    exit 1
fi
mkdir Wikipedia_datasets/$1_gpt2
mkdir Wikipedia_datasets/$2_gpt2

#python wikipedia_datasets.py --mode subset --old $1 --new $2


#!/bin/bash

if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <old_date> <new_data> "
    exit 1
fi
mkdir Wikidata_datasets/$1
mkdir Wikidata_datasets/$2
mkdir Wikidata_datasets/$1_$2
for mode in new updated unchanged
do
    mkdir Wikidata_datasets/$1_$2/$mode
    for out in id item
    do
        mkdir Wikidata_datasets/$1_$2/$mode/${mode}_${out}
    done
done

for ((i=0;i<20;i++))
do
    python wikidata_datasets.py --mode unchanged --old $1 --new $2 --idx $i --combine 0 &
done

#python wikidata_datasets.py --mode unchanged --old 20210801 --new 20210901 --idx -1 --combine 1 

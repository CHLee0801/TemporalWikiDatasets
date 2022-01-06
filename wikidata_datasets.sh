#!/bin/bash

for ((i=0;i<20;i++))
do
    python wikidata_datasets.py --mode unchanged --old 20210801 --new 20210901 --idx $i --combine 0 &
done

#python wikidata_datasets.py --mode unchanged --old 20210801 --new 20210901 --idx -1 --combine 1 

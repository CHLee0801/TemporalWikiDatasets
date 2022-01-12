#!/bin/bash

for ((i=0;i<10;i++))
do
    python wikipedia_wikidata_mapping.py --old 20211101 --new 20211201 --idx $i &
done

#!/bin/bash

for ((i=0;i<17;i++))
do
    python wikipedia_datasets.py --mode entire --tenth_digit $i --month 20211201 &
done

#python wikipedia_datasets.py --mode entire --tenth_digit 16 --month 20210801 

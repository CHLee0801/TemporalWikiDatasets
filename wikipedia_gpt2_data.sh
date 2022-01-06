#!/bin/bash

for ((i=0;i<17;i++))
do
    python wikipedia_datasets.py --mode subset --tenth_digit $i --month 20210801 &
done

#python wikipedia_datasets.py --mode 1 --tenth_digit 16 --month 20210801 

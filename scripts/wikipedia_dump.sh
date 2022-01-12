#!/bin/bash
if [[ $# -ne 1 ]]; then
    echo "Illegal number of parameters, Please enter the data for download the wikipedia datasets"
    exit 1
fi
mkdir Wikipedia_datasets
wget https://dumps.wikimedia.org/enwiki/$1/enwiki-$1-pages-articles-multistream.xml.bz2
python -m wikiextractor.WikiExtractor enwiki-$1-pages-articles-multistream.xml.bz2 --json
mv text Wikipedia_datasets/$1

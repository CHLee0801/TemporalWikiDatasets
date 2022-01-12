#!/bin/bash
if [[ $# -ne 1 ]]; then
    echo "Illegal number of parameters, Please enter the data for download the wikidata datasets" 
    exit 1
fi
mkdir wikidata_datasets
wget https://dumps.wikimedia.org/wikidatawiki/$1/wikidatawiki-$1-pages-articles-multistream.xml.bz2
python -m gensim.scripts.segment_wiki -i -f wikidatawiki-20211101-pages-articles-multistream.xml.bz2 -o wikidata-$1.json.gz
mv wikidata-$1.json.gz  Wikidata_datasets

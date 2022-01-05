# TemporalWiki Datasets

![Figure 1](/mnt/nfs/changho/figure1.png)

## 0. Setting

* Python environment 3.9
```
conda create -n twiki python=3.9 
conda activate twiki
```

* Python packages
```
pip install -r requirements.txt
```

## 0-1. Wikipedia Dump Download

Please choose [Wikipedia Dump File](https://dumps.wikimedia.org/enwiki/) in XML format. (About 18 GB)
e.g. [https://dumps.wikimedia.org/enwiki/20211001/enwiki-20211001-pages-articles-multistream.xml.bz2](https://dumps.wikimedia.org/enwiki/20211001/enwiki-20211001-pages-articles-multistream.xml.bz2)

Execute the command.
```
cd Wikipedia_datasets
wget <Dump File Link>
```

It will take about less than 2 hours to download the file.

Execute command.
```
python -m wikiextractor.WikiExtractor <Wikipedia dump file>
```

## 0-2. Wikidata Dump Download

Please choose [Wikidata Dump File](https://dumps.wikimedia.org/wikidatawiki/) in XML format. (About 120 GB)
e.g. [https://dumps.wikimedia.org/wikidatawiki/20211001/wikidatawiki-20211001-pages-articles-multistream.xml.bz2](https://dumps.wikimedia.org/wikidatawiki/20211001/wikidatawiki-20211001-pages-articles-multistream.xml.bz2)

```
cd Wikidata_datasets 
wget <Dump File Link>
```

It will take about 7-8 hours to download the file.

```
python -m gensim.scripts.segment_wiki -i -f <Wikidata Dump file> -o <Transformed file>
<Transformed file> : 'wikidata-{year+month+date}.json.gz' e.g. wikidata-20210801.json.gz
```

* It is important to write 'json.gz' at the end for your new file.

It will take 2 days. 

## 1. Wikipedia

#### wikipedia_datasets.py

``` 
python wikipedia_datasets.py --mode 0 --old <previous_month> --new <new_month>
or
python wikipedia_datasets.py --mode 1 --tenth_digit <0-16> --month <month>
```
> mode : 0 (generate datasets for only subsets)   
> old : year + month + date, e.g. 20210801   
> new : year + month + date, e.g. 20210901   

> mode : 1 (generate datasets for entire datasets)   
> tenth_digit : One number between 0-16 (There are 16 sets of Wikipedia bundle)   
> month : year + month + date, e.g. 20210801   

We suggest you to use bash file for mode 1. You can easily modify example bash file and type command below in terminal.
``` 
bash wikipedia_datasets.sh
```

You will have final csv file in directory below.

- ../TemporalWiki_datasets/Wikipedia_datasets

## 2. Wikidata

#### wikidata_datasets.py

``` 
python wikidata_datasets.py --mode <mode> --old <previous_month> --new <new_month> --idx <0-100> --combine <0 or 1>
```
> mode : unchanged / updated / new   
> old : year + month + date, e.g. 20210801   
> new : year + month + date, e.g. 20210901   
> idx : One number between 0-100 (Preprocessing is held in every million entities of Wikidata)   
> combine : 0 (Not combining created sets by idx) / 1 (Combine all the sets to one json file)   

We suggest you to use bash file for this part. You can easily modify example bash file and type command below in terminal.
``` 
bash wikidata_datasets.sh
```

## 3. Aligning

#### evaluation_datasets.py

``` 
python evaluation_datasets.py --mode <mode> --old <previous_month> --new <new_month>
```
> mode : unchanged / updated / new   
> old : year + month + date, e.g. 20210801   
> new : year + month + date, e.g. 20210901   

You will have final csv file in directory below.

- ../TemporalWiki_datasets/Wikidata_datasets/{old}\_{new}/{mode}/final_{mode}_item.csv
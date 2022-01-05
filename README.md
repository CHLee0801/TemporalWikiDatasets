# TemporalWiki Datasets

![Figure 1](https://user-images.githubusercontent.com/87512263/148145276-30afa286-110d-44aa-9ca4-dde3dc42fd75.png)

This is an overview of this github repository. 

You have to download Wikipedia dumps first. And then you can work on **Section 1. Wikipedia** and **Section 2. Wikidata** at the same time. But you have to get both Section done to do **Section 3. Alignment**. 

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

* Some directories

You have to choose two time step for Wikipedia and Wikidata (time step should be same for both).

> old_time_step : year + month + date, e.g. 20210801
> new_time_step : year + month + date, e.g. 20210901

Then follow the command.
```
cd Wikipedia_datasets
mkdir <old_time_step>
mkdir <old_time_step>_gpt2
mkdir <new_time_step>
mkdir <new_time_stem>_gpt2
cd ../
cd Wikidata_datasets
mkdir <old_time_step>
mkdir <new_time_stem>
mkdir <old_time_step>_<new_time_step>
```

Output would look like this.

![Figure 2](https://user-images.githubusercontent.com/87512263/148151373-d1b65f7d-8a86-4419-838e-c9a8a996a88f.png)

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
```
> <'Transformed file'> : 'wikidata-{year+month+date}.json.gz' e.g. wikidata-20210801.json.gz

* It is important to write 'json.gz' at the end for your new file.

It will take 2 days. 

## 1. Wikipedia

There are two types of generation at the end. One is GPT-2 training datasets, and the other is Wikipedia subsets which will be used in Section 3. Alignment. 

#### wikipedia_datasets.py

``` 
python wikipedia_datasets.py --mode 0 --old <previous_month> --new <new_month>
```
> mode : 0 (generate datasets for only subsets)   
> old : year + month + date, e.g. 20210801   
> new : year + month + date, e.g. 20210901   

or
```
python wikipedia_datasets.py --mode 1 --tenth_digit <0-16> --month <month>
```
> mode : 1 (generate datasets for entire datasets)   
> tenth_digit : One number between 0-16 (There are 16 sets of Wikipedia bundle)   
> month : year + month + date, e.g. 20210801   

We suggest you to use bash file for mode 1. You can easily modify example bash file **wikipedia_datasets.sh** and type command below in terminal.
``` 
bash wikipedia_datasets.sh
```

You will have final csv file in directory below.

- ../TemporalWiki_datasets/Wikipedia_datasets

## 2. Wikidata

Section 2 preprocess Wikidata from extracting entity id from Wikidata Dump to mapping id to corresponding string item.

#### wikidata_datasets.py

``` 
python wikidata_datasets.py --mode <mode> --old <previous_month> --new <new_month> --idx <0-100> --combine <0 or 1>
```
> mode : unchanged / updated / new   
> old : year + month + date, e.g. 20210801   
> new : year + month + date, e.g. 20210901   
> idx : One number between 0-100 (Preprocessing is held in every million entities of Wikidata)   
> combine : 0 (Not combining created sets by idx) / 1 (Combine all the sets to one json file)   

We suggest you to use bash file for this part. You can easily modify example bash file **wikidata_datasets.sh** and type command below in terminal.
``` 
bash wikidata_datasets.sh
```

The whole process will take less than a day (The mapping process takes a lot of time).

## 3. Aligning

Section 3 aligned subsets file from Section 1 and Wikidata item file from Section 2 by mapping Wikipedia page-id and Wikidata entity id.

#### evaluation_datasets.py

``` 
python evaluation_datasets.py --mode <mode> --old <previous_month> --new <new_month>
```
> mode : unchanged / updated / new   
> old : year + month + date, e.g. 20210801   
> new : year + month + date, e.g. 20210901   

You will have final csv file in directory below.

- ../TemporalWiki_datasets/Wikidata_datasets/<'previous_month'>\_<'new_month'>/<'mode'>/final_<'mode'>_item.csv
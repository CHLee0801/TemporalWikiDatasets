# TemporalWiki Datasets

## 0. Setting

* Python environment 3.9
> conda create -n twiki python=3.9 
> conda activate twiki

* Python packages
> pip install -r requirements.txt

### Wikipedia Dump Download

### Wikidata Dump Download

https://dumps.wikimedia.org/wikidatawiki/

If you visit the website above, you can see some dates. Click the one you want for WikiData. 

For this project, we will only use file ends with '*.xml.bz2'

If you chose the dump, instead just click the link, go to the directory you are working on, and copy link and type the command below in your terminal

```
cd Wikidata_datasets 
wget 'link of wikidata dump'
```

This will take about 7-8 hours to download the file.

```
pip install gensim   
python -m gensim.scripts.segment_wiki -i -f 'original_name_of_the_file.xml.bz2' -o 'new_name_you_want.json.gz'
```

* It is important to write 'json.gz' at the end for your new file.

This will take about 2 days to complete this. 

## 1. Wikipedia

#### wikipedia_datasets.py

``` 
python wikipedia_datasets.py --mode 0 --old <previous_month> --new <new_month>
or
python wikipedia_datasets.py --mode 1 --tenth_digit <0-16> --month <month>
```
* mode : 0 (generate datasets for only subsets)
* old : year + month. ex) 20210801
* new : year + month. ex) 20210901

* mode : 1 (generate datasets for entire datasets)
* tenth_digit : One number between 0-16 (There are 16 sets of Wikipedia bundle)
* month : year + month. ex) 20210801

We suggest you to use bash file for mode 1. You can easily modify example bash file.
``` 
bash wikipedia_datasets.sh
```

You will have final csv file in directory below.

> ../TemporalWiki_datasets/Wikipedia_datasets

## 2. Wikidata

#### wikidata_datasets.py

``` 
python wikidata_datasets.py --mode <mode> --old <previous_month> --new <new_month> --idx <0-100> --combine <0 or 1>
```
* mode : unchanged / updated / new
* old : year + month. ex) 20210801
* new : year + month. ex) 20210901
* idx : One number between 0-100 (Preprocessing is held in every million entities of Wikidata)
* combine : 0 (Not combining created sets by idx) / 1 (Combine all the sets to one json file)

We suggest you to use bash file for this part. You can easily modify example bash file. 
``` 
bash wikidata_datasets.sh
```


## 3. Aligning

#### evaluation_datasets.py

``` 
python evaluation_datasets.py --mode <mode> --old <previous_month> --new <new_month>
```
* mode : unchanged / updated / new
* old : year + month. ex) 20210801
* new : year + month. ex) 20210901

You will have final csv file in directory below.

* ../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/{mode}/final_{mode}_item.csv
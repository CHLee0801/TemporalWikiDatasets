import json
import pandas as pd
import argparse
import requests
from bs4 import BeautifulSoup
import time
import random

SUPPORT_MODE=["unchanged", "new", "updated"]

def construct_generation_args():

    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', type=str, default="unchange", required=True)
    parser.add_argument('--old', type=str, default='20210801')
    parser.add_argument('--new', type=str, default='20210901')
    arg = parser.parse_args()
    
    return arg

def combine_json(old, new):
    output_dir = f"../TemporalWiki_datasets/Wikidata_datasets/Wikipedia_to_Wikidata_total.json"
    with open(output_dir, "r") as read_json_1:
        wikipedia_to_wikidata = json.load(read_json_1)
    for i in range(10):
        idx = str(i)
        input_dir = f"../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/Wikipedia_to_Wikidata_{idx}.json"
        with open(input_dir, "r") as read:
            small_list = json.load(read)
        for j in small_list:
            if j in wikipedia_to_wikidata:
                continue
            wikipedia_to_wikidata[j] = small_list[j]

    with open(output_dir, "w") as write_json_file:
        json.dump(wikipedia_to_wikidata, write_json_file, indent=4)

def aligning(old, new, mode):
    subset_dir = f"../TemporalWiki_datasets/Wikipedia_datasets/wikipedia_{old}_{new}_subset.json"
    unchange_dir = f"../TemporalWiki_datasets/Wikipedia_datasets/wikipedia_{old}_{new}_unchanged.json"
    wikidata_to_wikipedia = f"../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/Wikipedia_to_Wikidata_total.json"
    id_fname = f"../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/{mode}/total_{mode}_id.json"
    item_fname = f"../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/{mode}/total_{mode}_item.json"

    if mode == "unchanged":
        with open(unchange_dir, "r") as read_json_0:
            id_text_dict = json.load(read_json_0)
    else:
        with open(subset_dir, "r") as read_json_0:
            id_text_dict = json.load(read_json_0)

    with open(wikidata_to_wikipedia, "r") as read_json_1:
        mapping_dict = json.load(read_json_1)

    with open(id_fname, "r") as read_json_2:
        id_list = json.load(read_json_2)
        
    with open(item_fname, "r") as read_json_3:
        item_list = json.load(read_json_3)

    filtered_name = []

    for j in range(len(id_list)):
        if id_list[j][0] not in mapping_dict: 
            continue
        wikipedia_id = mapping_dict[id_list[j][0]]
        if wikipedia_id not in id_text_dict:
            continue
        object = item_list[j][2].lower()
        sub = ""
        rel = ""
        obj = ""
        text = str(id_text_dict[wikipedia_id])
        text = text.lower()
        if object in text:
            for i in item_list[j][0]:
                if i == ',':
                    continue
                sub += i
            for i in item_list[j][1]:
                if i == ',':
                    continue
                rel += i
            for i in item_list[j][2]:
                if i == ',':
                    continue
                obj += i
            filtered_name.append([sub, rel, obj])

    output_item_dir = f"../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/{mode}/final_{mode}_item.scv"
    
    pd.DataFrame(filtered_name, columns=['subject','relation','objective']).to_csv(output_item_dir, index=False)

def main():
    arg = construct_generation_args()
    
    mode = arg.mode # mode : unchanged / updated / new
    old = arg.old # old : year + month + date, e.g. 20210801
    new = arg.new # new : year + month + date, e.g. 20210901
    if mode != "unchanged":
        combine_json(old, new)
    aligning(old, new, mode) # Map Wikipedia to Wikidata

if __name__ == '__main__':
    main()
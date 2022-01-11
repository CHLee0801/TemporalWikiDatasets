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
    wikipedia_to_wikidata = {}
    for i in range(10):
        idx = str(i)
        input_dir = f"../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/Wikipedia_to_Wikidata_{idx}.json"
        with open(input_dir, "r") as read:
            small_list = json.load(read)
        for j in small_list:
            if j in wikipedia_to_wikidata:
                continue
            wikipedia_to_wikidata[j] = small_list[j]

    output_dir = f"../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/Wikipedia_to_Wikidata_total.json"
    with open(output_dir, "w") as write_json_file:
        json.dump(wikipedia_to_wikidata, write_json_file, indent=4)

def aligning(old, new, mode):
    subset_dir = f"../TemporalWiki_datasets/Wikipedia_datasets/wikipedia_{old}_{new}_subset.json"
    wikidata_to_wikipedia = f"../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/Wikipedia_to_Wikidata_total.json"
    id_fname = f"../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/{mode}/total_{mode}_id.json"
    item_fname = f"../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/{mode}/total_{mode}_item.json"

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

def unchanged_filtering(old, new, mode):
    item_dir = f"../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/{mode}/total_{mode}_item.json"
    with open(item_dir, "r") as read:
        item_list = json.load(read)
    
    filtered_list = []

    for i in range(len(item_list)):
        rel = item_list[i][1]
        sub = item_list[i][0].lower()
        obj = item_list[i][2].lower()
        try: # Detect unicode
            sub.encode('ascii')
            obj.encode('ascii')
        except:
            continue

        if "untitled" in sub or "untitled" in obj:
            continue
        if rel.lower() in obj:
            continue
        if len(sub.split()) > 5 or len(obj.split()) > 5:
            continue
        if sub in obj or obj in sub:
            continue
        if ',' in obj or ',' in sub or ',' in rel :
            continue

        # Remove string with numbers, punctuation, special characters
        no = 0
        for k in sub:
            if k == ' ':
                continue
            if k > 'z' or k < 'A':
                no = 1
                break
        if no == 1:
            continue
        for p in obj:
            if p == ' ':
                continue
            if p > 'z' or p < 'A':
                no = 1
                break
        if no == 1:
            continue
        filtered_list.append(item_list[i])
    
    semi_list = []
    for i in filtered_list:
        if i in semi_list:
            continue
        else:
            semi_list.append(i)
    random.shuffle(semi_list)
    small = {}
    semi_final_list = []
    for i in semi_list:
        if i[1] in small:
            small[i[1]] += 1
            if small[i[1]] > 100:
                continue
        else:
            small[i[1]] = 1
        semi_final_list.append(i)

    final_list = []
    data_list = random.sample(range(len(semi_final_list)), 10000)
    for i in data_list:
        if i in data_list:
            final_list.append(semi_final_list[i])
    
    output_dir = f"../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/{mode}/final_{mode}_item.scv"

    pd.DataFrame(final_list, columns=['subject','relation','objective']).to_csv(output_dir, index=False)

def main():
    arg = construct_generation_args()
    
    mode = arg.mode # mode : unchanged / updated / new
    old = arg.old # old : year + month + date, e.g. 20210801
    new = arg.new # new : year + month + date, e.g. 20210901

    if mode == "unchanged":
        unchanged_filtering(old, new, mode) # Unchange heuristic filtering
    else: # If mode is updated or new
        combine_json(old, new)
        aligning(old, new, mode) # Map Wikipedia to Wikidata

if __name__ == '__main__':
    main()
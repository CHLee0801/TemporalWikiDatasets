import json
import pandas as pd
import argparse
import requests
from bs4 import BeautifulSoup
import time
import random

SUPPORT_MODE=["unchanged", "changed"]

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
    final_list = []
    small = {}
    for i in filtered_name:
        if i in small:
            continue
        small[i] = 1
        final_list.append(i)
    output_item_dir = f"../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/{mode}/filtered_{mode}_item.scv"
    
    pd.DataFrame(final_list, columns=['subject','relation','objective']).to_csv(output_item_dir, index=False)

def post_processing(old, new, mode):
    filtered = f"../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/{mode}/filtered_{mode}_item.scv"
    filtered_csv = pd.read_csv(filtered)
    filtered_list = pd.read_csv(filtered_csv)
    
    first_post_process_list = []
    dic = {}
    dic2 = {}
    dic3 = {}
    for i in filtered_list:
        sentence = i[0] + i[1] + i[2]
        if sentence in dic:
            continue
        dic[sentence] = 1
        sub, rel, obj = i[0], i[1], i[2]
        sub = sub.lower()
        rel = rel.lower()
        obj = obj.lower()
        if sub in obj or obj in sub:
            continue
        if len(obj.split()) > 5:
            continue
        first_post_process_list.append(i)
        
    # Keep proportion of Subject under 1%
    proportion_1 = len(first_post_process_list) // 100
    random.shuffle(first_post_process_list)
    second_post_process_list = []
    for i in first_post_process_list:
        if i[0] in dic2:
            dic2[i[0]] += 1
            if dic2[i[0]] > proportion_1:
                continue
        else:
            dic2[i[0]] = 1
        second_post_process_list.append(i)
        
    # Keep proportion of Relation under 5%
    proportion_2 = len(second_post_process_list) // 20
    final_list = []
    for i in second_post_process_list:
        if i[1] in dic3:
            dic3[i[1]] += 1
            if dic3[i[1]] > proportion_2:
                continue
        else:
            dic3[i[1]] = 1
        final_list.append(i)
    
    output_dir = f"../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/{mode}/final_{mode}_item.scv"
    pd.DataFrame(final_list, columns=['subject','relation','object']).to_csv(output_dir, index=False)

def main():
    arg = construct_generation_args()
    
    mode = arg.mode # mode : unchanged / changed
    old = arg.old # old : year + month + date, e.g. 20210801
    new = arg.new # new : year + month + date, e.g. 20210901
    if mode == "changed":
        combine_json(old, new)
    aligning(old, new, mode) # Map Wikipedia to Wikidata
    post_processing(old, new, mode)

if __name__ == '__main__':
    main()
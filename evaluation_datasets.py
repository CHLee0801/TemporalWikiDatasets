import json
import pandas as pd
import argparse
import requests
from bs4 import BeautifulSoup
import time
import random

parser = argparse.ArgumentParser()
parser.add_argument('--mode', type=str, default="unchange", required=True)
parser.add_argument('--old', type=str, default='20210801')
parser.add_argument('--new', type=str, default='20210901')
arg = parser.parse_args()

def wikipedia_csv_to_json(old, new):
    file_dir = f"../TemporalWiki_datasets/Wikipedia_datasets/wikipedia_{old}_{new}_subset.csv"
    df = pd.read_csv(file_dir, encoding='utf-8')

    wikipedia_subsets = {}
    list_item = df.values.tolist()

    for i in list_item:
        id = str(i[1])
        id = id[36:]
        text = str(i[3]).lower()
        if id not in wikipedia_subsets:
            wikipedia_subsets[id] = []
            wikipedia_subsets[id].append(text)
        else:
            wikipedia_subsets[id].append(text)

    output_file_dir = f"../TemporalWiki_datasets/Wikipedia_datasets/wikipedia_{old}_{new}_subset.json"
    with open(output_file_dir, "w") as write_json_file:
        json.dump(wikipedia_subsets, write_json_file, indent=4)

def crawling(old, new):
    file_dir = f"../TemporalWiki_datasets/Wikipedia_datasets/wikipedia_{old}_{new}_subset.json"
    with open(file_dir, "r") as read_json_file:
        wikipedia_list = json.load(read_json_file)

    wikipedia_to_wikidata = {}
    wikipedia_id = []
    base_url = "https://en.wikipedia.org/wiki?curid="

    for id in wikipedia_list:
        wikipedia_id.append(id)
    
    for i in range(len(wikipedia_id)):
        try:
            url = base_url + wikipedia_id[i]
            response = requests.get(url)
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            a = soup.select_one("#t-wikibase > a")
            wikidata_id = str(a)[72:-92]
            wikipedia_to_wikidata[wikidata_id] = wikipedia_id[i]
        except:
            time.sleep(1)
            i -= 1

    output_file_dir = f"../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/Wikipedia_to_Wikidata.json"
    with open(output_file_dir, "w") as write_json_file:
        json.dump(wikipedia_to_wikidata, write_json_file, indent=4)

def aligning(old, new, mode):
    subset_dir = f"../TemporalWiki_datasets/Wikipedia_datasets/wikipedia_{old}_{new}_subset.json"
    wikidata_to_wikipedia = f"../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/Wikipedia_to_Wikidata.json"
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

    filtered_id = []
    filtered_name = []

    for j in range(len(id_list)):
        if id_list[j][0] not in mapping_dict: # id_list[j][0] = wikidata_id, big_dict = wikidata_id, wikipedia_id
            continue
        wikipedia_id = mapping_dict[id_list[j][0]] # wikipedia_id
        if wikipedia_id not in id_text_dict:
            continue
        filtered_id.append(id_list[j])
        filtered_name.append(item_list[j])

    output_id_dir = f"../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/{mode}/aligned_{mode}_id.json"
    output_item_dir = f"../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/{mode}/aligned_{mode}_item.json"

    with open(output_id_dir, "w") as write_json_file:
        json.dump(filtered_id, write_json_file, indent=4)
    with open(output_item_dir, "w") as write_json_file:
        json.dump(filtered_name, write_json_file, indent=4)

def updated_new_filtering(old, new, mode):
    item_dir = f"../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/{mode}/aligned_{mode}_item.json"
    with open(item_dir, "r") as read:
        item_list = json.load(read)
    filtered_list = []
    
    for i in range(len(item_list)):
        rel = item_list[i][1]
        sub = item_list[i][0].lower()
        obj = item_list[i][2].lower()
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
        cnt1 = 0
        cnt2 = 0
        for j in sub:
            try:
                j.encode('ascii')
            except:
                cnt1 += 1
                continue
        if len(j) == cnt1:
            continue
        for k in obj:
            try:
                k.encode('ascii')
            except:
                cnt2 += 1
                continue
        if len(k) == cnt2:
            continue

        filtered_list.append(item_list[i])
    
    semi_list = []
    for i in filtered_list:
        if i in semi_list:
            continue
        else:
            semi_list.append(i)

    random.shuffle(semi_list)
    final_list = []
    data_list = random.sample(range(len(semi_list)), 10000)
    for i in data_list:
        if i in data_list:
            final_list.append(semi_list[i])

    output_dir = f"../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/{mode}/final_{mode}_item.json"
    with open(output_dir, "w") as write_json_file:
        json.dump(final_list, write_json_file, indent=4)

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
    final_list = []
    data_list = random.sample(range(len(semi_list)), 10000)
    for i in data_list:
        if i in data_list:
            final_list.append(semi_list[i])
    
    output_dir = f"../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/{mode}/final_{mode}_item.json"
    with open(output_dir, "w") as write_json_file:
        json.dump(final_list, write_json_file, indent=4)

def json_to_csv(old, new, mode):
    item_dir = f"../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/{mode}/final_{mode}_item.json"
    with open(item_dir, "r") as read_json_file_2:
        final = json.load(read_json_file_2)

    f_list= []
    for i in range(len(final)):
        f_list.append(final[i])
    output_dir = f"../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/{mode}/final_{mode}_item.csv"
    pd.DataFrame(f_list, columns=['subject','relation','objective']).to_csv(output_dir, index=False)

mode = arg.mode
old = arg.old 
new = arg.new 

if mode == "unchanged":
    unchanged_filtering(old, new, mode)
    json_to_csv(old, new, mode)
else:
    wikipedia_csv_to_json(old, new)
    crawling(old, new)
    aligning(old, new, mode)
    updated_new_filtering(old, new, mode)
    json_to_csv(old, new, mode)


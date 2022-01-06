import json
import argparse
import requests
from bs4 import BeautifulSoup
import time

def construct_generation_args():

    parser = argparse.ArgumentParser()
    parser.add_argument('--idx', type=int, default=0)
    parser.add_argument('--old', type=str, default='20210801')
    parser.add_argument('--new', type=str, default='20210901')
    arg = parser.parse_args()
    
    return arg

def crawling(old, new, idx):
    file_dir = f"../TemporalWiki_datasets/Wikipedia_datasets/wikipedia_{old}_{new}_subset.json"
    with open(file_dir, "r") as read_json_file:
        wikipedia_list = json.load(read_json_file)

    wikipedia_to_wikidata = {}
    wikipedia_id = []
    base_url = "https://en.wikipedia.org/wiki?curid="

    for id in wikipedia_list:
        wikipedia_id.append(id)
    num = len(wikipedia_id) // 10
    start = num * idx
    if idx == 10:
        end = len(wikipedia_id)
    else:
        end = num * (idx + 1)
    for i in range(start, end):
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

    output_file_dir = f"../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/Wikipedia_to_Wikidata_{idx}.json"
    with open(output_file_dir, "w") as write_json_file:
        json.dump(wikipedia_to_wikidata, write_json_file, indent=4)

def main():
    arg = construct_generation_args()

    idx = arg.idx
    old = arg.old # old : year + month + date, e.g. 20210801
    new = arg.new # new : year + month + date, e.g. 20210901
    crawling(old, new, idx)
    

if __name__ == '__main__':
    main()
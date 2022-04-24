import pandas as pd 
import re
import json
from difflib import Differ
import os 
from argparse import ArgumentParser
from transformers import GPT2Tokenizer

SUPPORT_MODE= ["subset", "entire"]

differ = Differ()

tokenizer = GPT2Tokenizer.from_pretrained("gpt2-large")

def construct_generation_args():

    parser = ArgumentParser()
    parser.add_argument('--mode', default="subset", type=str, choices=SUPPORT_MODE)
    parser.add_argument('--old', default='20211101', type=str, required=False)
    parser.add_argument('--new', default='20211201', type=str, required=False)
    parser.add_argument('--month', default="20211201", type=str, required=False)
    parser.add_argument('--tenth_digit', default=0, type=int, required=False)
    arg = parser.parse_args()
    return arg

def preprocess(lst):
    new_lst = []
    ref_lst = []
    for line in lst:
        if line!='\n':
            line = line.replace('\n', '')
            new_lst.append(line)
            line = re.sub(r'[^\w\s]','',line)
            line = line.lower()
            ref_lst.append(line)
    return new_lst, ref_lst

def get_difference(old, new):  

    old, old_pre = preprocess(old.split('\n'))
    new, new_pre = preprocess(new.split('\n'))

    checkpoints = []
    j=0
    for i in range(len(old_pre)):
        if old_pre[i] in new_pre[j:]:
            j = new_pre.index(old_pre[i])
            checkpoints.append([i,j])

    diff = []
    for i in range(len(checkpoints)-1):
        old1 = checkpoints[i][0]
        new1 = checkpoints[i][1]
        old2 = checkpoints[i+1][0]
        new2 = checkpoints[i+1][1]
        old_diff = ". ".join(old[old1+1:old2])
        new_diff = ". ".join(new[new1+1:new2])
        
        if (new1+1)!=new2:
            if (old1+1)!=old2:
                df = list(differ.compare(old_diff.split('.'), new_diff.split('.'))) #Getting the diff
                specific_diff = []
                for d in df:
                    if '+' in d and (d[0]!='?'):
                        specific_diff.append(d.replace("+ ", ""))
                specific_diff= ". ".join(specific_diff)
                diff.append(specific_diff) 
            else:    
                diff.append(new_diff)
    diff = ". ".join(diff)
    
    return diff

def generate_subsets_csv(old_month, new_month):
    data_dir1 = f"../TemporalWiki_datasets/Wikipedia_datasets/{new_month}" # the newer dump
    data_dir2 = f"../TemporalWiki_datasets/Wikipedia_datasets/{old_month}" # the old dump
    lst = os.listdir(data_dir1)
    lst_ = os.listdir(data_dir2)
    lst.sort()
    lst_.sort()

    old_articles = {}
    new_articles = {}

    for dir in lst:
        dir1 = data_dir1+'/'+dir 
        lst1 = os.listdir(dir1)
        lst1.sort()
        for file in lst1:
            full_dir = dir1+'/'+file 
            print(full_dir)
            data = pd.read_json(full_dir,lines=True)
            for index, row in data.iterrows():
                id = row['id']
                url = row['url']
                title = row['title']
                text = row['text']
                new_articles[id] = [url,title,text]

    for dir in lst_:
        dir1 = data_dir2+'/'+dir 
        lst1 = os.listdir(dir1)
        lst1.sort()
        for file in lst1:
            full_dir = dir1+'/'+file 
            print(full_dir)
            data = pd.read_json(full_dir,lines=True)
            for index, row in data.iterrows():
                id = row['id']
                url = row['url']
                title = row['title']
                text = row['text']
                old_articles[id] = [url,title,text]

    new_article_id = [0]
    entries = []

    cnt=0

    for key in new_articles:
        if cnt%1000==0:
            print(key/70000000)
        cnt+=1
        row = new_articles[key]
        url = row[0]
        title = row[1]
        new_article = row[2]
        if key not in old_articles:
            new_article_id.append(key)
            entry = [key,url,title,new_article.replace('\n', '')]
            entries.append(entry)
        else:
            old_row = old_articles[key]
            old_article = old_row[2]
            if new_article!='':
                diff = get_difference(old_article, new_article)
                if diff!='':
                    entry = [key,url,title,diff]
                    entries.append(entry)
    
    output_dir = f"../TemporalWiki_datasets/Wikipedia_datasets/wikipedia_{old_month}_{new_month}_subset.csv"
    pd.DataFrame(entries, columns=['id','url','title','text']).to_csv(output_dir, index=False) # save it as csv

def generate_unchanged_csv(old_month, new_month):
    data_dir1 = f"../TemporalWiki_datasets/Wikipedia_datasets/{new_month}" # the newer dump
    data_dir2 = f"../TemporalWiki_datasets/Wikipedia_datasets/{old_month}" # the old dump
    lst = os.listdir(data_dir1)
    lst_ = os.listdir(data_dir2)
    lst.sort()
    lst_.sort()

    old_articles = {}
    new_articles = {}

    for dir in lst:
        dir1 = data_dir1+'/'+dir 
        lst1 = os.listdir(dir1)
        lst1.sort()
        for file in lst1:
            full_dir = dir1+'/'+file 
            print(full_dir)
            data = pd.read_json(full_dir,lines=True)
            for index, row in data.iterrows():
                id = row['id']
                url = row['url']
                title = row['title']
                text = row['text']
                new_articles[id] = [url,title,text]

    for dir in lst_:
        dir1 = data_dir2+'/'+dir 
        lst1 = os.listdir(dir1)
        lst1.sort()
        for file in lst1:
            full_dir = dir1+'/'+file 
            print(full_dir)
            data = pd.read_json(full_dir,lines=True)
            for index, row in data.iterrows():
                id = row['id']
                url = row['url']
                title = row['title']
                text = row['text']
                old_articles[id] = [url,title,text]

    new_article_id = [0]
    entries = []
    unchanged_entries = []
    whole = []
    subset = []

    cnt=0

    for key in new_articles:
        if cnt%1000==0:
            print(key/70000000)
        cnt+=1
        row = new_articles[key]
        url = row[0]
        title = row[1]
        new_article = row[2]
        if key not in old_articles:
            new_article_id.append(key)
            entry = [key,url,title,new_article.replace('\n', '')]
            entries.append(entry)
        else:
            old_row = old_articles[key]
            old_article = old_row[2]
            if new_article!='':
                diff, same = get_difference(old_article, new_article)
                whole.append(len(new_article))
                subset.append(len(diff))
                if diff!='':
                    entry = [key,url,title,diff]
                    entries.append(entry)
                    if same!='':
                        unchanged_entries.append([key,url,title,same])
                else:
                    unchanged_entries.append([key,url,title,new_article])
    output_dir = f"../TemporalWiki_datasets/Wikipedia_datasets/wikipedia_{old_month}_{new_month}_unchanged.csv"    
    pd.DataFrame(unchanged_entries, columns=['id','url','title','text']).to_csv(output_dir, index=False)

def wikipedia_csv_to_json(old, new, key):
    if key == 0:
        ver = "subset"
    else:
        ver = "unchanged"
    file_dir = f"../TemporalWiki_datasets/Wikipedia_datasets/wikipedia_{old}_{new}_{ver}.csv"
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

    output_file_dir = f"../TemporalWiki_datasets/Wikipedia_datasets/wikipedia_{old}_{new}_{ver}.json"
    with open(output_file_dir, "w") as write_json_file:
        json.dump(wikipedia_subsets, write_json_file, indent=4)
    

def process_article(title, text):
    # Configurations
    length_limit = 512 #The limit of words per input instance. 512 is the maximum

    text = str(text).replace('\n', '')
    text = str(title) + '. ' + text
    lst = []
    tokens = tokenizer.encode(text)
    if len(tokens) > length_limit:
        while len(tokens) > length_limit:
            seg1 = tokens[:length_limit]
            tokens = tokens[length_limit:]
            seg1_text = tokenizer.decode(seg1)
            lst.append(seg1_text)
    else:
        lst.append(text)
    return lst

def generate_gpt2_subset(old_month, new_month):
    # Bring subset csv file
    fname = f"../TemporalWiki_datasets/Wikipedia_datasets/wikipedia_{old_month}_{new_month}_subset.csv"

    df = pd.read_csv(fname)

    empty_article = 0
    d = []

    for index, row in df.iterrows():
        text = row['text']
        title = row['title']
        if text!='':
            entries = process_article(title, text)
            d = d + entries
        else:
            empty_article+=1
    output_dir = f"../TemporalWiki_datasets/Wikipedia_datasets/wikipedia_{old_month}_{new_month}_gpt2.csv"
    pd.DataFrame(d, columns=['text']).to_csv(output_dir, index=False)

def generate_gpt2_data(month, tenth_digit):

    data_dir = f"../TemporalWiki_datasets/Wikipedia_datasets/{month}"

    lst = os.listdir(data_dir)
    lst.sort()

    empty_article = 0

    cnt=0
    start_from = tenth_digit * 10
    end_at = start_from + 10

    d = []

    print(f'Starting from {start_from}')
    for dir in lst:
        if cnt >= start_from and cnt < end_at:
            dir1 = data_dir+'/'+dir 
            print(dir1)
            lst1 = os.listdir(dir1)
            lst1.sort()
            for file in lst1:
                full_dir = dir1+'/'+file 
                data = pd.read_json(full_dir,lines=True)
                for index, row in data.iterrows():
                    title = row['title']
                    text = row['text']
                    if text!='':
                        entries = process_article(title, text)
                        d = d + entries
                    else:
                        empty_article+=1
            output_dir = f"../TemporalWiki_datasets/Wikipedia_datasets/{month}_gpt2/{dir}.csv"
            pd.DataFrame(d, columns=['text']).to_csv(output_dir, index=False)
            d = []
        cnt+=1
        
def combine_csv(month):
    
    data_dir = f"../TemporalWiki_datasets/Wikipedia_datasets/{month}_gpt2"

    lst = os.listdir(data_dir)
    lst.sort()

    df1 = pd.DataFrame()

    for dir in lst:
        print(dir)
        full_dir = data_dir + '/' + dir
        df = pd.read_csv(full_dir)
        df1 = pd.concat([df1, df], axis=0)
    
    output_dir = f"../TemporalWiki_datasets/Wikipedia_datasets/{month}_gpt2/wikipedia_{month}_gpt2.csv"
    df1.to_csv(output_dir, index=False)

def size_of_wikipedia(month):
    data_dir = f"../TemporalWiki_datasets/Wikipedia_datasets/{month}"

    lst = os.listdir(data_dir)
    lst.sort()
    cnt = 0

    for dir in lst:
        cnt += 1
    return cnt

def preprocess_corpus(text):
    # from full file
    text = text.replace("&amp;", "")
    text = text.replace("&amp", "")
    text = re.sub('lt(.)*gt;', '', text)
    text = text.replace('&gt;', "")
    text = text.replace('&g', "")
    text = text.replace('gt;', "")
    text = text.replace('.&', ". ")
    text = text.replace(',&', ", and")
    text = text.replace('&lt;', "")
    text = text.replace('&lt', "")
    text = text.replace('\\new', "")
    text = text.replace('\cresc', "")
    text = text.replace('\override', "")
    text = text.replace('\\relative', "")
    text = text.replace('\clef', "")
    text = text.replace('\!', "")
    text = text.replace('\key', "")
    text = text.replace('\\time', "")
    text = text.replace('\once', "")
    text = text.replace('\ottava', "")
    text = text.replace('\set', "")
    text = text.replace('<unk>', "")
    text = text.replace('\\bar', "")
    text = text.replace('\stemUp', "")
    text = text.replace('\markup', "")
    text = text.replace('\stemDown', "")
    text = text.replace('\\voice', "")
    text = text.replace(' [. ', " ")
    text = text.replace(' [. ', " ")
    text = text.replace(' ]. ', " ")
    text = text.replace('  [.', " ")
    text = re.sub('-[0-9]+.[0-9]+.', '', text)
    text = re.sub('[0-9]+.[0-9]+.', '', text)
    text = re.sub('style=(.)* ', '', text)
    text = text.replace('.   ', ".")
    for _ in range(5):
        text = text.replace('  ', " ")
    text = text.replace('..', ".")
    text = text.replace('. . ', " ")
    text = text.replace('. . ', " ")
    text = re.sub('!align=(.)*|', '', text)
    text = re.sub('!align=(.)* ', '', text)
    text = re.sub('valign=(.)*|', '', text)
    text = re.sub('valign=(.)* ', '', text)
    text = re.sub('align=(.)*|', '', text)
    text = re.sub('align=(.)* ', '', text)
    text = re.sub('colspan=(.)*|', '', text)
    text = re.sub('colspan=(.)* ', '', text)
    text = re.sub('rowspan=(.)*|', '', text)
    text = re.sub('rowspan=(.)* ', '', text)
    text = re.sub('!width=(.)*|', '', text)
    text = text.replace('width= ', "")
    for _ in range(5):
        text = text.replace('..', ".")
    text = text.replace('.!', ".")
    text = text.replace('. ', '.')
    text = text.replace('.', '. ')
    text = text.strip()
    if len(text) == 1 and (text[0] == '.' or text[0] == '[' or text[0] == ']'):
        text = ""
    return text

def final_preprocess(old_month, new_month, mode):
    if mode == "subset":
        fname = f"../TemporalWiki_datasets/Wikipedia_datasets/wikipedia_{old_month}_{new_month}_gpt2.csv"
    else:
        fname = f"../TemporalWiki_datasets/Wikipedia_datasets/{old_month}_gpt2/wikipedia_{old_month}_gpt2.csv"
    s_dir = pd.read_csv(fname)
    text_file = s_dir.values.tolist()

    new_list = []
    for i in text_file: 
        new_list.append([preprocess_corpus(str(i[0]))])

    MAX_LENGTH = 1024
    out = []
    now = []
    rest = []
    for t in new_list:
        try:
            target_str = [' ' + str(t[0])]
            text_ids = tokenizer(target_str)['input_ids'][0]
        except:
            continue
        for ids in text_ids:
            now.append(ids)
        while len(now) >= MAX_LENGTH:
            rest = now[MAX_LENGTH:]
            now = now[:MAX_LENGTH]
            now_str = tokenizer.decode(now)
            if now_str[0] == ' ':
                now_str = now_str[1:]
            out.append([now_str])
            now = []
            for i in rest:
                now.append(i)
            rest = []

    now_str = tokenizer.decode(now)
    if now_str[0] == ' ':
        now_str = now_str[1:]
    out.append([now_str])
    pd.DataFrame(out, columns=['text']).to_csv(fname, index=False)

def main():
    arg = construct_generation_args()

    mode = arg.mode

    if mode == "subset": # mode : 0 (generate datasets for only subsets)
        old = arg.old # old : year + month + date, e.g. 20210801
        new = arg.new # new : year + month + date, e.g. 20210901
        print("Generating subset mode. Make sure you typed in \"old\" and \"new\" in command line")
        generate_subsets_csv(old, new)
        wikipedia_csv_to_json(old, new, 0)
        generate_unchanged_csv(old, new)
        wikipedia_csv_to_json(old, new, 1)
        print("Generating subsets and unchanged in csv, json file completed!") # Ready to be aligned with Wikidata

        generate_gpt2_subset(old, new)
        final_preprocess(old, new, mode)
        print("Generating GPT-2 training datasets for subsets is completed!") # Final Wikipedia subsets for training GPT-2
    elif mode == "entire": # mode : 1 (generate datasets for entire datasets)
        tenth_digit = arg.tenth_digit # tenth_digit : One number between 0-16 (There are 16 sets of Wikipedia bundle)
        month = arg.month # month : year + month + date, e.g. 20210801
        try:
            w_path = f"Wikipedia_datasets/{month}_gpt2"
            os.makedirs(w_path, exist_ok=False)
        except:
            pass
        
        wikipedia_size = size_of_wikipedia(month)
        generate_gpt2_data(month, tenth_digit)
        
        data_dir = f"../TemporalWiki_datasets/Wikipedia_datasets/{month}_gpt2"
        lst = os.listdir(data_dir)
        lst.sort()
        cnt = 0
        for dir in lst:
            cnt += 1
        if wikipedia_size == cnt:
            combine_csv(month)
            print("Datasets", tenth_digit, "has been completed.")
            final_preprocess(month, "0", mode)
            print("Generating GPT-2 training datasets for entire data is completed!") # Final Wikipedia datasets for training GPT-2
        else:
            print("Datasets", tenth_digit, "has been completed. Please wait for others to finish")
        
if __name__ == "__main__":
    main()

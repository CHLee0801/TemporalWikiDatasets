import argparse
import json
from qwikidata.json_dump import WikidataJsonDump
from wikidata.client import Client

SUPPORT_MODE = ["unchanged", "new", "updated"]

client = Client()

def construct_generation_args():

    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', type=str, default="unchanged", required=True, choices=SUPPORT_MODE)
    parser.add_argument('--old', type=str, default='20210801')
    parser.add_argument('--new', type=str, default='20210901')
    parser.add_argument('--idx', type=int, default=0)
    parser.add_argument('--combine', type=int, default=0)

    arg = parser.parse_args()
    return arg

def extraction(month, idx):
    dump_location = f"../TemporalWiki_datasets/Wikidata_datasets/wikidata-{month}.json.gz"

    wjd = WikidataJsonDump(dump_location)

    big_list = {}

    for ii, entity_dict in enumerate(wjd):
        small_list = []
        entity_id = entity_dict["title"]
        s = int(entity_id[1:])
        if s < idx*1000000:
            continue
        if s >= idx*1000000 + 1000000:
            break
        texts = entity_dict["section_texts"][0]
        index = -1
        while True:
            index = texts.find("wikibase-entity", index + 1)
            target = texts[index-200:index]
            idx1 = target.find("\"property\"")
            idx2 = target.find("hash")
            idx3 = target.find("\"id\":\"")
            idx4 = target.find(",\"type\":")
            relation = target[idx1+12: idx2-3]
            objective = target[idx3+6: idx4-2]
            if relation == "" or objective == "":
                pass
            elif "\"},\"type\":" in objective:
                small_list.append([relation, objective[:-10]])
            else:
                small_list.append([relation, objective])
            if index == -1:
                break
        small_list = small_list[:-1]
        semi_result = []
        for i in small_list:
            if i not in semi_result:
                    semi_result.append(i)
        big_list[entity_id] = semi_result

    idx = str(idx)
    output_dir = f"../TemporalWiki_datasets/Wikidata_datasets/{month}/{month}_{idx}.json"

    with open(output_dir, "w") as write_json_file:
        json.dump(big_list, write_json_file, indent=4)

def id(old, new, idx, mode):
    old_address = f"../TemporalWiki_datasets/Wikidata_datasets/{old}/{old}_{idx}.json"
    new_address = f"../TemporalWiki_datasets/Wikidata_datasets/{new}/{new}_{idx}.json"
    output_dir = f"../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/{mode}/{mode}_id/{mode}_{idx}_id.json"
    with open(old_address, "r") as read_json_file_1:
        previous_python = json.load(read_json_file_1)

    with open(new_address, "r") as read_json_file_2:
        present_python = json.load(read_json_file_2)

    if mode == "unchanged":
        unchanged_relation = []
        for entity in previous_python:
            if entity in present_python:
                small = []
                for first_relation in previous_python[entity]:
                    small.append(first_relation)
                for second_relation in present_python[entity]:
                    if second_relation in small:
                        unchanged_relation.append([entity] + second_relation)
 
        with open(output_dir, "w") as write_json_file:
            json.dump(unchanged_relation, write_json_file, indent=4)

    elif mode == "new":
        new_relation = []
        for entity in previous_python:
            if entity in present_python:
                small = []
                for first_relation in previous_python[entity]:
                    if first_relation[0] not in small:
                        small.append(first_relation[0])
                for second_relation in present_python[entity]:
                    if second_relation[0] not in small:
                        if [entity, second_relation[0], second_relation[1]] not in new_relation:
                            new_relation.append([entity, second_relation[0], second_relation[1]])

        with open(output_dir, "w") as write_json_file:
            json.dump(new_relation, write_json_file, indent=4)

    elif mode == "updated":
        updated_lama = []
        for entity in previous_python:
            if entity in present_python:
                small = []
                new_rel = []
                for first_relation in previous_python[entity]:
                    if first_relation[0] not in small:
                        small.append(first_relation[0])
                for second_relation in present_python[entity]:
                    if second_relation[0] not in small:
                        new_rel.append(second_relation[0])
                same = []
                for i in previous_python[entity]:
                    for j in present_python[entity]:
                        if i == j:
                            same.append(i)
                new_prev = []
                new_pres = []
                for i in previous_python[entity]:
                    if i not in same:
                        new_prev.append(i)
                for i in present_python[entity]:
                    if i not in same:
                        if i[0] not in new_rel:
                            new_pres.append(i)
                included = []
                for first_relation in new_prev:
                    relation = first_relation[0]
                    object = first_relation[1]
                    if len(object) > 15:
                        continue
                    for second_relation in new_pres:
                        if relation == second_relation[0]:
                            if len(second_relation[1]) > 15:
                                continue
                            if object != second_relation[1]:
                                updated_lama.append([entity] + first_relation + [second_relation[1]])
                                included.append(second_relation)
                for i in new_pres:
                    if i not in included:
                        updated_lama.append([entity] + i)

        with open(output_dir, "w") as write_json_file:
            json.dump(updated_lama, write_json_file, indent=4)     

def name(old, new, idx, mode):
    id_dir = f"../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/{mode}/{mode}_id/{mode}_{idx}_id.json"
    item_dir = f"../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/{mode}/{mode}_item/{mode}_{idx}_item.json"

    with open(id_dir, "r") as read_json_file_1:
        id_list = json.load(read_json_file_1)
    with open(f"../TemporalWiki_datasets/Property_string.json", "r") as read_dictionary:
        property_dict = json.load(read_dictionary)
    entity_dict = {}
    big_list = []
    new_id = []
    if mode == "updated":
        for i in id_list:
            if len(i) == 3:
                sub = i[0]
                rel = i[1]
                obj = i[2]
                if sub in entity_dict:
                    a1 = entity_dict[sub]
                else:
                    try:
                        entity = client.get(sub, load=True)
                    except:
                        continue
                    l = str(entity)[24:-2]
                    try:
                        a, b = l.split()
                        b = b[1:]
                        entity_dict[a] = b
                        a1 = b
                    except:
                        a = l.split()[0]
                        b = l.split()[1:]
                        s = ""
                        for j in b:
                            s += j + " "
                        s = s[1:-1]
                        entity_dict[a] = s
                        a1 = s

                if obj in entity_dict:
                    a3 = entity_dict[obj]
                else:
                    try:
                        entity = client.get(obj, load=True)
                    except:
                        continue
                    l = str(entity)[24:-2]
                    try:
                        a, b = l.split()
                        b = b[1:]
                        entity_dict[a] = b
                        a3 = b
                    except:
                        try:
                            a = l.split()[0]
                        except:
                            continue
                        b = l.split()[1:]
                        s = ""
                        for j in b:
                            s += j + " "
                        s = s[1:-1]
                        entity_dict[a] = s
                        a3 = s
                if len(a3.split()) > 5:
                    continue
                if rel in property_dict:
                    a2 = property_dict[rel]
                else:
                    continue
                big_list.append([a1, a2, a3])
                new_id.append(i)

            elif len(i) == 4:
                sub = i[0]
                rel = i[1]
                obj = i[2]
                obj2 = i[3]
                if sub in entity_dict:
                    a1 = entity_dict[sub]
                else:
                    try:
                        entity = client.get(sub, load=True)
                    except:
                        continue
                    l = str(entity)[24:-2]
                    try:
                        a, b = l.split()
                        b = b[1:]
                        entity_dict[a] = b
                        a1 = b
                    except:
                        a = l.split()[0]
                        b = l.split()[1:]
                        s = ""
                        for j in b:
                            s += j + " "
                        s = s[1:-1]
                        entity_dict[a] = s
                        a1 = s

                if obj in entity_dict:
                    a3 = entity_dict[obj]
                else:
                    try:
                        entity = client.get(obj, load=True)
                    except:
                        continue
                    l = str(entity)[24:-2]
                    try:
                        a, b = l.split()
                        b = b[1:]
                        entity_dict[a] = b
                        a3 = b
                    except:
                        try:
                            a = l.split()[0]
                        except:
                            continue
                        b = l.split()[1:]
                        s = ""
                        for j in b:
                            s += j + " "
                        s = s[1:-1]
                        entity_dict[a] = s
                        a3 = s
                if len(a3.split()) > 5:
                    continue
                if obj2 in entity_dict:
                    a4 = entity_dict[obj2]
                else:
                    try:
                        entity = client.get(obj2, load=True)
                    except:
                        continue
                    l = str(entity)[24:-2]
                    try:
                        a, b = l.split()
                        b = b[1:]
                        entity_dict[a] = b
                        a4 = b
                    except:
                        try:
                            a = l.split()[0]
                        except:
                            continue
                        b = l.split()[1:]
                        s = ""
                        for j in b:
                            s += j + " "
                        s = s[1:-1]
                        entity_dict[a] = s
                        a4 = s
                if len(a4.split()) > 5:
                    continue
                if a3.lower() == a4.lower():
                    continue
                if rel in property_dict:
                    a2 = property_dict[rel]
                else:
                    continue
                big_list.append([a1, a2, a4])
                new_id.append([i[0], i[1], i[3]])

        new_big_list = []
        new_big_id_list = []
        for i in range(len(big_list)):
            if big_list[i] not in new_big_list:
                new_big_list.append(big_list[i])
                new_big_id_list.append(new_id[i])

        with open(item_dir, "w") as write_json_file:
            json.dump(new_big_list, write_json_file, indent=4)

        with open(id_dir, "w") as write_json_file_2:
            json.dump(new_big_id_list, write_json_file_2, indent=4)
    else:
        cnt = 0
        for i in id_list:
            cnt += 1
            sub = i[0]
            rel = i[1]
            obj = i[2]
            if sub in entity_dict:
                a1 = entity_dict[sub]
            else:
                try:
                    entity = client.get(sub, load=True)
                except:
                    continue
                l = str(entity)[24:-2]
                try:
                    a, b = l.split()
                    b = b[1:]
                    entity_dict[a] = b
                    a1 = b
                except:
                    a = l.split()[0]
                    b = l.split()[1:]
                    s = ""
                    for j in b:
                        s += j + " "
                    s = s[1:-1]
                    entity_dict[a] = s
                    a1 = s

            if obj in entity_dict:
                a3 = entity_dict[obj]
            else:
                try:
                    entity = client.get(obj, load=True)
                except:
                    continue
                l = str(entity)[24:-2]
                try:
                    a, b = l.split()
                    b = b[1:]
                    entity_dict[a] = b
                    a3 = b
                except:
                    try:
                        a = l.split()[0]
                    except:
                        continue
                    b = l.split()[1:]
                    s = ""
                    for j in b:
                        s += j + " "
                    s = s[1:-1]
                    entity_dict[a] = s
                    a3 = s
            if len(a3.split()) > 5:
                continue
            if rel in property_dict:
                a2 = property_dict[rel]
            else:
                continue
            big_list.append([a1, a2, a3])
            new_id.append(i)
            
        with open(item_dir, "w") as write_json_file:
            json.dump(big_list, write_json_file, indent=4)

        with open(id_dir, "w") as write_json_file_2:
            json.dump(new_id, write_json_file_2, indent=4)

def merge(old, new, mode):

    big_id_list = []
    big_item_list = []
    for i in range(100):
        s = str(i)
        id_dir = f"../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/{mode}/{mode}_id/{mode}_{s}_id.json"
        item_dir = f"../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/{mode}/{mode}_item/{mode}_{s}_item.json"
        try:
            with open(id_dir, "r") as read_json_1:
                id_list = json.load(read_json_1)
            with open(item_dir, "r") as read_json_2:
                item_list = json.load(read_json_2)
            if len(id_list) != len(item_list):
                continue
            for k in id_list:
                big_id_list.append(k)
            for j in item_list:
                big_item_list.append(j)
        except:
            continue
    id_fname = "../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/{mode}/total_{mode}_id.json"
    item_fname = "../TemporalWiki_datasets/Wikidata_datasets/{old}_{new}/{mode}/total_{mode}_item.json"
    with open(id_fname, "w") as write_json_file_1:
        json.dump(big_id_list, write_json_file_1, indent=4) 
    with open(item_fname, "w") as write_json_file_2:
        json.dump(big_item_list, write_json_file_2, indent=4)
        
def main():
    arg = construct_generation_args()

    mode = arg.mode # mode : unchanged / updated / new
    if mode != "unchanged" and mode != "updated" and mode != "new":
        print("You typed in wrong mode!")
        exit()

    old = arg.old # old : year + month + date, e.g. 20210801
    new = arg.new # new : year + month + date, e.g. 20210901
    idx = arg.idx # idx : One number between 0-100 (Preprocessing is held in every million entities of Wikidata)
    combine = arg.combine # combine : 0 (Not combining created sets by idx) / 1 (Combine all the sets to one json file)

    if idx != -1:
        extraction(old, idx) # Extract Wikidata id of previous month
        extraction(new, idx) # Extract Wikidata id of new month
        id(old, new, idx, mode) # Filter Unchanged, Updated or New factual instances by id
        name(old, new, idx, mode) # Mapping id to string item by using 'WikiMapper'

    if combine == 1:
        merge(old, new, mode) 
        
if __name__ == '__main__':
    main()

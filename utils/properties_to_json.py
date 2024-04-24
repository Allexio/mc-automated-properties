"""This script allows the user to generate json files as seen in input-jsons from their X.properties files."""

from json import dump # needed to write to .json files
from os.path import exists # needed to check if there already are .properties files present
from os import mkdir # needed to create the output file

def initial_loader():
    """Loads the initial properties files, merges them into one single python dictionary with no additional processing"""
    object_types = ["block", "item", "entity"]
    unified_raw_data = {}
    for object_type in object_types:
        file = open(mode="r", file=object_type + ".properties")
        raw_data_lines = file.readlines()
        unified_raw_data[object_type] = {}
        for line in raw_data_lines:
            if "=" in line and "#" not in line: # if I care about this line 
                # add it to the dictionary in list format
                unstripped_data = line[line.find("=")+2:].split(" ")
                stripped_data = [s.strip() for s in unstripped_data]
                unified_raw_data[object_type][int(line[line.find(".")+1:line.find(".")+6])] = stripped_data    
    return unified_raw_data

def sort_by_mod(unified_raw_data: dict) -> dict:
    """Changes formats to something closer to the json one

    Args:
        unified_raw_data (dict): dict of the following format:
        "block": {
            100XX: ["mod_id:xxxxx", "xxxx:xxxx"]
        }

    Returns:
        sorted_data (dict): dict of the following format:
        "mod_id": {
            "block": {
                100XX: ["xxxxx", "xxxxx"]
            }
        }
    """
    sorted_data = {}
    
    for object_type in unified_raw_data:
        for object_id in unified_raw_data[object_type]:
            for object in unified_raw_data[object_type][object_id]:
                if ":" not in object: # that means it's a vanilla object
                    object = "minecraft:" + object # so I add the minecraft: prefix
                mod_id = object[:object.find(":")]
                object_name = object[object.find(":")+1:]
                if mod_id not in sorted_data:
                    sorted_data[mod_id] = {"block": {}, "item": {}, "entity": {}}
                if object_id not in sorted_data[mod_id][object_type]:
                    sorted_data[mod_id][object_type][object_id] = []
                sorted_data[mod_id][object_type][object_id].append(object_name)
    return sorted_data

def json_write(sorted_data: dict):
    """Initialises and writes to a new json file for each mod / vanilla
    """
    try:
        mkdir("./output")
    except FileExistsError:
        print("INFO: output folder already exists, skipping creation...")
    for mod_id in sorted_data:
        clean_json = {
            "name": mod_id,
            "description": "[please fill me in]",
            "id": mod_id,
            "version": "",
            "author": "",
            "data": sorted_data[mod_id]
        }
        with open("./output/"+mod_id+".json", "w") as output_file:
            dump(clean_json, output_file)

### Code execution starts here

#check_existing_file()
raw_data = initial_loader()
sorted_data = sort_by_mod(raw_data)
json_write(sorted_data)
print("Done.")
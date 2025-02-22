import json # needed to load the .json files
from os import listdir, mkdir # needed to list the .toml files in the folder and create the ouput folder
from tomllib import load

def loader() -> dict:
    """Generates dictionary with all the information from local json files

    Returns:
        dict: dictionary containing all the information in each json, key corresponds to filename
    """
    data_dict = {}  # initialise the dict
    for file in listdir("./input_jsons"):

        if ".json" not in file or file == "template.json":  # ignore non json files
            continue

        toml_dict = {}

        json_data = json.load(open("./input_jsons/" + file))  # load json from file into a python dict
        # add mod ID to block IDs
        print("INFO: Loading data from " + json_data["name"])
        toml_dict["name"] = json_data["name"]
        toml_dict["description"] = json_data["description"]
        toml_dict["id"] = json_data["id"]
        
        for object_type in json_data["data"]:  # item/entity/block
            toml_dict[object_type] = {}
            for object in json_data["data"][object_type]:  # dictionaries with an id and affected blocks
                category, key = object_id_to_string(object["object_id"])
                if category not in toml_dict[object_type]:
                    toml_dict[object_type][category] = {}
                
                toml_dict[object_type][category][key] = object["affected_objects"]
        print(toml_dict)

        with open('./v2_json/' + file, 'w') as f:
            json.dump(toml_dict,f)

    return toml_dict

def object_id_to_string(object_id: int) -> str:
    with open("./shader_mappings/photon.toml", 'rb') as f:
        photon_mapping = load(f)
    for mapping_category in photon_mapping:
        if mapping_category == "name" or mapping_category == "shaderpack_author" or mapping_category == "mapping_author" or mapping_category == "description":
            continue
        for key in photon_mapping[mapping_category]:
            if object_id == photon_mapping[mapping_category][key]:
                return mapping_category, key
    print("woops, couldn't find anything")
    return

data = loader()
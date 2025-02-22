from os import listdir, mkdir # needed to list the .toml files in the folder and create the ouput folder
from tomllib import load # needed to load the .toml files
from os.path import exists  # needed to check if there already are .properties files present


def loader() -> dict:
    """Generates dictionary with all the information from local toml files

    Returns:
        dict: dictionary containing all the information in each toml, key corresponds to filename
    """
    data_dict = {}  # initialise the dict
    for file in listdir("./input_tomls"):
        if ".toml" not in file or file == "template.toml":  # ignore non toml files
            continue
        filename = file[:file.find(".toml")]  # cut off the .toml
        toml_data = load(open("./input_tomls/" + file))  # load toml from file into a python dict
        # add mod ID to block IDs
        print("INFO: Loading data from " + toml_data["name"])
        current_mod_id = toml_data["id"]
        for object_type in toml_data["data"]:  # item/entity/block
            for object in toml_data["data"][object_type]:  # dictionaries with an id and affected blocks
                # add mod id in front of block ids
                object["affected_objects"] = [current_mod_id+":" + e for e in object["affected_objects"]]
        data_dict[filename] = toml_data["data"]
    return data_dict


def description_obtainer(vanilla_data: dict) -> dict:
    """Takes a dictionary of vanilla values and returns a dict containing the descriptions for each block ID

    Args:
        vanilla_data (dict): the vanilla toml in python dictionary format

    Returns:
        description_data (dict): a dictionary where the format is as follows:
        "block": {
            12345: "blabla",
            67890: "blublu"
        },
        "item": {etc.}
    """
    description_data = {}
    for block_type in vanilla_data:  # block/item/entity
        description_data[block_type] = {}  # instantiate the different dictionaries per block type
        for object in vanilla_data[block_type]:
            description_data[block_type][object["object_id"]] = object["description"]
    return description_data


def merger(data_dict: dict) -> dict:
    """takes a dictionary with multiple keys that correspond to different files and
    merges them to obtain a single dict with blocks and items directly

    Args:
        data_dict (dict): a dictionary where keys are derived from filenames:
            "chipped": {
                "block": [
                    "description": "blabla",
                    "object_id": 12345,
                    "affected_objects": "mod:block",
                ]
            }

    Returns:
        merged_dict: a dictionary where the different entries have been merged
        into one so that each block/item ID is unique
    """
    merged_dict = {"block": {}, "item": {}, "entity": {}}  # instanciate an empty dictionary for each object type
    for file_key in data_dict:  # filename minus .toml
        for object_type in data_dict[file_key]:  # block, item, entity
            for object in data_dict[file_key][object_type]:  # the actual object w/ desc, block_id, affected_blocks
                current_object_id = object["object_id"]  # the ID of the current block. ex: 10032.
                current_affected_blocks = object["affected_objects"]  # the list of blocks in the current structure
                current_object_id = object["object_id"]  # the ID of the current block. ex: 10032.
                if current_object_id not in merged_dict[object_type]:
                    merged_dict[object_type][current_object_id] = []
                full_object_id_list = current_affected_blocks  # if from vanilla minecraft, don't add mod ID
                merged_dict[object_type][current_object_id].extend(full_object_id_list)
    return merged_dict


def check_existing_file():
    """Checks if there is already a properties file in the directory.
    If yes, asks user confirmation to overwrite. If user declines, exits the program.
    """
    confirmation_needed = False
    for object_type in ["entity", "item", "block"]:
        if exists("./output/" + object_type + ".properties"):
            print("WARNING: there is already a " + object_type + ".properties file in the output directory!")
            confirmation_needed = True
    if confirmation_needed:
        user_confirmation = input("Do you wish to overwrite?")
        if user_confirmation in ["y", "yes", "confirm", "overwrite", "ok"]:
            return
        else:
            exit(0)
    else:
        return


def sort_by_id(merged_dict: dict) -> dict:
    """Sort a merged dict by object ID (from 10001 to XXXXX)
    This serves no functional purpose and serves only to make the output file more readable and consistent

    Args:
        merged_dict (dict): the merged dict with all the information needed

    Returns:
        sorted_dict (dict): the same dict, just with the keys sorted in increasing order
    """
    sorted_dict = {"block": {}, "item": {}, "entity": {}}
    for object_type in merged_dict:
        sorted_dict[object_type] = dict(sorted(merged_dict[object_type].items()))
    return sorted_dict


def writer(merged_dict: dict, description_data: dict):
    """Takes a merged dict and writes to local x.properties files

    Args:
        blocks_to_write (dict): a dictionary containing the blocks
    """
    try:
        mkdir("./output")
    except FileExistsError:
        print("INFO: output folder already exists, skipping creation...")

    for object_type in merged_dict:  # block/item/entity
        print("INFO: Writing data to ./output/" + object_type + ".properties")
        output_string = ""
        for block_id in merged_dict[object_type]:
            try:
                output_string += "\n\n# " + description_data[object_type][block_id]  # add the description on top
            except KeyError:
                output_string += "\n\n# no description provided"  # no description in vanilla file
            output_string += "\n" + object_type + "." + str(block_id) + " = " + \
                " ".join(merged_dict[object_type][block_id])  # add the block ID and affected blocks
        file = open(mode="w", file="./output/"+object_type+".properties")
        file.write(output_string)
        file.close()


# Code execution starts here


check_existing_file()
raw_data = loader()
description_data = description_obtainer(raw_data["vanilla"])
merged_dict = merger(raw_data)
sorted_dict = sort_by_id(merged_dict)
writer(sorted_dict, description_data)
print("Done.")

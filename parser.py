# parser.py
# Gabriel Krotkov
# This script is intended to facilitate breaking .json files up into more 
# managable chunks for another tool like R to import and analyze.
# Last Update: 1/31/2022

import os
import sys
import json
import pandas as pd

##########################
#### Helper Functions ####
##########################

# ASSUMPTION: directory has no directories
def clear_dir(dir):
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))

# non-pandas line by line reading of a json line separated file in utf8 encoding
# 
def read_jl_lines(filepath):
    file = open(filepath, "r", encoding = "utf8")
    lines = []
    for line in file:
        lines.append(json.loads(line))
    file.close()

#####################
#### Driver Code ####
#####################

# The user must define how many splits they want in the data. 
# The program will evenly divide the number of json objects in the input file
# but will not account for varying size of json objects.
splits = int(input("How many splits?"))
message = "If you don't need to split the data, don't run this script."
assert(splits > 1, message)
filepath = "data/full zendesk 042020.json"

data = pd.read_json(filepath, lines=True)

clear_dir("data/splits")

# compute the length required for each of the split dataframes.
# The mod solution presented here is not perfect but is only separated from 
# perfect by (splits - 1) json objects, which is negligible on this scale.
split_length = len(data) // splits
for i in range(splits):
    tmp = data[(split_length * i):(split_length * (i + 1))]
    if (i == splits - 1): # if last iteration, take all the remaining data
        tmp = data[(split_length * 1):]
    target = f"data/splits/split{i + 1}.json"
    tmp.to_json(target, orient = "records", force_ascii = False, lines = True)
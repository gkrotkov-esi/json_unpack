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
def read_jl_lines(filepath):
    file = open(filepath, "r", encoding = "utf8")
    lines = []
    for line in file:
        lines.append(json.loads(line))
    file.close()

# colnames must be a list of strings, legal column names for the pandas 
# dataframe data
def get_columns(data, colnames):
    return data[colnames]

# wrapper function for pandas syntax, gets column names of a dataframe
def get_colnames(data):
    return list(data.columns)

def export(data, name = "output", target = None):
    if (target == None):
        target = f"data/parser_output/{name}.json"
    data.to_json(target, orient = "records", 
                 force_ascii = False, lines = True)

# The user must define how many splits they want in the data. 
# The program will evenly divide the number of json objects in the input file
# but will not account for varying size of json objects.
def split_data(data, splits):
    clear_dir("data/parser_output")
    assert(splits > 1, "Need splits > 1")
    split_length = len(data) // splits
    # send split data to data/splits
    for i in range(splits):
        tmp = data[(split_length * i):(split_length * (i + 1))]
        if (i == splits - 1): # if last iteration, take all the remaining data
            tmp = data[(split_length * 1):]
        target = f"data/parser_output/split{i + 1}.json"
        tmp.to_json(target, orient = "records", 
                    force_ascii = False, lines = True)

# splits should be the # of splits desired if provided
def export_comments(data, splits = False):
    # select down the data to only these columns
    data = get_columns(data, ["id", "comments"])
    if(splits):
        split_data(data, splits)
    else:
        export(data, "comments")

#####################
#### Driver Code ####
#####################
# can adjust this to default to looping through all files in parser_input?
filepath = "data/parser_input/" + os.listdir("data/parser_input")[0]
data = pd.read_json(filepath, lines=True)
export_comments(data)
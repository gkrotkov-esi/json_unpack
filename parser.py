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

# Replicates the "which" inbuilt function from R
def which(lst, condition = True):
    idx = []
    for i in range(len(lst)):
        if lst[i] == condition:
            idx.append(i)
    return idx

# dirpath - the path to the parser input directory
def get_extensions(dirpath = "data/parser_input"):
    files = os.listdir(dirpath)
    extensions = []
    for file in files:
        extensions.append(file.split(".")[1])
    return extensions

# given a filepath, loads that file as a json into a pandas df
def load_json(filepath):
    return pd.read_json(filepath, lines = True)

def load_csv(filepath):
    return pd.read_csv(filepath)

# can adjust these to loop through all files in parser_input?


# gets the first .json file in the input directory
def load_first_json(dirpath = "data/parser_input"):
    extensions = get_extensions(dirpath)
    files = os.listdir(dirpath)
    idx = which(extensions, "json")
    filepath = dirpath + "/" + files[idx[0]]
    return load_json(filepath)

# returns the first .csv file in the input directory
def load_first_csv(dirpath = "data/parser_input"):
    extensions = get_extensions(dirpath)
    files = os.listdir(dirpath)
    idx = which(extensions, "csv")
    filepath = dirpath + "/" + files[idx[0]]
    return load_csv(filepath)

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
    assert splits > 1, "called split_data without a valid # of splits"
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

########################
#### Test functions ####
########################

def test_which():
    print("Testing function 'which'...", end = "")
    assert(which([True, False]) == [0])
    assert(which([1, 7, 1, 2], 1) == [0, 2])
    assert(which([]) == [])
    assert(which([1]) == [0])
    print("passed!")

def test_all():
    test_which()

def veros_operation():
    data_json = load_first_json()
    data_csv = load_first_csv()
    # want to merge json and csv on id
    export_comments(data)

def main():
    data = load_first_json()
    export_comments(data)

#####################
#### Driver Code ####
#####################
test_all()
#main()

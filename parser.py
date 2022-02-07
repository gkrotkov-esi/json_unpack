# parser.py
# Gabriel Krotkov
# This script is intended to facilitate breaking .json files up into more 
# managable chunks for another tool like R to import and analyze.
# Last Update: 1/31/2022

import os
import sys
import json
import pandas as pd
import numpy as np

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
    return list(data.comments)

def export(data, name = "output", filetype = "csv"):
    target = f"data/parser_output/{name}.{filetype}"
    if (filetype == "json"):
        data.to_json(target, orient = "records", 
                     force_ascii = False, lines = True)
        return
    if (filetype == "csv"):
        data.to_csv(target)
        return
    assert False, "unsupported file type in export fxn"

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

# to be applied to comment data
# input "thread" is a list of dictionaries, where each dict is an email
# fxn is destructive, returns None
def trim_thread_comments(thread, mode = "body"):
    for i in range(len(thread)):
        thread[i] = thread[i][mode]

# data - a pandas dataframe including a column titled "comments"
# ASSUMPTION: comments is a pandas Series of threads, each thread being a 
# list of emails, each represented as a dictionary
# mode - the value in each dictionary we want to extract; usually "body"
def trim_comments(data, mode = "body"):
    comments = data.comments
    comments.apply(trim_thread_comments, mode = mode)

# splits should be the # of splits desired if provided
# if splits are desired, required output is json.
def export_comments(data, target = "comments", filetype = "csv", 
                    splits = False):
    # select down the data to only these columns
    data = get_columns(data, ["id", "comments"])
    if(splits):
        split_data(data, splits)
    else:
        export(data, name = target, filetype = filetype)

# the merge is an inner join, so if a ticket exists in BOTH the .csv and the
# .json, then its comments will be represented.
def load_merged_data(customer = ""):
    data = load_first_json()
    tmp = load_first_csv()
    tmp = tmp.rename(columns = {"Id": "id", "Customer [list]": "customer"})
    tmp = get_columns(tmp, ["id", "customer"])
    # want to merge json and csv on id
    # id is capitalized in the csv and not in the json
    data = data.merge(tmp, how = "inner", on = "id")
    # filter by customer if requested
    if (customer != ""):
        data = data[data["customer"] == customer]
    return(data)

# uses numpy to flatten a list
def flatten(lst):
    return list(np.concatenate(lst).flat)

def flatten_comments(data):
    flattened = flatten(list(data.comments))
    lengths = data.comments.apply(len)
    idx = list(np.repeat(lengths.index, lengths.values))
    result = pd.DataFrame(data = {"id": idx, "comments": flattened})
    return result

def main():
    data = load_first_json()
    export_comments(data)

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

# checks to see whether all elements of the input list are dicts
def all_dicts(lst):
    lst = list(lst) # just in case a pandas series is input
    print("Testing all_dicts ...", end = "")
    for i in range(len(lst)):
        assert(isinstance(lst[i], dict))
    print("passed!")

def test_all():
    test_which()

#####################
#### Driver Code ####
#####################
test_all()
data = load_merged_data(customer = "US Cellular")
trim_comments(data)
export_comments(data)
# flatten comments, output again
data = flatten_comments(data)
export_comments(data, "flattened_emails")
#main()


# TODO: implement filtering by date
#    - which date?
#    - leave turned off
# TODO: (maybe) update load files to go through all files in parser_input?
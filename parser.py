# parser.py
# Gabriel Krotkov
# This script is intended to facilitate breaking .json files up into more 
# managable chunks for another tool like R to import and analyze.
# Last Update: 3/2/2022

import os
import sys
import json
import pandas as pd
import numpy as np

###########################
#### Utility Functions ####
###########################

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
        # use -1 instead of 1 in case the user uses periods in their
        # file name
        extensions.append(file.split(".")[-1])
    return extensions

# given a filepath, loads that file as a json into a pandas df
def load_json(filepath):
    return pd.read_json(filepath, lines = True)

def load_csv(filepath):
    return pd.read_csv(filepath)

# returns a JsonReader object for iteration
# n - chunksize; the number of rows we want in each chunk
def load_json_stream(filepath, n):
    return pd.read_json(filepath, lines = True, chunksize = n)

# dirpath - path to a directory
# extension_type - "json" or "csv" (string)
# n - the cardinal order of the filename we want to get
def get_filepath_by_type(dirpath, extension_type, n = 0):
    extensions = get_extensions(dirpath)
    files = os.listdir(dirpath)
    idx = which(extensions, extension_type)
    return dirpath + "/" + files[idx[n]]

# gets the first .json file in the input directory
def load_first_json(dirpath = "data/parser_input"):
    return load_json(get_filepath_by_type(dirpath, "json", 0))

# returns the first .csv file in the input directory
def load_first_csv(dirpath = "data/parser_input"):
    return load_csv(get_filepath_by_type(dirpath, "csv", 0))

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
# NOTE: this function is DESTRUCTIVE
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
    lookup = load_first_csv()
    lookup = lookup.rename(columns = {"Id": "id", 
                                      "Customer [list]": "customer"})
    lookup = get_columns(lookup, ["id", "customer"])
    # want to merge json and csv on id
    # id is capitalized in the csv and not in the json
    data = data.merge(lookup, how = "inner", on = "id")
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

#############################
#### Operation Functions ####
#############################

# will use camelCase for operation functions, snake_case for all other functions

# reads in merged data (requires both json and csv) for a single customer
# trims comments, exports in threaded format, flattens and exports unthreaded
# assumes that data does not need to be read in chunks
def singleCustomerReport(customer):
    data = load_merged_data(customer = customer)
    trim_comments(data)
    export_comments(data)
    data = flatten_comments(data)
    export_comments(data, "flattened_emails")

# for use when the json file is massive and requires a chunksize parameter
# returns the data merged and filtered by customer
# chunk - chunk of the large json file as read by a reader
# lookup - csv file with id and customer information
# customer - string value of the custumer we want to filter for
def singleCustomerReportChunk(chunk, lookup, customer = ""):
    data = chunk.merge(lookup, how = "inner", on = "id")
    if (customer != ""):
        data = data[data["customer"] == customer]
    return(data)

def singleCustomerReportChunks(customer, chunksize):
    dirpath = get_filepath_by_type("data/parser_input", "json")
    stream = load_json_stream(dirpath, chunksize)
    lookup = load_first_csv()
    lookup = lookup.rename(columns = {"Id": "id", "Customer [list]": "customer"})
    lookup = get_columns(lookup, ["id", "customer"])
    tickets = []
    for chunk in stream:
        tickets.append(singleCustomerReportChunk(chunk, lookup, customer))
    # flatten tickets
    tickets = pd.concat(tickets)
    trim_comments(tickets)
    export_comments(tickets)
    tickets = flatten_comments(tickets)
    export_comments(tickets, "flattened_emails")


def main():
    singleCustomerReportChunks(CUSTOMER_OF_INTEREST, CHUNKSIZE)

#####################
#### Driver Code ####
#####################
test_all()
CUSTOMER_OF_INTEREST = "US Cellular"
CHUNKSIZE = 1000
main()

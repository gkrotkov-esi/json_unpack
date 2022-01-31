# parser.py
# Gabriel Krotkov
# This script is intended to facilitate breaking .json files up into more 
# managable chunks for another tool like R to import and analyze.
# Getsize function adapted from Aaron Hall at
# https://stackoverflow.com/questions/449560/how-do-i-determine-the-size-of-an-object-in-python
# Last Update: 1/31/2022

import module_manager
module_manager.review()
import os
import sys
import json
import copy
from types import ModuleType, FunctionType
from gc import get_referents

# Custom objects know their class.
# Function objects seem to know way too much, including modules.
# Exclude modules as well.
BLACKLIST = type, ModuleType, FunctionType

def getsize(obj):
    """sum size of object & members."""
    if isinstance(obj, BLACKLIST):
        raise TypeError('getsize() does not take argument of type: '+ str(type(obj)))
    seen_ids = set()
    size = 0
    objects = [obj]
    while objects:
        need_referents = []
        for obj in objects:
            if not isinstance(obj, BLACKLIST) and id(obj) not in seen_ids:
                seen_ids.add(id(obj))
                size += sys.getsizeof(obj)
                need_referents.append(obj)
        objects = get_referents(*need_referents)
    return size

def cleanse_dir(filepath):
    for f in os.listdir(filepath):
        os.remove(os.path.join(filepath, f))

file = open("data/full zendesk 092020.json", "r", encoding = "utf8")

lines = []
for line in file:
    lines.append(json.loads(line))

total_size = getsize(lines)

# Now we want to write to data/split, which is our directory for holding split
# json files.
# We should be guaranteed that data/split does not have any directories.
# We first delete all the files in split
cleanse_dir("data/split")

# Next we're interested in splitting the data into more managable chunks
# This constant was taken from the size of a file that was successfully read
# into R; size not by system measurement but by the getsize fxn above.
CAP = 3900000000

size_counter = 0

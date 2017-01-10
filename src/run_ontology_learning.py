#!/usr/bin/python

"""
    this is the main script which calls the rest
    basically, it loads the model, gets the term candidates, and saves them for evaluation
    we use a sqlite3 DB to store the data and the ratings
"""

import fs_helpers, db
from config import *

# simple: connect to the sqlite DB
get_db()

# check if sqlite tables exists, else create them 
db.check_tables_exist(conf)

# check if seed terms already in DB -- if not, insert them 
db.check_initial_seeds(conf)

# find out in what iteration we are, load seed terms, etc
db.get_status(conf)

# load model
model = fs_helpers.load_model(conf) 

# use word2vec to get term candidates
candidates = model.most_similar(positive=conf['seeds'], topn=75)

# save the term candidates
db.save_candidates(conf, candidates)

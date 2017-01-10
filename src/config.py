#!/usr/bin/python

# you need to config this!
# set the model file, and if the model supports big-grams: set seed with bigrams..


## the conf dict stores all relevant config parameters

conf={}
conf['model'] = "climate2_2015_7.txt.2gram.small.model" # default dummy model
#conf['model'] = "climate2_2015_7.txt.2gram.model"



# if using a bigram model
conf['seedfn'] = "../data/climate.seed" # bigram seed for climate change models 

# config for hypernym extraction
conf['num_taxomy_best'] = 1 # number of most similar terms to consider when building a taxonomy
conf['sim_threshold'] = 0.40


# if using a unigram  model
#conf['seedfn'] = "../data/climate-single-word.seed"

#  config for hypernym extraction
#conf['num_taxomy_best'] = 3 # number of most similar terms to consider when building a taxonomy
#conf['sim_threshold'] = 0.23


conf['binary_model'] = True # default: using a binary word2vec model (like created by Mikolov's C implementation)
conf['domain'] = "climate change" # your domain of knowledge -- not important for the algorithms ..

########################################################################################################################

# no need to change below this
DB_PATH= "../data/our.db"
#DB_PATH= "/home/wohlg/workspace/dl4j-0.4-examples/src/main/java/MinicBac/python/data/our.db"

print "db-path", DB_PATH

import sqlite3
def get_db():
    """ just connect to the sqlite3 database """
    conf['db'] = sqlite3.connect(DB_PATH)


# model file name
conf['MFN'] = "../data/models/" + conf['model']

# setup logging
import logging, os
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

#!/usr/bin/python

import os
from config import *
import gensim.models



def load_judgements_from_fs(conf):
    """
        load the manual evalations from the file system
    """
    fn = "../data/to_check/" + conf['model'] + "step_" + str(conf['step']) + ".NEW"

    try: 
        lines = open(fn).readlines()
    except Exception, e:
        print "\n\n *** \n Please check in the data/to_check folder if there are terms to manually evaluate!!\n *** \n\n"
        raise e

    terms = [l.strip() for l in lines]
    return terms

def load_model(conf):
    """
        load the gensim model for usage 
    """

    # load model
    print "loading model", conf['MFN']

    if conf['binary_model']:
        model = gensim.models.Word2Vec.load_word2vec_format(conf['MFN'], binary=True)
    else:
        model = gensim.models.Word2Vec.load_word2vec_format(conf['MFN'], binary=False)
    model.init_sims(replace=True) # clean up RAM
    return model

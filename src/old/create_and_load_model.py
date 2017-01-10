#!/usr/bin/python

BASE="/home/wohlg/word2vec/trunk/"
#FN= BASE + "climate2_2015_7.txt" # unfiltered unigrams
FN= BASE + "climate2_2015_7.txt-norm1-phrase1"
end = FN.split("/")[-1].strip()
MFN="/home/wohlg/word2vec/trunk/my_onto/data/"+end


import gensim.models
# setup logging
import logging, os
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# train the basic model with text8-rest, which is all the sentences
# without the word - queen
# -cbow 1 -size 200 -window 8 -negative 25 -hs 0 -sample 1e-4 -threads 20 -binary 1 -iter 15

if (not os.path.isfile(MFN)):   

    model = gensim.models.Word2Vec(size=200, window=8, min_count=10, workers=4)
    sentences = gensim.models.word2vec.LineSentence(FN)
    model.build_vocab(sentences)
    model.train(sentences)
    model.save(MFN)

else:
    model = gensim.models.Word2Vec.load(MFN)

# Evaluation
print model.n_similarity(["king"], ["duke"])
print model.n_similarity(["king"], ["queen"])
print model.n_similarity(["climate"], ["greenhouse"])
print model.n_similarity(["king"], ["greenhouse"])
print "climate+greenhouse", model.most_similar(positive=['climate', 'greenhouse']) #, negative=['man'])
print "climate", model.most_similar(positive=['climate']) #, 'king'], negative=['man'])


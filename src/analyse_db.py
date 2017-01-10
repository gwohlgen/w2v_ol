#!/usr/bin/python

"""
    make some analysis on the contents of the DB
"""
import db
from config import *

# details?
PRINT_DETAILS=True

# simple: connect to the sqlite DB
get_db()
conn, model = conf['db'], conf['model']



# get models used

dbc = conn.cursor()

    # 1. which is the last step
dbc.execute("select distinct model from data")
models = [c[0] for c in dbc.fetchall()]

for model in models:
    # see if max_stage == 3, else continue
    dbc.execute("SELECT MAX(step) FROM data WHERE model='%s'" % (model,))
    if (dbc.fetchone()[0] != 3): continue

    # total number of concepts:
    dbc.execute("SELECT COUNT(*) FROM data WHERE model='%s' AND step IN (1,2,3)" % (model,))
    tot_num = dbc.fetchone()[0]
    if tot_num != 75: raise Exception

    # num releveant
    dbc.execute("SELECT COUNT(*) FROM data WHERE model='%s' AND step IN (1,2,3) AND relevant=1" % (model,))
    rel_num = dbc.fetchone()[0]

    print "\n\nNext model:", model, " -- Total number of concepts:", tot_num, "Num: relevant", rel_num , "Perc. relevant", rel_num / float(tot_num)

    if PRINT_DETAILS:
        for step in [1,2,3]:
            dbc.execute("SELECT term FROM data WHERE model='%s' AND step IN (%d) AND relevant=1" % (model, step))
            rel = [t[0] for t in dbc.fetchall()]
            print "\n\tStep: %d -- Number of relevant concepts: %d -- Percent: %f" % (step, len(rel), len(rel)/25.0)
            for t in rel:
                print "\t\t+ ", t

            dbc.execute("SELECT term FROM data WHERE model='%s' AND step IN (%d) AND relevant=0" % (model, step))
            nrel = [t[0] for t in dbc.fetchall()]
            for t in nrel:
                print "\t\t- ", t





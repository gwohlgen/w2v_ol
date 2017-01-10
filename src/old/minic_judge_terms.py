import sqlite3,os,subprocess

DBFILE="/home/wohlg/workspace/dl4j-0.4-examples/src/main/java/MinicBac/python/data/our.db"
conn = sqlite3.connect(DBFILE)
dbc = conn.cursor()

def get_and_save_terms():

    # get terms which are obviously not relevant (which were not in the pos_terms)
    dbc.execute("SELECT distinct term FROM data WHERE relevant IS NULL")
    res = dbc.fetchall()

    terms = [t[0] for t in res]
    print "number of terms", len(terms)

    # reuse existing judgements

    if terms:
        # write into a checkme file
        fn = "CHECK_ME"
        fh = open(fn, 'wb')
        for term in terms:
            fh.write(term.encode('utf-8') + "\n")

def load_and_save_terms():
    fn = "NEW" 

    if os.path.isfile(fn):
        lines = open(fn).readlines()
        terms = [l.strip() for l in lines]

        print "number of relevant terms", len(terms)

        for term in terms:
            # update db
            dbc.execute("UPDATE data SET relevant=1 WHERE term=? AND relevant IS NULL", (term,))
            conn.commit()

        dbc.execute("update data set relevant = 0 where relevant is null")
        conn.commit()

get_and_save_terms()
load_and_save_terms()
subprocess.call(["svn", "commit", "-m", "wohlg:new judgements", DBFILE])

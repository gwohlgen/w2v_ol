import os,sys
from config import *
import fs_helpers

def check_tables_exist(conf):
    """ those two tables are used 
    -- create a sqlite3 DB for them .."""

    dbc = conf['db'].cursor()

    data_table = """CREATE TABLE IF NOT EXISTS data (
                    id INTEGER PRIMARY KEY,
                    domain VARCHAR,
                    model VARCHAR,
                    term VARCHAR,
                    step INT,
                    relevant BOOLEAN); """

    checked_table = """
                CREATE TABLE IF NOT EXISTS checked_terms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain VARCHAR,
                    term VARCHAR,
                    relevant BOOLEAN
                ); """

    dbc.execute(data_table)
    dbc.execute(checked_table)


def get_status(conf):
    """ 
        Find out in what state we are, ie. what steps have been done, etc
        - are there unjudged terms? update with judgements from the file (if existings)
        - if all terms are judged, we can proceed to the next step, so we set the new seed terms
    """
    conn, domain, model = conf['db'], conf['domain'], conf['model']
    dbc = conn.cursor()

    # 1. which is the last step
    dbc.execute("SELECT MAX(step) FROM data WHERE domain='%s' AND model='%s'" % (domain, model))
    max_step = dbc.fetchone()[0]
    conf['step'] = max_step
    print "current max_step", max_step


    # see if there are unjudged terms in DB?  
    dbc.execute("SELECT COUNT(*) FROM data WHERE domain='%s' AND model='%s' AND relevant IS NULL" % (domain, model))
    c = dbc.fetchone()[0]

    if c>0:
        file_terms = fs_helpers.load_judgements_from_fs(conf)

        # step 1 # construct lists of relevant and not relevant-terms and update data table
        pos_terms, neg_terms, num_missing = update_data_table(conf, file_terms)

        # step 2 # insert into checked_terms table
        save_checked_terms(conf, pos_terms, neg_terms)

        # are there still unjudged terms? # TODO ? check in DB?
        fn =  "../data/to_check/" + conf['model'] + "step_" + str(conf['step']) + ".CHECK_ME"
        if (num_missing>0):
            print "\nTHERE ARE TERMS IN THE TABLE WITHOUT JUDGEMENT -- set relevance\n"
            print "See file:", fn, "\n"
            sys.exit()

    # everything done for this step
    if max_step == 3:
        print "\n\nstep 3 and everything judged -- we are finished"
        print "\n\nlet's try to create a taxonomy:" 
        generate_taxonomy(conf)
        sys.exit()

    # get current terms
    dbc.execute("SELECT term FROM data WHERE domain='%s' AND model='%s' AND relevant=1" % (domain, model))
    rows = dbc.fetchall()
    current_terms = [row[0] for row in rows]
    print "current_terms", current_terms

    ### set current seed terms -- for the next iteration!
    conf['seeds'] = current_terms 

def save_candidates(conf, candidates):
    """
        save the new candidates to the DB and to the filesystem (if unjudged candidates exist)
    """

    conn, domain, model, step = conf['db'], conf['domain'], conf['model'], conf['step']
    dbc = conn.cursor()

    inserted_terms = [] 
    for (term, sim) in candidates:

        # insert only 25 candidates max!
        if len(inserted_terms) >= 25: break

        # filters
        if term.find("'") >= 0:
            print "Filtering term", term
            continue

        # check if already exists
        dbc.execute("SELECT count(*) FROM data WHERE domain=? AND model=? AND term=?", (domain, model, term))
        if dbc.fetchone()[0]>0:
            print "term %s already exists!!! won't insert again" % (term)

        else:
            # insert a new term in to the DB
            dbc.execute("INSERT INTO data (domain, model, term, step) VALUES (?,?,?,?)", (domain, model, term, step+1))
            inserted_terms.append( (term,sim) )

    conn.commit()

    # reuse existing judgements
    unjudged_terms = set_judgements_from_existing(inserted_terms, conf)

    if unjudged_terms:
        # write into a checkme file
        fn = "../data/to_check/"+ conf['model'] + "step_" + str(conf['step']+1) + ".CHECK_ME"
        fh = open(fn, 'wb')
        for (term,sim) in unjudged_terms:
            fh.write(term.encode('utf-8') + "\n")
        

def set_judgements_from_existing(inserted_terms, conf):
    conn, domain, model = conf['db'], conf['domain'], conf['model']
    dbc = conn.cursor()

    unjudged_terms = []

    for (term, sim) in inserted_terms:
        dbc.execute("SELECT relevant FROM checked_terms WHERE domain=? AND term=?", (domain, term))

        # if found
        res = dbc.fetchone()
        if res: 
            dbc.execute("UPDATE data SET relevant=? WHERE domain=? AND model=? AND term=?", (res[0], domain, model, term))
            print "updating in set_judgements_from_existing -- term:", term, res[0]
        else:
            unjudged_terms.append( (term,sim) )

        conn.commit()

    return unjudged_terms

    

def check_initial_seeds(conf):
    """
        check that the initial seed concepts exist in the DB
        else: add them 
    """
    conn, domain, model = conf['db'], conf['domain'], conf['model']
    dbc = conn.cursor()

    dbc.execute("SELECT count(*) FROM data WHERE domain='%s' AND model='%s' AND step=0" % (domain, model))
    if dbc.fetchone()[0]==0:
        print "No seeds found for model: %s" % (model,)

        # read seeds from file
        seeds = [l.strip() for l in open(conf['seedfn']).readlines()]
        print "Using seeds from file:", seeds

        for term in seeds:
            dbc.execute("INSERT INTO data (domain, model , term, step, relevant) VALUES ('%s', '%s', '%s', 0, 1)" % (domain, model, term))
        conn.commit()

        print "Initial seeds entered in DB."
    else:
        print "Inital seeds exist."

def update_data_table(conf, pos_terms):
    """
        update the database with judgements given in the file
        the file only contains the positive judgements, so the rest must be the negative ("non-relevant") ones
        @pos_terms: the list of terms with judged as relevant (for the given "step")
        @returns: missing (unjudged) terms, if there are any
    """
    conn, domain, model, step = conf['db'], conf['domain'], conf['model'], conf['step']
    dbc = conn.cursor()

    dbc.execute("SELECT count(*) FROM data WHERE domain='%s' AND model='%s' AND step=%d AND relevant IS NULL" % (domain, model, step))
    num_unj = dbc.fetchone()[0]
    print "Number of unjudged terms before update_data_table:", num_unj

    for term in pos_terms:
        dbc.execute("UPDATE data SET relevant=1 WHERE domain=? AND model=? AND term=? AND step=?", (domain, model, term, step))
    conn.commit()

    # get terms which are obviously not relevant (which were not in the pos_terms)
    dbc.execute("SELECT term FROM data WHERE domain='%s' AND model='%s' AND step=%d AND relevant IS NULL" % (domain, model, step))
    res = dbc.fetchall()

    neg_terms = [t[0] for t in res] 
    # update in DB
    for term in neg_terms:
        dbc.execute("UPDATE data SET relevant=0 WHERE domain=? AND model=? AND term=? AND step=?", (domain, model, term, step))
    conn.commit()

    #get missing terms 
    dbc.execute("SELECT count(*) FROM data WHERE domain='%s' AND model='%s' AND relevant IS NULL" % (domain, model))
    num_missing = dbc.fetchone()[0]
    print "Number of unjudged terms after update_data_table:", num_missing

    return pos_terms, neg_terms, num_missing

def save_checked_terms(conf, pos_terms, neg_terms):
    conn, domain, model, step = conf['db'], conf['domain'], conf['model'], conf['step']
    dbc = conn.cursor()

    for term in pos_terms:
        if not term_in_checked_terms(term):
            dbc.execute("INSERT INTO checked_terms (domain, term, relevant) VALUES (?, ?, 1)",  (domain, term))
    conn.commit()

    for term in neg_terms:
        if not term_in_checked_terms(term):
            dbc.execute("INSERT INTO checked_terms (domain, term, relevant) VALUES (?, ?, 0)",  (domain, term))
    conn.commit()

def term_in_checked_terms(term):
    conn, domain = conf['db'], conf['domain']
    dbc = conn.cursor()

    dbc.execute("SELECT count(*) FROM checked_terms WHERE domain=? AND term=?", (domain, term))
    n = dbc.fetchone()[0]
    
    if n>0: return True
    else:   return False

def generate_taxonomy(conf): 
    """
        try to generate a taxonomy using simple word2vec operations
    """
    conn, domain, model = conf['db'], conf['domain'], conf['model']
    dbc = conn.cursor()
    
    # get all terms 
    dbc.execute("SELECT term FROM data WHERE domain='%s' AND model='%s' AND relevant=1" % (domain, model))
    res = dbc.fetchall()
    terms = [r[0] for r in res]

    model = fs_helpers.load_model(conf)

    result_pairs = []

    input_hyperynm_pairs = [('tree', 'forest'), ('carbon_emissions', 'emissions'), ('methane', 'greenhouse_gas')]

    for term in terms:
        print "Getting Hypernyms for", term

        for input_pair in input_hyperynm_pairs:

            try:
                hypo = model.most_similar(positive=[input_pair[0], term], negative=[input_pair[1]], topn=conf['num_taxomy_best'])
            except KeyError:
                continue
                # go to next term
                
            #print "HYPER", hyper 
            for (hy, sim) in hypo:
                if hy in terms:
                    print "found connection", term, "hyopym of", hy, "sim", sim
                    result_pairs.append( (hy, term, sim ) )
     
    # write to file
    fn = "../data/hypernyms." + conf['model'] 
    fh = open(fn, 'wb')

    final_pairs = []
    # filter result pairs
    for pair in result_pairs:
        if pair[2] > conf['sim_threshold']:
            # check if pair already in final_pairs
            found = False 
            for p in final_pairs:
                if p[0] == pair[0] and p[1] == pair[1]:
                    found = True
            if not found: 
                final_pairs.append(pair) 
            else:
                print "found already, skipping", pair


    for pair in final_pairs:
        fh.write(pair[0] + "  isA  " + pair[1] + "   " + str(pair[2]) + "\n")


    fh.close()


if __name__== "__main__":

    # some testing
    inserted_terms = [('climate',0.8) , ('asfsafsadf',0.9), ('climate_scientist',0.7)]
    get_db()
    #set_judgements_from_existing(inserted_terms, conf)    

    generate_taxonomy(conf) 

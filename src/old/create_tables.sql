
/* those two tables are used 
    -- create a sqlite3 DB for them ..
*/

CREATE TABLE data (
    id INTEGER PRIMARY KEY,
    domain VARCHAR,
    corpus VARCHAR,
    term VARCHAR,
    step INT,
    relevant BOOLEAN
);


CREATE TABLE checked_terms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain VARCHAR,
    term VARCHAR,
    relevant BOOLEAN
);


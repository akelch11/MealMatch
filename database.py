
def new_connection():
    from psycopg2 import connect
    conn = connect(database="d4p66i6pnk5690",
                user="uvqmavpcfqtovz",
                password="e7843c562a8599da9fecff85cd975b8219280577dd6bf1a0a235fe35245973d2",
                host="ec2-44-194-167-63.compute-1.amazonaws.com",
                port="5432")
    cur = conn.cursor()
    return cur, conn

def close_connection(cur, conn):
    conn.commit()
    cur.close()
    conn.close()

def create_user_table():
    create_table_query = '''CREATE TABLE users
            (NETID TEXT PRIMARY KEY NOT NULL,
            NAME TEXT NOT NULL,
            YEAR INT NOT NULL,
            MAJOR TEXT NOT NULL,
            PHONENUM TEXT NOT NULL,
            BIO TEXT);'''
    
    cur, conn = new_connection()
    cur.execute(create_table_query)
    close_connection(cur, conn)

def create_matches_table():
    create_table_query = '''CREATE TABLE matches
            (MATCH_ID TEXT PRIMARY KEY NOT NULL,
            FIRST_NETID TEXT NOT NULL,
            SECOND_NETID TEXT NOT NULL,
            MATCH_TIME TIMESTAMP NOT NULL,
            DINING_HALL TEXT NOT NULL,
            START_WINDOW TIMESTAMP NOT NULL,
            END_WINDOW TIMESTAMP NOT NULL,
            ACTIVE BOOLEAN NOT NULL);'''
    
    cur, conn = new_connection()
    cur.execute(create_table_query)
    close_connection(cur, conn)

def create_requests_table():
    from big_lists import dhall_list as dl
    dhall_list = [a.upper() for a in dl]
    create_table_query = '''CREATE TABLE requests
            (REQUESTID TEXT PRIMARY KEY NOT NULL,
            NETID TEXT NOT NULL,
            BEGINTIME TIMESTAMP NOT NULL,
            ENDTIME TIMESTAMP NOT NULL,
            LUNCH BOOLEAN NOT NULL,
            MATCHID TEXT,\n'''

    for i in range(len(dhall_list)):
        create_table_query = create_table_query + "{} BOOLEAN NOT NULL,\n".format(dhall_list[i])

    create_table_query = create_table_query + "ATDHALL BOOLEAN, \n ACTIVE BOOLEAN NOT NULL);"

    cur, conn = new_connection()
    cur.execute(create_table_query)
    close_connection(cur, conn)
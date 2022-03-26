import psycopg2
dhall_list = ["WUCOX", "ROMA", "FORBES", "CJL", "WHITMAN"]

def add_request(mealtime, dhall, endtime):
    create_requests_table()

def create_requests_table():
    conn = psycopg2.connect(database="d4p66i6pnk5690", user = "uvqmavpcfqtovz", password = "e7843c562a8599da9fecff85cd975b8219280577dd6bf1a0a235fe35245973d2", host = "ec2-44-194-167-63.compute-1.amazonaws.com", port = "5432")

    cur = conn.cursor()

    create_table_query = '''CREATE TABLE requests
            (NETID TEXT PRIMARY KEY NOT NULL,
            BEGIN TIMESTAMP NOT NULL,
            END TIMESTAMP NOT NULL,
            MATCHID TEXT,\n'''

    for i in range(len(dhall_list)):
        create_table_query = create_table_query + "{} BOOLEAN NOT NULL,\n".format(dhall_list[i])

    create_table_query = create_table_query + "ATDHALL BOOLEAN);"

    print(create_table_query)
    cur.execute(create_table_query)
    conn.commit()
    conn.close()
    
    
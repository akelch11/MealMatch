import psycopg2
dhall_list = ["WUCOX", "ROMA", "FORBES", "CJL", "WHITMAN"]

def create_profile(mealtime, dhall, endtime):
    conn = psycopg2.connect(database="d4p66i6pnk5690", user = "uvqmavpcfqtovz", password = "e7843c562a8599da9fecff85cd975b8219280577dd6bf1a0a235fe35245973d2", host = "ec2-44-194-167-63.compute-1.amazonaws.com", port = "5432")
    cur = conn.cursor()
    

    sql = "INSERT INTO users (NETID,BEGINTIME,ENDTIME,MATCHID,"
    
    for i in range(len(dhall_list)):
        sql = sql + "{},".format(dhall_list[i])


    "ATDHALL) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (netid, name, year, major, phonenum, bio)
    cur.execute(sql, val)

    conn.commit()
    conn.close()
    print("Profile created for: " + netid)

    return netid
def create_requests_table():
    conn = psycopg2.connect(database="d4p66i6pnk5690", user = "uvqmavpcfqtovz", password = "e7843c562a8599da9fecff85cd975b8219280577dd6bf1a0a235fe35245973d2", host = "ec2-44-194-167-63.compute-1.amazonaws.com", port = "5432")

    cur = conn.cursor()

    create_table_query = '''CREATE TABLE requests
            (NETID TEXT PRIMARY KEY NOT NULL,
            BEGINTIME TIMESTAMP NOT NULL,
            ENDTIME TIMESTAMP NOT NULL,
            MATCHID TEXT,\n'''

    for i in range(len(dhall_list)):
        create_table_query = create_table_query + "{} BOOLEAN NOT NULL,\n".format(dhall_list[i])

    create_table_query = create_table_query + "ATDHALL BOOLEAN);"

    print(create_table_query)
    cur.execute(create_table_query)
    conn.commit()
    conn.close()
    
    
def match_requests():
    print("Match Requests")
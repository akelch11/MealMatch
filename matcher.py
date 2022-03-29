from tracemalloc import start
from venv import create
import psycopg2
import random
import string
dhall_list = ["WUCOX", "ROMA", "FORBES", "CJL", "WHITMAN"]

def add_request(netid, meal_type, start_time, end_time, dhall_arr):
    conn = psycopg2.connect(database="d4p66i6pnk5690", user = "uvqmavpcfqtovz", password = "e7843c562a8599da9fecff85cd975b8219280577dd6bf1a0a235fe35245973d2", host = "ec2-44-194-167-63.compute-1.amazonaws.com", port = "5432")
    cur = conn.cursor()

    sql = "INSERT INTO requests (REQUESTID, NETID,BEGINTIME,ENDTIME, LUNCH, MATCHID,"
    
    for i in range(len(dhall_list)):
        sql = sql + "{},".format(dhall_list[i])

    sql = sql + "ATDHALL) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s, %s)"
    print(sql)
    requestId = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))


    val = [requestId, netid, start_time, end_time, meal_type, ""]
    for i in range(len(dhall_arr)):
        val.append(dhall_arr[i])

    val.append(True)
    cur.execute(sql, tuple(val))

    conn.commit()
    conn.close()
    print("Profile created for: " + netid)

def create_requests_table():
    conn = psycopg2.connect(database="d4p66i6pnk5690", user = "uvqmavpcfqtovz", password = "e7843c562a8599da9fecff85cd975b8219280577dd6bf1a0a235fe35245973d2", host = "ec2-44-194-167-63.compute-1.amazonaws.com", port = "5432")

    cur = conn.cursor()

    create_table_query = '''CREATE TABLE requests
            (REQUESTID TEXT PRIMARY KEY NOT NULL,
            NETID TEXT NOT NULL,
            BEGINTIME TIMESTAMP NOT NULL,
            ENDTIME TIMESTAMP NOT NULL,
            LUNCH BOOLEAN NOT NULL,
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
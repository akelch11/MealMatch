from tracemalloc import start
from venv import create
import psycopg2
import random
import string
from datetime import datetime
dhall_list = ["WUCOX", "ROMA", "FORBES", "CJL", "WHITMAN"]

def add_request(netid, meal_type, start_time, end_time, dhall_arr):
    conn = psycopg2.connect(database="d4p66i6pnk5690", user = "uvqmavpcfqtovz", password = "e7843c562a8599da9fecff85cd975b8219280577dd6bf1a0a235fe35245973d2", host = "ec2-44-194-167-63.compute-1.amazonaws.com", port = "5432")
    cur = conn.cursor()

    sql = "INSERT INTO requests (REQUESTID, NETID,BEGINTIME,ENDTIME, LUNCH,"
    
    for i in range(len(dhall_list)):
        sql = sql + "{},".format(dhall_list[i])

    sql = sql + "ATDHALL) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s,%s, %s)"
    requestId = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(16))


    val = [requestId, netid, start_time, end_time, meal_type]
    for i in range(len(dhall_arr)):
        val.append(dhall_arr[i])

    val.append(True)
    cur.execute(sql, tuple(val))

    conn.commit()
    conn.close()

    match_requests()

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

    cur.execute(create_table_query)
    conn.commit()
    conn.close()

def create_matches_table():
    conn = psycopg2.connect(database="d4p66i6pnk5690", user = "uvqmavpcfqtovz", password = "e7843c562a8599da9fecff85cd975b8219280577dd6bf1a0a235fe35245973d2", host = "ec2-44-194-167-63.compute-1.amazonaws.com", port = "5432")

    cur = conn.cursor()

    create_table_query = '''CREATE TABLE matches
            (MATCH_ID TEXT PRIMARY KEY NOT NULL,
            FIRST_NETID TEXT NOT NULL,
            SECOND_NETID TEXT NOT NULL,
            MATCH_TIME TIMESTAMP NOT NULL,
            DINING_HALL TEXT NOT NULL);'''
    
    cur.execute(create_table_query)
    conn.commit()
    conn.close()
    
    
def match_requests():
    
    for dhall in dhall_list:

        # Create queries for both lunch and dinner request matching
        parse_requests_lunch = '''SELECT REQUESTID, NETID, BEGINTIME, ENDTIME
                            FROM requests\n'''
        parse_requests_lunch += "WHERE {} = TRUE AND LUNCH = TRUE AND MATCHID IS NULL\n".format(dhall)
        parse_requests_lunch += "ORDER BY BEGINTIME ASC"

        parse_requests_din = '''SELECT REQUESTID, NETID, BEGINTIME, ENDTIME
                            FROM requests\n'''
        parse_requests_din += "WHERE {} = TRUE AND LUNCH = FALSE AND MATCHID IS NULL\n".format(dhall)
        parse_requests_din += "ORDER BY BEGINTIME ASC"

        execute_match_query(parse_requests_lunch, dhall)
        execute_match_query(parse_requests_din, dhall)


def execute_match_query(parse_requests, dhall):
    # Number of characters in id
    N = 16
    conn = psycopg2.connect(database="d4p66i6pnk5690", user = "uvqmavpcfqtovz", password = "e7843c562a8599da9fecff85cd975b8219280577dd6bf1a0a235fe35245973d2", host = "ec2-44-194-167-63.compute-1.amazonaws.com", port = "5432")

    cur = conn.cursor()
    cur.execute(parse_requests)
    rows = []
    row = cur.fetchone()
    # Add all current requests to rows for further processing
    while(row):
        rows.append(row)
        row = cur.fetchone()

    # Remove last element from requests if there are an odd number
    # of requests
    if len(rows)%2 == 1:
        rows.pop()    
    # Use requests in rows to create matches in pairs of two
    while(rows):
        # get data for first and second student to be matched
        first = rows.pop(0)
        second = rows.pop(0)

        # Obtain matchid
        match_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k = N))
        first_netid = first[1]
        second_netid = second[1]

        # Current time for match made
        now = datetime.now()

        sql = "INSERT INTO matches (MATCH_ID, FIRST_NETID, SECOND_NETID, MATCH_TIME, DINING_HALL) "
        sql += "VALUES (%s, %s, %s, %s, %s)"

        val = (match_id, first_netid, second_netid, now, dhall)

        cur.execute(sql, val)

        # Remove requests after match is made
        modify_request(first[0], match_id)
        modify_request(second[0], match_id)
    
    conn.commit()
    conn.close()

    pass

# Remove request from request table 
def modify_request(request_id, match_id):
    conn = psycopg2.connect(database="d4p66i6pnk5690", user = "uvqmavpcfqtovz", password = "e7843c562a8599da9fecff85cd975b8219280577dd6bf1a0a235fe35245973d2", host = "ec2-44-194-167-63.compute-1.amazonaws.com", port = "5432")

    cur = conn.cursor()

    sql = "UPDATE requests SET MATCHID = %s WHERE REQUESTID = %s"
    val = (match_id, request_id)

    cur.execute(sql, val)

    conn.commit()
    conn.close()    
    print("Removed request")

def get_all_matches(netid):
    all_matches = []

    conn = psycopg2.connect(database="d4p66i6pnk5690", user = "uvqmavpcfqtovz", password = "e7843c562a8599da9fecff85cd975b8219280577dd6bf1a0a235fe35245973d2", host = "ec2-44-194-167-63.compute-1.amazonaws.com", port = "5432")
    cur = conn.cursor()
    query="""SELECT * 
            FROM matches as m, users as u
            WHERE (m.first_netid = u.netid
            OR m.second_netid = u.netid)
            AND (m.first_netid = %s OR m.second_netid = %s)
            ORDER BY match_time ASC"""

    cur.execute(query, (netid, netid))
    rows=cur.fetchall()
    
    for row in rows:
        row_arr = []
        for col in row:
            row_arr.append(col)
        all_matches.append(row_arr)



    cur.close()
    return all_matches
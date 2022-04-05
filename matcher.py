from tracemalloc import start
from urllib import request
from venv import create
import psycopg2
import random
import string
from datetime import datetime
dhall_list = ["WUCOX", "ROMA", "FORBES", "CJL", "WHITMAN"]

def add_request(netid, meal_type, start_time, end_time, dhall_arr, atdhall):
    conn = psycopg2.connect(database="d4p66i6pnk5690", user = "uvqmavpcfqtovz", password = "e7843c562a8599da9fecff85cd975b8219280577dd6bf1a0a235fe35245973d2", host = "ec2-44-194-167-63.compute-1.amazonaws.com", port = "5432")
    cur = conn.cursor()

    sql = "INSERT INTO requests (REQUESTID, NETID,BEGINTIME,ENDTIME, LUNCH,"
    
    for i in range(len(dhall_list)):
        sql = sql + "{},".format(dhall_list[i])

    sql = sql + "ATDHALL, ACTIVE) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s,%s, %s, %s)"
    requestId = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(16))


    val = [requestId, netid, start_time, end_time, meal_type]
    for i in range(len(dhall_arr)):
        val.append(dhall_arr[i])

    val.append(atdhall)
    val.append(True)
    cur.execute(sql, tuple(val))
    conn.commit()
    conn.close()

    match_requests()


def remove_request(requestid):
    sql = """ UPDATE requests
                SET active = %s
                WHERE requestid = %s"""
    conn = psycopg2.connect(database="d4p66i6pnk5690", user = "uvqmavpcfqtovz", password = "e7843c562a8599da9fecff85cd975b8219280577dd6bf1a0a235fe35245973d2", host = "ec2-44-194-167-63.compute-1.amazonaws.com", port = "5432")
    cur = conn.cursor()
    cur.execute(sql, (False, requestid))

    conn.commit()
    conn.close()



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

    create_table_query = create_table_query + "ATDHALL BOOLEAN, \n ACTIVE BOOLEAN NOT NULL);"

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
            DINING_HALL TEXT NOT NULL
            START_WINDOW TIMESTAMP NOT NULL
            END_WINDOW TIMESTAMP NOT NULL);'''
    
    cur.execute(create_table_query)
    conn.commit()
    conn.close()
    
    
def match_requests():
    
    for dhall in dhall_list:

        # Create queries for both lunch and dinner request matching
        parse_requests_lunch = '''SELECT REQUESTID, NETID, BEGINTIME, ENDTIME
                            FROM requests\n'''
        parse_requests_lunch += "WHERE {} = TRUE AND LUNCH = TRUE AND MATCHID IS NULL AND ACTIVE = TRUE\n".format(dhall)
        parse_requests_lunch += "ORDER BY BEGINTIME ASC"

        parse_requests_din = '''SELECT REQUESTID, NETID, BEGINTIME, ENDTIME
                            FROM requests\n'''
        parse_requests_din += "WHERE {} = TRUE AND LUNCH = FALSE AND MATCHID IS NULL AND ACTIVE + TRUE\n".format(dhall)
        parse_requests_din += "ORDER BY BEGINTIME ASC"

        execute_match_query(parse_requests_lunch, dhall)
        execute_match_query(parse_requests_din, dhall)


def execute_match_query(parse_requests, dhall):
    # Number of characters in id
    N = 16
    conn = psycopg2.connect(database="d4p66i6pnk5690", user = "uvqmavpcfqtovz", password = "e7843c562a8599da9fecff85cd975b8219280577dd6bf1a0a235fe35245973d2", host = "ec2-44-194-167-63.compute-1.amazonaws.com", port = "5432")

    cur = conn.cursor()
    cur.execute(parse_requests)
    rows = cur.fetchall()
    
    matched = []
    # iterate through requests, comparing pairs to examine match 
    for i in range(len(rows)):
        for j in range(i+1,len(rows)):

            # Do not attempt to find match if row is already matched
            if i in matched or j in matched:
                continue

            first = rows[i] # First request
            second = rows[j] # Second request

            overlap = find_overlap(first[2], first[3], second[2], second[3])
            
            # if there is no valid overlap between current requests 
            # then skip current pairing
            if not overlap:
                continue
            
            # Establish start and end windows for match
            start_int = overlap[0]
            end_int = overlap[1]


            # Obtain matchid
            match_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k = N))
            first_netid = first[1]
            second_netid = second[1]


            # Current time for match made
            now = datetime.now()

            sql = "INSERT INTO matches (MATCH_ID, FIRST_NETID, SECOND_NETID, MATCH_TIME, DINING_HALL, START_WINDOW, END_WINDOW) "
            sql += "VALUES (%s, %s, %s, %s, %s, %s, %s)"

            val = (match_id, first_netid, second_netid, now, dhall, start_int, end_int)

            cur.execute(sql, val)

            # Modify requests after match is made
            modify_request(first[0], match_id)
            modify_request(second[0], match_id)

            # cache the row numbers being matched
            matched.append(i)
            matched.append(j)

    conn.commit()
    conn.close()

# Remove request from request table 
def modify_request(request_id, match_id):
    conn = psycopg2.connect(database="d4p66i6pnk5690", user = "uvqmavpcfqtovz", password = "e7843c562a8599da9fecff85cd975b8219280577dd6bf1a0a235fe35245973d2", host = "ec2-44-194-167-63.compute-1.amazonaws.com", port = "5432")

    cur = conn.cursor()

    sql = "UPDATE requests SET MATCHID = %s WHERE REQUESTID = %s"
    val = (match_id, request_id)

    cur.execute(sql, val)

    conn.commit()
    conn.close()    
    print("Modified request")

def get_all_matches(netid):
    all_matches = []

    conn = psycopg2.connect(database="d4p66i6pnk5690", user = "uvqmavpcfqtovz", password = "e7843c562a8599da9fecff85cd975b8219280577dd6bf1a0a235fe35245973d2", host = "ec2-44-194-167-63.compute-1.amazonaws.com", port = "5432")
    cur = conn.cursor()
    query="""SELECT * 
            FROM matches as m, users as u
            WHERE (m.first_netid = u.netid
            OR m.second_netid = u.netid)
            AND (m.first_netid = %s OR m.second_netid = %s)
            AND (u.netid != %s)
            ORDER BY match_time ASC"""

    cur.execute(query, (netid, netid, netid))
    rows=cur.fetchall()
    
    for row in rows:
        row_arr = []
        for col in row:
            row_arr.append(col)
        all_matches.append(row_arr)



    cur.close()
    return all_matches

def get_all_requests(netid):
    all_requests = []

    conn = psycopg2.connect(database="d4p66i6pnk5690", user = "uvqmavpcfqtovz", password = "e7843c562a8599da9fecff85cd975b8219280577dd6bf1a0a235fe35245973d2", host = "ec2-44-194-167-63.compute-1.amazonaws.com", port = "5432")
    cur = conn.cursor()
    query="""SELECT begintime, endtime, lunch, wucox, roma, forbes, cjl, whitman, atdhall, requestid FROM requests as r
            WHERE r.netid = %s"""

    cur.execute(query, [netid])
    rows=cur.fetchall()
    
    for row in rows:
        row_arr = []
        for col in row:
            row_arr.append(col)
        all_requests.append(row_arr)



    cur.close()
    return all_requests

# Find overlap between two datetime intervals, used in finding matches
# between two requests
# inter_1 and inter_2 are tuples of datetime object
def find_overlap(start_A, end_A, start_B, end_B):
    start_int = max(start_A, start_B)
    end_int = min(end_A, end_B)

    # There is no overlap in input intervals
    if start_int >= end_int:
        return False
    
    # Check if overlap is smaller than 30 minutes, not suitable for 
    # adequate meal time
    if (end_int - start_int).total_seconds() / 60.0 < 30:
        return False
    
    # return the start and end of the overlap
    return (start_int, end_int)
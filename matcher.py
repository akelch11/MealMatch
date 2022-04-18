from tracemalloc import start
from urllib import request
from venv import create
import psycopg2
import random
import string
import notifications
from datetime import datetime
from big_lists import dhall_list

dhall_list = [a.upper() for a in dhall_list]

def add_request(netid, meal_type, start_time, end_time, dhall_arr, atdhall):
    conn = psycopg2.connect(database="d4p66i6pnk5690", user = "uvqmavpcfqtovz", password = "e7843c562a8599da9fecff85cd975b8219280577dd6bf1a0a235fe35245973d2", host = "ec2-44-194-167-63.compute-1.amazonaws.com", port = "5432")
    cur = conn.cursor()

    flag = validate_reqeust(netid, meal_type, start_time, end_time, dhall_arr, atdhall)
    if not flag:
        print("Cannot add request: there is already a request in the current meal period")
        return False

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

    clean_requests()

    match_requests()

    return True

def validate_reqeust(netid, meal_type, start_time, end_time, dhall_arr, atdhall):
    conn = psycopg2.connect(database="d4p66i6pnk5690", user = "uvqmavpcfqtovz", password = "e7843c562a8599da9fecff85cd975b8219280577dd6bf1a0a235fe35245973d2", host = "ec2-44-194-167-63.compute-1.amazonaws.com", port = "5432")
    cur = conn.cursor()
    flag = True
    # search for active requests made by user with netid
    sql = """SELECT *
            FROM requests
            WHERE netid = %s AND active = TRUE AND LUNCH  = %s"""
    cur.execute(sql, (netid, meal_type))

    rows = cur.fetchall()

    if(len(rows) > 0):
        flag = False
    
    conn.commit()
    conn.close()

    return flag

def clean_requests():
    conn = psycopg2.connect(database="d4p66i6pnk5690", user = "uvqmavpcfqtovz", password = "e7843c562a8599da9fecff85cd975b8219280577dd6bf1a0a235fe35245973d2", host = "ec2-44-194-167-63.compute-1.amazonaws.com", port = "5432")
    cur = conn.cursor()
    sql = """SELECT *
            FROM requests"""

    cur.execute(sql)

    rows = cur.fetchall()

    now = datetime.now()

    old_requests = []

    for row in rows:
        # Check if endtime of request has passed
        end_time = row[3]
        #
        if end_time < now:
            old_requests.append(row[0])
    
    sql = """ UPDATE requests
                SET active = %s
                WHERE requestid = %s"""
    conn = psycopg2.connect(database="d4p66i6pnk5690", user = "uvqmavpcfqtovz", password = "e7843c562a8599da9fecff85cd975b8219280577dd6bf1a0a235fe35245973d2", host = "ec2-44-194-167-63.compute-1.amazonaws.com", port = "5432")
    cur = conn.cursor()
    for id in old_requests:
        cur.execute(sql, (False, id))
        
    cur.close()
    conn.commit()
    conn.close()

def remove_request(requestid):
    sql = """ UPDATE requests
                SET active = %s
                WHERE requestid = %s"""
    conn = psycopg2.connect(database="d4p66i6pnk5690", user = "uvqmavpcfqtovz", password = "e7843c562a8599da9fecff85cd975b8219280577dd6bf1a0a235fe35245973d2", host = "ec2-44-194-167-63.compute-1.amazonaws.com", port = "5432")
    cur = conn.cursor()
    cur.execute(sql, (False, requestid))

    conn.commit()
    conn.close()

def remove_match(netid, matchid, phonenum):
    sql = """ UPDATE matches
                SET active = %s
                WHERE match_id = %s"""
    conn = psycopg2.connect(database="d4p66i6pnk5690", user = "uvqmavpcfqtovz", password = "e7843c562a8599da9fecff85cd975b8219280577dd6bf1a0a235fe35245973d2", host = "ec2-44-194-167-63.compute-1.amazonaws.com", port = "5432")
    cur = conn.cursor()
    cur.execute(sql, (False, matchid))
    conn.commit()
    conn.close()

    message = "{} cancelled your match. Check the MealMatch app for more information".format(get_name_from_netid(netid))

    notifications.send_message(message, phonenum)



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
            DINING_HALL TEXT NOT NULL,
            FIRST_ACCEPTED BOOLEAN NOT NULL,
            SECOND_ACCEPTED BOOLEAN NOT NULL,
            START_WINDOW TIMESTAMP NOT NULL,
            END_WINDOW TIMESTAMP NOT NULL,
            ACTIVE BOOLEAN NOT NULL);'''
    
    cur.execute(create_table_query)
    conn.commit()
    conn.close()
    
    
def match_requests():
    
    for dhall in dhall_list:

        # Create queries for both lunch and dinner request matching
        parse_requests_lunch = """SELECT REQUESTID, r.NETID, BEGINTIME, ENDTIME, u.NAME, PHONENUM FROM requests as r, users as u 
                                    WHERE {} = TRUE 
                                    AND r.LUNCH = TRUE 
                                    AND r.MATCHID IS NULL 
                                    AND r.ACTIVE = TRUE
                                    AND r.netid = u.netid
                                    ORDER BY BEGINTIME ASC
                                    """.format(dhall)

        parse_requests_din = """SELECT REQUESTID, r.NETID, BEGINTIME, ENDTIME, u.NAME, PHONENUM FROM requests as r, users as u 
                                    WHERE {} = TRUE 
                                    AND r.LUNCH = FALSE 
                                    AND r.MATCHID IS NULL 
                                    AND r.ACTIVE = TRUE
                                    AND r.netid = u.netid
                                    ORDER BY BEGINTIME ASC
                                    """.format(dhall)

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

            print("Test!")
            print(first[1])
            print(second[1])

            overlap = find_overlap(first[2], first[3], second[2], second[3])
            
            # if there is no valid overlap between current requests 
            # then skip current pairing
            if not overlap:
                print("Continue")
                continue

            if first[1] == second[1]:
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

            sql = "INSERT INTO matches (MATCH_ID, FIRST_NETID, SECOND_NETID, MATCH_TIME, DINING_HALL, START_WINDOW, END_WINDOW, FIRST_ACCEPTED, SECOND_ACCEPTED, ACTIVE) "
            sql += "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

            val = (match_id, first_netid, second_netid, now, dhall, start_int, end_int, False, False, True)

            cur.execute(sql, val)

            # Modify requests after match is made
            modify_request(first[0], match_id)
            modify_request(second[0], match_id)

            message = "You matched with {} on MealMatch! Check the app for more information on your match."

            notifications.send_message(message.format(first[4]), second[5])
            notifications.send_message(message.format(second[4]), first[5])

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

    remove_request(request_id)
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
            AND (m.active = TRUE)
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

def get_name_from_netid(netid):
    conn = psycopg2.connect(database="d4p66i6pnk5690", user = "uvqmavpcfqtovz", password = "e7843c562a8599da9fecff85cd975b8219280577dd6bf1a0a235fe35245973d2", host = "ec2-44-194-167-63.compute-1.amazonaws.com", port = "5432")
    cur = conn.cursor()
    query="""SELECT name FROM users WHERE netid = %s"""
    cur.execute(query, [netid])
    row = cur.fetchone()
    conn.close()

    return row[0]


def accept_match(netid, matchid, phonenum):

    print("AACEPT MATCH")
    print(netid)
    conn = psycopg2.connect(database="d4p66i6pnk5690", user = "uvqmavpcfqtovz", password = "e7843c562a8599da9fecff85cd975b8219280577dd6bf1a0a235fe35245973d2", host = "ec2-44-194-167-63.compute-1.amazonaws.com", port = "5432")
    cur = conn.cursor()
    query="""SELECT match_id, first_netid, second_netid, first_accepted, second_accepted FROM matches
            WHERE match_id = %s"""

    cur.execute(query, [matchid])
    row=cur.fetchone()

    netid_type = ""

    if row[1] == netid:
        #We know that the user is the first_netid
        netid_type = 'FIRST_ACCEPTED'
        if not row[4]:
            #If the other person has accepted, notify the other person that theres a match
            message = "{} accepted the match! Confirm that you'll be there on the MealMatch App!".format(get_name_from_netid(netid))
            notifications.send_message(message, phonenum)
        else:
            #If the other person has not accepted, notify the other person that match is confirmed
            message = "{} also accepted the match! Have fun eating!".format(get_name_from_netid(netid))
            notifications.send_message(message, phonenum)

            
    elif row[2] == netid:
        # We know that the user if the second_netid
        netid_type = 'SECOND_ACCEPTED'
        if not row[3]:
            #If the other person has accepted, notify the other person that theres a match
            message = "{} accepted the match! Confirm that you'll be there on the MealMatch App!".format(netid)
            notifications.send_message(message, phonenum)
        else:
            #If the other person has not accepted, notify the other person that match is confirmed
            message = "{} also accepted the match! Have fun eating!".format(netid)
            notifications.send_message(message, phonenum)

    query="""UPDATE matches SET {} = TRUE WHERE MATCH_ID = %s""".format(netid_type)


    cur.execute(query, [matchid])
    conn.commit()
    conn.close()



def get_all_requests(netid):
    all_requests = []

    conn = psycopg2.connect(database="d4p66i6pnk5690", user = "uvqmavpcfqtovz", password = "e7843c562a8599da9fecff85cd975b8219280577dd6bf1a0a235fe35245973d2", host = "ec2-44-194-167-63.compute-1.amazonaws.com", port = "5432")
    cur = conn.cursor()
    query="""SELECT begintime, endtime, lunch, cjl, forbes, roma, whitman, wucox, atdhall, requestid FROM requests as r
            WHERE r.netid = %s
            AND r.active = TRUE"""

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
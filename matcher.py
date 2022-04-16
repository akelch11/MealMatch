from sys import stderr
import random
import string
import notifications
from datetime import datetime
from big_lists import dhall_list
from database import new_connection, close_connection


def add_request(netid, meal_type, start_time, end_time, dhall_arr, atdhall):
    if not validate_request(netid, meal_type):
        print("Cannot add request: there is already a request in the current meal period", file=stderr)
        return False

    sql = "INSERT INTO requests (REQUESTID, NETID,BEGINTIME,ENDTIME, LUNCH,"
    for i in dhall_list:
        sql = sql + "{},".format(i)
    # add %s for each dining hall
    dhall_strargs = "%s, "*len(dhall_list)
    sql = sql + "ATDHALL, ACTIVE) VALUES (%s, %s, %s, %s, %s, " + dhall_strargs + "%s, %s)"

    all_chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
    requestId = ''.join(random.choice(all_chars) for _ in range(16))

    val = [requestId, netid, start_time, end_time, meal_type]
    val += dhall_arr
    val += [atdhall, True]
    
    cur, conn = new_connection()
    cur.execute(sql, tuple(val))
    close_connection(cur, conn)

    clean_requests()
    match_requests()

    return True

def validate_request(netid, meal_type):
    # search for active requests made by user with netid
    sql = """SELECT *
            FROM requests
            WHERE netid = %s AND active = TRUE AND LUNCH  = %s"""
    
    cur, conn = new_connection()
    cur.execute(sql, (netid, meal_type))
    rows = cur.fetchall()
    close_connection(cur, conn)    

    # Return True if there are no conflicting requests, i.e. the list is empty
    return len(rows) == 0

def clean_requests():
    sql = """SELECT endtime
            FROM requests
            WHERE active = TRUE"""

    cur, conn = new_connection()
    cur.execute(sql)

    now = datetime.now()
    # Check if endtime of request has passed
    old_requests = [row[0] for row in cur.fetchall() if row[0]<now]
    
    sql = """ UPDATE requests
                SET active = FALSE
                WHERE requestid = %s"""
    
    for id in old_requests:
        cur.execute(sql, [id])
        
    close_connection(cur, conn)



def remove_request(requestid):
    sql = """ UPDATE requests
                SET active = FALSE
                WHERE requestid = %s"""
    
    cur, conn = new_connection()
    cur.execute(sql, [requestid])
    close_connection(cur, conn)

def remove_match(matchid):
    sql = """ UPDATE matches
                SET active = FALSE
                WHERE match_id = %s"""
    
    cur, conn = new_connection()
    cur.execute(sql, [matchid])
    close_connection(cur, conn)
    
    
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
    N = 16 # length of match id
    cur, conn = new_connection()
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

            sql = "INSERT INTO matches (MATCH_ID, FIRST_NETID, SECOND_NETID, MATCH_TIME, DINING_HALL, START_WINDOW, END_WINDOW, ACTIVE) "
            sql += "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

            val = (match_id, first_netid, second_netid, now, dhall, start_int, end_int, True)

            cur.execute(sql, val)

            # Modify requests after match is made
            modify_request(first[0], match_id)
            modify_request(second[0], match_id)

            notifications.send_message(first[4], second[5])
            notifications.send_message(second[4], first[5])

            # cache the row numbers being matched
            matched.append(i)
            matched.append(j)

    close_connection(cur, conn)

# Remove request from request table 
def modify_request(request_id, match_id):
    sql = "UPDATE requests SET MATCHID = %s WHERE REQUESTID = %s"
    val = (match_id, request_id)

    cur, conn = new_connection()
    cur.execute(sql, val)
    close_connection(cur, conn)

    remove_request(request_id)
    print("Modified request")

def get_all_matches(netid):
    all_matches = []

    query="""SELECT * 
            FROM matches as m, users as u
            WHERE (m.first_netid = u.netid
            OR m.second_netid = u.netid)
            AND (m.first_netid = %s OR m.second_netid = %s)
            AND (u.netid != %s)
            AND (m.active = TRUE)
            ORDER BY match_time ASC"""

    cur, conn = new_connection()
    cur.execute(query, (netid, netid, netid))
    rows = cur.fetchall()
    close_connection(cur, conn)

    for row in rows:
        row_arr = []
        for col in row:
            row_arr.append(col)
        all_matches.append(row_arr)

    return all_matches

def get_all_requests(netid):
    all_requests = []

    query="""SELECT begintime, endtime, lunch, {}, atdhall, requestid FROM requests as r
            WHERE r.netid = %s
            AND r.active = TRUE""".format(', '.join(dhall_list))

    cur, conn = new_connection()
    cur.execute(query, [netid])
    rows=cur.fetchall()
    close_connection(cur, conn)
    
    for row in rows:
        row_arr = []
        for col in row:
            row_arr.append(col)
        all_requests.append(row_arr)


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
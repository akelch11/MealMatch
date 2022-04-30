from database import new_connection, close_connection
from big_lists import dhall_list
from datetime import datetime
from sys import stdout
import random
import string


def add_request(netid, meal_type, start_time, end_time, dhall_arr, atdhall):
    cur, conn = new_connection()

    flag = validate_request(netid, meal_type)
    if not flag:
        print("Cannot add request: there is already a request in the current meal period")
        return False

    sql = "INSERT INTO requests (REQUESTID, NETID,BEGINTIME,ENDTIME, LUNCH,"

    for dhall in dhall_list:
        sql = sql + "{},".format(dhall)

    dhall_strargs = "%s, " * len(dhall_list)
    sql = sql + ("ATDHALL, ACTIVE) VALUES (%s, %s, %s, %s, %s, {} %s, %s)".format(dhall_strargs))

    requestId = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))

    val = [requestId, netid, start_time, end_time, meal_type]
    val += dhall_arr
    val += [atdhall, True]

    cur.execute(sql, val)
    close_connection(cur, conn)

    clean_requests()

    from matcher import match_requests
    match_requests()

    return True
    
# Remove request from request table
def modify_request(request_id, match_id):
    sql = "UPDATE requests SET MATCHID = %s WHERE REQUESTID = %s"
    val = (match_id, request_id)

    cur, conn = new_connection()
    cur.execute(sql, val)
    close_connection(cur, conn)

    remove_request(request_id)
    print("Modified request", file=stdout)


def get_all_requests(netid):
    all_requests = []
    dhall_str = ', '.join(dhall_list)
    query = """SELECT begintime, endtime, lunch, {} ,atdhall, requestid FROM requests as r
            WHERE r.netid = %s
            AND r.active = TRUE""".format(dhall_str)

    cur, conn = new_connection()
    cur.execute(query, [netid])
    rows = cur.fetchall()
    close_connection(cur, conn)

    for row in rows:
        row_arr = []
        for col in row:
            row_arr.append(col)
        all_requests.append(row_arr)

    return all_requests
    


def validate_request(netid, meal_type):
    # search for active requests made by user with netid
    sql = """SELECT *
            FROM requests
            WHERE netid = %s AND active = TRUE AND LUNCH  = %s"""

    cur, conn = new_connection()
    cur.execute(sql, (netid, meal_type))
    rows = cur.fetchall()
    close_connection(cur, conn)

    return len(rows) == 0


def clean_requests():
    sql = """SELECT *
            FROM requests"""

    cur, conn = new_connection()
    cur.execute(sql)

    rows = cur.fetchall()

    now = datetime.now()

    # list of requests that have expired
    old_requests = [row[0] for row in rows if row[3] < now]

    sql = """ UPDATE requests
                SET active = %s
                WHERE requestid = %s"""

    for id in old_requests:
        cur.execute(sql, (False, id))

    close_connection(cur, conn)


def remove_request(requestid):
    sql = """ UPDATE requests
                SET active = %s
                WHERE requestid = %s"""

    cur, conn = new_connection()
    cur.execute(sql, (False, requestid))
    close_connection(cur, conn)
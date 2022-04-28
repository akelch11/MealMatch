import random
import string
from sys import stdout, stderr
import notifications
from datetime import datetime
from big_lists import dhall_list
from database import new_connection, close_connection


def add_request(netid, meal_type, start_time, end_time, dhall_arr, atdhall):
    cur, conn = new_connection()

    flag = validate_request(netid, meal_type)
    if not flag:
        print("Cannot add request: there is already a request in the current meal period")
        return False

    sql = "INSERT INTO requests (REQUESTID, NETID,BEGINTIME,ENDTIME, LUNCH,"

    for i in range(len(dhall_list)):
        sql = sql + "{},".format(dhall_list[i])

    dhall_strargs = "%s, " * len(dhall_list)
    sql = sql + ("ATDHALL, ACTIVE) VALUES (%s, %s, %s, %s, %s, {} %s, %s)".format(dhall_strargs))

    requestId = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))

    val = [requestId, netid, start_time, end_time, meal_type]
    val += dhall_arr
    val += [atdhall, True]

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


def remove_match(netid, matchid, phonenum):
    sql = """ UPDATE matches
                SET active = %s
                WHERE match_id = %s"""

    cur, conn = new_connection()
    cur.execute(sql, (False, matchid))
    close_connection(cur, conn)

    message = "{} cancelled your match. Check "\
    "the MealMatch app for more information" \
        .format(get_name_from_netid(netid))
    notifications.send_message(message, phonenum)


def match_requests():
    # Create queries for both lunch and dinner request matching

    dhall_str = ', '.join(["r."+dh.upper() for dh in dhall_list])
    parse_requests = """SELECT REQUESTID, r.NETID, BEGINTIME, ENDTIME, u.NAME, PHONENUM, {}, 
                                u.YEAR, u.MAJOR
                                FROM requests as r, users as u 
                                WHERE r.LUNCH = {} 
                                AND r.MATCHID IS NULL 
                                AND r.ACTIVE = TRUE
                                AND r.netid = u.netid
                                ORDER BY BEGINTIME ASC
                                """

    parse_requests_lunch = parse_requests.format(dhall_str, "TRUE")
    parse_requests_din = parse_requests.format(dhall_str, "FALSE")

    # Run helper method to find and insert matches into matches table
    execute_match_query(parse_requests_lunch, True)
    execute_match_query(parse_requests_din, False)


def execute_match_query(parse_requests, lunch):
    # Number of characters in id
    N = 16
    cur, conn = new_connection()
    cur.execute(parse_requests)
    rows = cur.fetchall()

    matched = []
    # iterate through requests, comparing pairs to examine match 
    for i in range(len(rows)):

        poss_matches = []
        first = rows[i]  # First request

        # Do not attempt to find match if row is already matched
        if i in matched:
            continue

        for j in range(i + 1, len(rows)):
            # Do not attempt to find match if row is already matched
            if j in matched:
                continue

            second = rows[j]  # Second request

            print("Test!")
            print(first[1])
            print(second[1])

            overlap = find_overlap(first[2], first[3], second[2], second[3])

            # if there is no valid overlap between current requests 
            # then skip current pairing
            if not overlap:
                print("Continue")
                continue

            # Do not match two requests originating from same user
            if first[1] == second[1]:
                print("Continue")
                continue

            # Evaluate possible dining halls for each request
            first_poss_dhalls = find_possible_dhalls(first)
            second_poss_dhalls = find_possible_dhalls(second)

            combined_dhalls = list(set(first_poss_dhalls) & set(second_poss_dhalls))

            # No common dining halls between a pair of requests
            if len(combined_dhalls) == 0:
                print("Continue")
                continue

            # Assign score to current possible match and add it
            # to the current possible matches
            # index for major: 12
            # index for class year: 11
            if first[11] == second[11] and first[12] == second[12]:
                poss_matches.append((j, 2, combined_dhalls, overlap))

            elif first[11] == second[11] or first[12] == second[12]:
                poss_matches.append((j, 1, combined_dhalls, overlap))

            else:
                poss_matches.append((j, 0, combined_dhalls, overlap))

        # Continue loop if there are no possible matches
        if len(poss_matches) == 0:
            continue

        # Now execute a match

        # Sort possible matches by match score, i.e., second item in
        # the list of tuples, in descending order
        poss_matches.sort(key=lambda x: x[1], reverse=True)
        chosen_row = poss_matches[0]
        second = rows[chosen_row[0]]  # Grab requests row of chosen request
        dhall = chosen_row[2][0]  # Dhall chosen for match
        overlap = chosen_row[3]

        # Establish start and end windows for match
        start_int = overlap[0]
        end_int = overlap[1]

        # Obtain matchid
        match_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))
        first_netid = first[1]
        second_netid = second[1]

        sql = "INSERT INTO matches (MATCH_ID, FIRST_NETID, SECOND_NETID, MATCH_TIME, DINING_HALL, " \
              "START_WINDOW, END_WINDOW, FIRST_ACCEPTED, SECOND_ACCEPTED, ACTIVE, LUNCH) "
        sql += "VALUES ({})".format(",".join(["%s"] * 11))

        # Current time for match made
        now = datetime.now()

        val = (match_id, first_netid, second_netid, now, dhall, start_int, end_int, False, False, True, lunch)

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

    close_connection(cur, conn)


# Helper method, returns a list of selected dhalls from request
def find_possible_dhalls(row):
    available = []
    # dhalls indexed starting at 
    dhalls = row[6:6 + len(dhall_list)]

    for i in range(len(dhalls)):
        if dhalls[i] == True:
            available.append(dhall_list[i])

    return available


# Remove request from request table
def modify_request(request_id, match_id):
    sql = "UPDATE requests SET MATCHID = %s WHERE REQUESTID = %s"
    val = (match_id, request_id)

    cur, conn = new_connection()
    cur.execute(sql, val)
    close_connection(cur, conn)

    remove_request(request_id)
    print("Modified request", file=stdout)


def get_all_matches(netid):
    all_matches = []

    query = """SELECT * 
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


def get_name_from_netid(netid):
    cur, conn = new_connection()
    query = """SELECT name FROM users WHERE netid = %s"""
    cur.execute(query, [netid])
    row = cur.fetchone()
    close_connection(cur, conn)
    return row[0]


def get_name_and_num_from_netid(netid):
    cur, conn = new_connection()
    query = """SELECT name, phonenum FROM users WHERE netid = %s"""
    cur.execute(query, [netid])
    row = cur.fetchone()
    close_connection(cur, conn)
    return row[0], row[1]
    


def get_past_matches(netid):
    query = """SELECT first_netid, second_netid,
            end_window, dining_hall, match_id, lunch
            FROM matches
            WHERE first_netid = %s
            OR second_netid = %s
            ORDER BY end_window DESC"""

    cur, conn = new_connection()
    cur.execute(query, (netid, netid))
    matches = cur.fetchmany(4)
    close_connection(cur, conn)

    past_matches = []
    for match in matches:
        match_info = {}
        other_netid = match[0] if match[1] == netid else match[1]

        match_info['netid'] = other_netid
        match_info['name'], phonenum = get_name_and_num_from_netid(other_netid)
        match_info['day'] = match[2]
        match_info['dhall'] = match[3]
        match_info['id'] = match[4]
        match_info['meal'] = 'Lunch' if match[5] else 'Dinner'
        match_info['phonenum'] = phonenum

        past_matches.append(match_info)
        

    return past_matches


def accept_match(netid, matchid, phonenum):
    print("ACCEPT MATCH")
    print(netid)
    query = """SELECT match_id, first_netid, second_netid, first_accepted, second_accepted FROM matches
            WHERE match_id = %s"""

    cur, conn = new_connection()
    cur.execute(query, [matchid])
    row = cur.fetchone()

    netid_type = ""

    if row[1] == netid:
        # We know that the user is the first_netid
        netid_type = 'FIRST_ACCEPTED'
        if not row[4]:
            # If the other person has accepted, notify the other person that theres a match
            message = "{} accepted the match! Confirm that you'll be there on the MealMatch App!".format(
                get_name_from_netid(netid))
        else:
            # If the other person has not accepted, notify the other person that match is confirmed
            message = "{} also accepted the match! Have fun eating!".format(get_name_from_netid(netid))

    elif row[2] == netid:
        # We know that the user is the second_netid
        netid_type = 'SECOND_ACCEPTED'
        if not row[3]:
            # If the other person has accepted, notify the other person that theres a match
            message = "{} accepted the match! Confirm that you'll be there on the MealMatch App!".format(get_name_from_netid(netid))
        else:
            # If the other person has not accepted, notify the other person that match is confirmed
            message = "{} also accepted the match! Have fun eating!".format(get_name_from_netid(netid))
    notifications.send_message(message, phonenum)

    query = """UPDATE matches SET {} = TRUE WHERE MATCH_ID = %s""".format(netid_type)
    cur.execute(query, [matchid])
    close_connection(cur, conn)


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

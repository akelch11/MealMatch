from sys import stdout
from database import new_connection, close_connection


""""Check if the logged-in user has created a profile"""
def exists(netid):
    stmt = 'select name from users where netid=%s'

    cur, conn = new_connection()
    cur.execute(stmt, [netid])
    ret = cur.fetchone()
    close_connection(cur, conn)

    return ret != None
    

def get_profile(netid):
    keys = ["netid", "name","year","major","phonenum","bio"]
    stmt = 'select {} from users where netid=%s'.format(','.join(keys))
    
    cur, conn = new_connection()
    cur.execute(stmt, [netid])
    vals = cur.fetchone()
    close_connection(cur, conn)
    
    if not vals:
        vals = [""] * len(keys)
    return dict(zip(keys, vals))


# Create profile for user and update MongoDB
def create_profile(netid, name, year, major, phonenum, bio):
    sql = "INSERT INTO users (NETID,NAME,YEAR,MAJOR,PHONENUM,BIO) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (netid, name, year, major, phonenum, bio)

    cur, conn = new_connection()
    cur.execute(sql, val)
    close_connection(cur, conn)

    print("Profile created for:", netid, file=stdout)
    return netid


def edit_profile(netid, name, year, major, phonenum, bio):
    sql = "UPDATE users SET NAME=%s,YEAR=%s,MAJOR=%s,PHONENUM=%s,BIO=%s WHERE NETID=%s"
    val = (name, year, major, phonenum, bio, netid)
    
    cur, conn = new_connection()
    cur.execute(sql, val)
    close_connection(cur, conn)

    print("Profile updated for:", netid, file=stdout)
    return netid
    
    





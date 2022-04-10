import re
from sys import stdout
from big_lists import dept_code
import psycopg2

def new_conn():
    return psycopg2.connect(database="d4p66i6pnk5690",
                            user="uvqmavpcfqtovz",
                            password="e7843c562a8599da9fecff85cd975b8219280577dd6bf1a0a235fe35245973d2",
                            host="ec2-44-194-167-63.compute-1.amazonaws.com",
                            port="5432")


""""Check if the logged-in user has created a profile"""
def exists(netid):
    conn = new_conn()
    cur = conn.cursor()
    stmt = 'select name from users where netid=%s'
    cur.execute(stmt, (netid,))
    ret = cur.fetchone()
    conn.commit()
    conn.close()
    return ret != None

def get_profile(netid):
    conn = new_conn()
    cur = conn.cursor()
    stmt = 'select netid,name,year,major,phonenum,bio from users where netid=%s'
    cur.execute(stmt, (netid,))
    vals = cur.fetchone()
    if not vals: # TODO need a default value in the dropdown menus to correspond to the first time
        vals = [""] * 6
    conn.commit()
    conn.close()
    keys = ["netid", "name","year","major","phonenum","bio"]
    return dict(zip(keys, vals))


def check_bio(bio):
    """ we are taking this as a statement they have not
    filled in their bio"""
    if bio[-1] == chr(0x200a): # if still using default, update with new info
        return True, "Hi! My name is %s. I'm a %s major in the class of %s. "+\
        "Super excited to grab a meal with you. You can reach me at %s."+chr(0x200a)
    else:
        return False, bio


#Create profile for user and update MongoDB
def create_profile(netid, name, year, major, phonenum, bio):
    conn = new_conn()
    cur = conn.cursor()
    
    sql = "INSERT INTO users (NETID,NAME,YEAR,MAJOR,PHONENUM,BIO) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (netid, name, year, major, phonenum, bio)
    cur.execute(sql, val)

    conn.commit()
    conn.close()
    print("Profile created for:", netid, file=stdout)

    return netid

def edit_profile(netid, name, year, major, phonenum, bio):
    conn = new_conn()
    cur = conn.cursor()
    
    print(ord(bio[-1]))
    updated, bio = check_bio(bio) 
    print(ord(bio[-1]))
    print(name)
    if updated:
        bio = bio % (name, dept_code[major], year, phonenum)
    sql = "UPDATE users SET NAME=%s,YEAR=%s,MAJOR=%s,PHONENUM=%s,BIO=%s WHERE NETID=%s"
    val = (name, year, major, phonenum, bio, netid)
    cur.execute(sql, val)

    conn.commit()
    conn.close()
    print("Profile updated for:", netid, file=stdout)

    return netid
    
def create_user_table():
    conn = new_conn()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE users
            (NETID TEXT PRIMARY KEY NOT NULL,
            NAME TEXT NOT NULL,
            YEAR INT NOT NULL,
            MAJOR TEXT NOT NULL,
            PHONENUM TEXT NOT NULL,
            BIO TEXT);''')
    conn.commit()
    conn.close()
    
    





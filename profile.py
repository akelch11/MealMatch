
import psycopg2


#Check with CAS authentication and see whether user
#is logged in or not
def get_loginstatus(netid):
    login_status = True
    return login_status
    
#Check with MongoDB and see whether this user
#is logged in or not --> indication of whether
#to go to login screen or the screen with 4 widgets
def get_profilestatus(netid):
    profile_status = True
    return profile_status

#Create profile for user and update MongoDB
def create_profile(netid):
    create_user_table()
    print("Profile created for: " + netid)
    return netid
    
def create_user_table():
    conn = psycopg2.connect(database="d4p66i6pnk5690", user = "uvqmavpcfqtovz", password = "e7843c562a8599da9fecff85cd975b8219280577dd6bf1a0a235fe35245973d2", host = "ec2-44-194-167-63.compute-1.amazonaws.com", port = "5432")

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
    
    





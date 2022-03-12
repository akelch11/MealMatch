


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
    print("Profile created for: " + netid)
    return netid
    
    





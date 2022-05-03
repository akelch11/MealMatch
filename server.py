##
from sys import stdout, stderr
from flask import Flask, request, session
from flask import render_template, make_response, redirect, url_for
import user_profile

import meal_requests
import matcher
import auth
import keys
from big_lists import majors, dept_code, dhall_list
from dateutil import parser
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import date, datetime
import os

app = Flask(__name__)
app.secret_key = keys.APP_SECRET_KEY


@app.route('/landing', methods=['GET'])
def landing_page():
    html = render_template('landing.html',
                        landing=True)
    response = make_response(html)
    return response


@app.route('/', methods=['GET'])
def home_page(): 
    if session.get('username'):
        html = render_template('homescreen.html')
        response = make_response(html)
        return response
    else:
        return redirect('/landing')


@app.route('/next', methods=['GET'])
def go_to_cas():
    auth.authenticate()
    return redirect(url_for('homescreen'))


@app.route('/index', methods=['GET'])
def homescreen():
    if not session.get('username'):
        return redirect('/landing') # go to landing page
    if not user_profile.exists(session.get('username')):
        return redirect('/create_account')
    html = render_template('homescreen.html')
    response = make_response(html)
    return response

#ABOUT PAGE
@app.route('/about', methods=['GET'])
def about_method():
    logged_out = session.get('username') == None
    html = render_template('about.html',
                            logged_out=logged_out,
                            landing=False)
    response = make_response(html)
    return response

# get what the senior class's year is right now 
def senior_year():
    td = date.today()
    return td.year if td.month<8 else td.year+1
    
##########

#establish the route for creating/editing your account
@app.route('/edit_account', methods=['GET'])
@app.route('/create_account', methods=['GET'])
def update_form():
    username = auth.authenticate()

    profile_dict = user_profile.get_profile(username)


    title_value = ""
    button_value = ""
    # netid detected in system
    if user_profile.exists(username):
        title_value = 'Edit Your Profile!'
        button_value = "Submit Changes"
    else:
        title_value = 'Create Your Account!'
        button_value = "Get Started!"

    html = render_template('editprofile.html',
                    senior_class=senior_year(),
                    majors=majors,
                    existing_profile_info=profile_dict,
                    title_value = title_value,
                    button_value = button_value)
    response = make_response(html)
    return response

#HOMESCREEN --- SUBMIT PROFILE FORM 
@app.route('/submit_profile_form', methods=["GET"])
def form():
    name = request.args.get('name').strip()
    netid = auth.authenticate()
    year = request.args.get('year')
    major = request.args.get('major')
    bio = request.args.get('bio').strip()
    phonenum = request.args.get('phonenum')
    yeardict = {}
    for i in range(4):
        y = str(senior_year()+i)
        yeardict[y] = 'class of '+str(y)
    if year == "Grad College":
        y=str(senior_year()-1)
        yeardict[y] = year
        year = y
    if bio == "":
        tup = (name, dept_code[major],  yeardict[year], phonenum)
        print('bio tuple:', tup, file=stdout)
        bio = ("Hi! My name is %s. I'm a %s major in the %s. "
        "Super excited to grab a meal with you. You can reach me at %s.")\
        % tup
    if user_profile.exists(netid):
        user_profile.edit_profile(netid, name, int(year), major, phonenum, bio)
    else:
        user_profile.create_profile(netid, name, int(year), major, phonenum, bio)

    return redirect('/index')


#TEST ROUTE --- FORCE MATCHES 
@app.route('/forcematches', methods=['GET'])
def force_matches():
    matcher.match_requests()
    return redirect("/matches")


#SUBMIT REQUEST 
@app.route('/submitrequest', methods = ['GET'])
def submit_request():
    print('match has been made', file=stdout)
    meal_type = request.args.get('meal')
    print('Meal type', meal_type, file=stdout)
    dhall = request.args.get('location')
    print('DHALL STRING:', dhall, file=stdout)
    start_time = request.args.get('start')
    end_time = request.args.get('end')
    at_dhall = request.args.get('atdhall')

    # may not need backend validation if route is invisible
    # # if any args missing when request typed into the url
    # if not validate_req(meal_type, dhall, start_time, end_time, at_dhall):
    #     return redirect('/matches')

    meal_type = (meal_type == "lunch")
    at_dhall = (at_dhall == "True")

    # multiple dhalls can be selected via scheduled match
    # Dining halls are listed in between '-' of dhall request parameter
   
    dhall_arr = [hall_name in dhall for hall_name in dhall_list]
    print('dhall_arr: ', dhall_arr, file=stdout)


    if start_time == "now":
        start_time_datetime = datetime.now()
    else:
        start_time_datetime = parser.parse(start_time)

    end_time_datetime = parser.parse(end_time)

    success = meal_requests.add_request(auth.authenticate(), meal_type,
        start_time_datetime, end_time_datetime, dhall_arr, at_dhall)
    
    if success:
        return redirect("/matches")
    else:
        return redirect("/schedule?error=multiplerequests")
    

# def validate_req(meal_type, dhall, start_time, end_time, at_dhall):
#     # We have to run the same validation we did in html
#     # for if the user submits via the address link:(
#     return True


#HOMESCREEN -> SCHEDULE MATCH PAGE 
@app.route('/schedule', methods = ['GET'])
def schedulematch():
    error = request.args.get('error')

    if error is None:
        error = ""

    html = render_template('scheduledmatch.html',
                            dhalls=dhall_list,
                            error=error)
    response = make_response(html)
    return response
    
#HOMESCREEN -> ON DEMAND MATCH PAGE 
@app.route('/ondemand', methods=['GET'])
def ondemand():
    error = request.args.get('error')

    if error is None:
        error = ""

    html = render_template('ondemandmatch.html',
                            dhalls=dhall_list,
                            error = error)
    response = make_response(html)
    return response

#HOMESCREEN -> MATCHES PAGE 
@app.route('/matches', methods = ['GET'])
def get_matches():

    netid = auth.authenticate()
    all_matches = matcher.get_all_matches(netid)

    for i in range(len(all_matches)):
        match = all_matches[i]
        print('match row:', match, file = stderr)

        you_accepted = False
        opponent_accepted = True
        
        if netid == match[1]:
           you_accepted = match[7]
           opponent_accepted = match[8] 
        elif netid == match[2]:
           you_accepted = match[8]
           opponent_accepted = match[7]

        if match[13] == senior_year()-1:
            all_matches[i][13] = "Grad College" 

        if you_accepted and opponent_accepted:
            all_matches[i][7] = "Both Accepted!"
        elif you_accepted and not opponent_accepted:
            all_matches[i][7] = "You Accepted"
        else:
            all_matches[i][7] = ""


    if len(all_matches) == 0:
        html = render_template('nomatches.html')
    else:
        html = render_template('matches.html',
                                all_matches=all_matches)
    response = make_response(html)
    return response

#HOMESCREEN -> HISTORY PAGE
@app.route('/history', methods=['GET'])
def past_matches():
    netid = auth.authenticate()
    past_matches = matcher.get_past_matches(netid)
    html = render_template('history.html', 
                             past_matches=past_matches)
    response = make_response(html)
    return response
    

#HOMESCREEN -> REQUESTS PAGE 
@app.route('/requests', methods = ['GET'])
def get_requests():

    session_netid = auth.authenticate()
    all_requests = meal_requests.get_all_requests(session_netid)
    
    req_locations = []
    for req in all_requests:
        # get lists of booleans from database
        dhalls_bools_in_req = req[3:3+len(dhall_list)]
        # get which dining halls have true values
        dhalls_in_req = [dhall_list[i] 
        for i in range(len(dhall_list)) if dhalls_bools_in_req[i]]
        # append dining halls into a string split by /
        loc = '/'.join(dhalls_in_req)
        print('REQ: ', req, "\n Loc: ", loc)
        req_locations.append(loc)

    if len(all_requests) == 0:
        html = render_template('norequests.html')
    else:
        html = render_template('requests.html', 
                        all_requests=all_requests,
                        locations=req_locations)
    print("allreqs:", all_requests, file=stderr)
    print("req_locations:", req_locations, file=stderr)

    response = make_response(html)
    return response

#REMOVE REQUEST ON REQUESTS PAGE
@app.route('/removerequest', methods = ['POST'])
def remove_request():
    requestid = [request.args.get("requestid")]
    meal_requests.remove_requests(requestid)
    return redirect(url_for('get_requests'))

#ACCEPT MATCH ON MATCHES PAGE
@app.route('/acceptmatch', methods = ['POST'])
def accept_match():
    matchid = request.args.get("matchid")
    phonenum = request.args.get("phonenum")

    matcher.accept_match(auth.authenticate(), matchid, phonenum)
    return redirect(url_for('get_matches'))

#CANCEL MATCH ON MATCHES PAGE
@app.route('/cancelmatch', methods = ['POST'])
def remove_matches():
    matchid = request.args.get("matchid")
    phonenum = request.args.get("phonenum")

    matcher.remove_match(auth.authenticate(), matchid, phonenum)
    return redirect('/matches')

#CAS LOGOUT
@app.route('/logout', methods=['GET'])
def logout():
    auth.logout()


#ERROR HANDLING
@app.route('/test404', methods=['GET'])
def test404(e):
    return render_template('page404.html')

@app.errorhandler(404)
def error404(e):

    return render_template('page404.html'), 404

@app.errorhandler(500)
def error500(e):
    return render_template('page500.html'), 500

scheduler = BackgroundScheduler()
job = scheduler.add_job(meal_requests.clean_requests, 'interval', hours=5)
scheduler.start()

port = int(os.environ.get('PORT', 5001))
# app.run(host='0.0.0.0', port=port, debug=False)
app.run(host='localhost', port=port, debug=False)

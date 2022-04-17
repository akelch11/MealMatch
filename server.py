##
from sys import stdout, stderr
from flask import Flask, request, session
from flask import render_template, make_response, redirect, url_for
import profile
import matcher
import auth
import keys
from big_lists import majors, dept_code, dhall_list
from dateutil import parser
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
    else:
        html = render_template('landing.html',
                            landing=True)
    response = make_response(html)
    return response


@app.route('/next', methods=['GET'])
def go_to_cas():
    auth.authenticate()
    return redirect(url_for('homescreen'))


@app.route('/index', methods=['GET'])
def homescreen():
    if not session.get('username'):
        return redirect(url_for('landing_page')) # go to landing page
    if not profile.exists(session.get('username')):
        return redirect('/create_account')
    html = render_template('homescreen.html')
    response = make_response(html)
    return response

@app.route('/about', methods=['GET'])
def about_method():
    html = render_template('about.html')
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

    profile_dict = profile.get_profile(username)


    title_value = ""
    button_value = ""
    # netid detected in system
    if profile.exists(username):
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


@app.route('/submit_profile_form', methods=["GET"])
def form():
    name = request.args.get('name').strip()
    netid = auth.authenticate()
    year = request.args.get('year')
    major = request.args.get('major')
    bio = request.args.get('bio').strip()
    phonenum = request.args.get('phonenum').strip()
    yeardict = {}
    for i in range(4):
        y = str(senior_year()+i)
        yeardict[y] = 'class of '+str(y)
    if year == "Grad College":
        y=str(senior_year()-1)
        yeardict[y] = year
        year = y
    if name == "":
        if profile.exists(netid):
            redirect("/edit_account")
        else:
            redirect("/create_account")
    if bio == "":
        tup = (name, dept_code[major],  yeardict[year], phonenum)
        print(tup)
        bio = ("Hi! My name is %s. I'm a %s major in the %s. "
        "Super excited to grab a meal with you. You can reach me at %s.")\
        % tup
    if profile.exists(netid):
        profile.edit_profile(netid, name, int(year), major, phonenum, bio)
    else:
        profile.create_profile(netid, name, int(year), major, phonenum, bio)

    return redirect('/index')
    # html = render_template('homescreen.html')
    # response = make_response(html)
    # return response



@app.route('/forcematches', methods=['GET'])
def force_matches():
    matcher.match_requests()
    return redirect("/matches")



@app.route('/ondemand', methods=['GET'])
def ondemand():
    html = render_template('ondemandmatch.html',
                            dhalls=dhall_list)
    response = make_response(html)
    return response

@app.route('/matchlanddummy', methods = ['GET'])
def matchland():
    print('match making thing went through')
    meal_type = request.args.get('meal')
    print('Meal type', meal_type)
    dhall = request.args.get('location')
    print('DHALL STRING', dhall)
    start_time = request.args.get('start')
    end_time = request.args.get('end')
    at_dhall = request.args.get('atdhall')

    meal_type = (meal_type == "lunch")
    at_dhall = (at_dhall == "True")

    if at_dhall == "True":
        at_dhall = True
    else:
        at_dhall = False

    dhall_list = ["Wucox", "RoMa", "Forbes", "CJL", "Whitman"]
    dhall_arr = []

    # multiple dhalls were selected via scheduled match
    # Dining halls are listed in between '-' of dhall request parameter
   
    if '-' in dhall:
        print('multiple dhalls')
        for hall_name in dhall_list:
            if hall_name not in dhall:
                dhall_arr.append(False)
            else:
                dhall_arr.append(True)
    else:
        # one dining hall selected
        for i in range(len(dhall_list)):
            if dhall_list[i].lower() == dhall.lower():
                dhall_arr.append(True)
            else:
                dhall_arr.append(False)
    print(dhall_arr, file = stderr)


    if start_time == "now":
        start_time_datetime = datetime.now()
    else:
        start_time_datetime = parser.parse(start_time)

    end_time_datetime = parser.parse(end_time)

    matcher.add_request(auth.authenticate(), meal_type, start_time_datetime, end_time_datetime, dhall_arr, at_dhall)
    return redirect("/matches")


@app.route('/schedulematchlanddummy', methods = ['GET'])
def scheduleland():
    meal_type = request.args.get('meal')
    dhall = request.args.get('location')
    start_time = request.args.get('start')
    end_time = request.args.get('end')

    html = render_template('matchlanddummy.html', \
            meal = meal_type, location = dhall, start = start_time, end = end_time)
    
    response = make_response(html)
    return response
######

@app.route('/schedule', methods = ['GET'])
def schedulematch():
     html = render_template('scheduledmatch.html',
                            dhalls=dhall_list)
     response = make_response(html)
     return response
    

@app.route('/match', methods=['GET'])
def match():
    html = render_template('ondemandmatch.html',
                            dhalls=dhall_list)
    print('call match route')
    response = make_response(html)
    return response


@app.route('/matches', methods = ['GET'])
def get_matches():

    session_netid = auth.authenticate()
    all_matches = matcher.get_all_matches(session_netid)

    for i in range(len(all_matches)):
        match = all_matches[i]

        you_accepted = False
        opponent_accepted = True

        if session_netid == match[1]:
           you_accepted = match[5]
           opponent_accepted = match[6] 
        elif session_netid == match[2]:
           you_accepted = match[6]
           opponent_accepted = match[5]

        if you_accepted and opponent_accepted:
            all_matches[i][5] = "Both Accepted!"
        elif you_accepted and not opponent_accepted:
            all_matches[i][5] = "You Accepted"
        elif not you_accepted and opponent_accepted:
            all_matches[i][5] = ""
        else:
            all_matches[i][5] = ""

        print(all_matches[0][5])


    html = render_template('matches.html', all_matches = all_matches)
    response = make_response(html)
    return response


@app.route('/removerequest', methods = ['POST'])
def remove_requests():

    requestid = request.args.get("requestid")
    matcher.remove_request(requestid)
    return redirect(url_for('get_requests'))


@app.route('/acceptmatch', methods = ['POST'])
def accept_match():
    matchid = request.args.get("matchid")
    phonenum = request.args.get("phonenum")

    matcher.accept_match(auth.authenticate(), matchid, phonenum)
    return redirect(url_for('get_matches'))


@app.route('/cancelmatch', methods = ['POST'])
def remove_matches():
    matchid = request.args.get("matchid")
    phonenum = request.args.get("phonenum")

    matcher.remove_match(auth.authenticate(), matchid, phonenum)
    return redirect(url_for('get_matches'))


@app.route('/requests', methods = ['GET'])
def get_requests():

    session_netid = auth.authenticate()
    all_requests = matcher.get_all_requests(session_netid)
    
    dHall_indexes = {3: 'Wucox', 4: 'Roma', 5: 'Forbes', 6: 'CJL', 7: 'Whitman'}
    req_locations = []
    
    for req in all_requests:
        loc = ""
        for i in range(3,8):
            print(req)
            if req[i]:
                loc += (dHall_indexes[i] + "/")
                print(dHall_indexes[i])
        loc = loc[:-1]
        req_locations.append(loc)


    html = render_template('requests.html', all_requests = all_requests, \
                    locations = req_locations, length = len(all_requests))
    print(all_requests, file = stderr)
    print(req_locations)
    response = make_response(html)
    return response

@app.route('/logout', methods=['GET'])
def logout():
    auth.logout()

@app.errorhandler(404)
def error404(e):
    return render_template('page404.html'), 404

@app.errorhandler(500)
def error500(e):
    return render_template('page500.html'), 500


port = int(os.environ.get('PORT', 5001))
# app.run(host='0.0.0.0', port=port, debug=False)
app.run(host='localhost', port=port, debug=False)

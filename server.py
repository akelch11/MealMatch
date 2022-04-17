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
        print('bio tuple:', tup, file=stdout)
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
    print('match has been made', file=stdout)
    meal_type = request.args.get('meal')
    print('Meal type', meal_type, file=stdout)
    dhall = request.args.get('location')
    print('DHALL STRING:', dhall, file=stdout)
    start_time = request.args.get('start')
    end_time = request.args.get('end')
    at_dhall = request.args.get('atdhall')

    meal_type = (meal_type == "lunch")
    at_dhall = (at_dhall == "True")

    # multiple dhalls can be selected via scheduled match
    # Dining halls are listed in between '-' of dhall request parameter
   
    dhall_arr = [hall_name in dhall.split('-')
                for hall_name in dhall_list]
    print('dhall_arr: ', dhall_arr, file=stdout)


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

    html = render_template('matches.html', all_matches = all_matches)
    response = make_response(html)
    return response


@app.route('/removerequest', methods = ['POST'])
def remove_requests():
    requestid = request.args.get("requestid")
    matcher.remove_request(requestid)
    return redirect(url_for('get_requests'))


@app.route('/cancelmatch', methods = ['POST'])
def remove_matches():
    matchid = request.args.get("matchid")
    matcher.remove_match(matchid)
    return redirect(url_for('get_matches'))


@app.route('/requests', methods = ['GET'])
def get_requests():

    session_netid = auth.authenticate()
    all_requests = matcher.get_all_requests(session_netid)
    
    req_locations = []
    for req in all_requests:
        # get lists of booleans from database
        dhalls_bools_in_req = req[3:3+len(dhall_list)]
        # get which dining halls have true values
        dhalls_in_req = [dhall_list[i] 
        for i in range(len(dhall_list)) if dhalls_bools_in_req[i]]
        # append dining halls into a string split by /
        loc = '/'.join(dhalls_in_req)
        req_locations.append(loc)

    html = render_template('requests.html', 
                        all_requests=all_requests,
                        locations=req_locations)
    print("allreqs:", all_requests, file=stderr)
    print("req_locations:", req_locations, file=stderr)
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

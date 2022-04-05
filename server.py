##
from ast import parse
from curses import endwin
import re
from sys import stderr
# from urllib import response
from flask import Flask, request, make_response, redirect, url_for, session
from flask import render_template
import profile
import matcher
import auth
import keys
from big_lists import majors, dhall_list, dept_code
from dateutil import parser
from datetime import date, datetime
import random
import string
import os

app = Flask(__name__)
app.secret_key = keys.APP_SECRET_KEY


@app.route('/landing', methods=['GET'])
def landing_page():
    html = render_template('landing.html')
    response = make_response(html)
    return response


@app.route('/next', methods=['GET'])
def go_to_cas():
    auth.authenticate()
    return redirect(url_for('homescreen'))


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def homescreen():
    # if not logged in
    if not session.get('username'):
        auth.authenticate() #TODO land->login->home
    # if not request.args.get('ticket'): # experiment
        # return redirect(url_for('landing_page')) # go to landing page
    if not profile.exists(session.get('username')):
        return redirect('/edit_account')
    html = render_template('homescreen.html')
    response = make_response(html)
    return response

# get what the senior class's year is right now 
def senior_year():
    td = date.today()
    return td.year if td.month<8 else td.year+1
    
#establish the route for creating/editing your account
@app.route('/edit_account', methods=['GET'])
def update_form():
    # should go to home_screen if account created
    username = auth.authenticate()

    # username = session.get('username')
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

""" Strip the bio of all whitespace except the default-bio flag, chr(0x200a)"""
def process_bio(req):
    bio = req.strip()
    if req and req[-1] == chr(0x200a):
        bio += chr(0x200a)
    return bio


@app.route('/submit_profile_form', methods=["GET"])
def form():
    name = request.args.get('name').strip()
    netid = auth.authenticate()
    year = request.args.get('year')
    major = request.args.get('major')
    bio = process_bio(request.args.get('bio'))
    phonenum = request.args.get('phonenum').strip()
    if bio == "":
        tup = (name, dept_code[major], year, phonenum)
        bio = ("Hi! My name is %s. I'm a %s major in the class of %s. "+\
        "Super excited to grab a meal with you. You can reach me at %s."+chr(0x200a))\
        % tup
    if profile.exists(netid):
        profile.edit_profile(netid, name, int(year), major, phonenum, bio)
    else:
        profile.create_profile(netid, name, int(year), major, phonenum, bio)

    return redirect('/')
    # html = render_template('homescreen.html')
    # response = make_response(html)
    # return response


@app.route('/ondemand', methods=['GET'])
def ondemand():
    html = render_template('ondemandmatch.html')
    response = make_response(html)
    return response

@app.route('/matchlanddummy', methods = ['GET'])
def matchland():
    meal_type = request.args.get('meal')
    dhall = request.args.get('location')
    start_time = request.args.get('start')
    end_time = request.args.get('end')
    at_dhall = request.args.get('atdhall')

    if meal_type == "lunch":
        meal_type = True
    else:
        meal_type = False

    if at_dhall == "True":
        at_dhall = True
    else:
        at_dhall = False

    dhall_arr = []

    # multiple dhalls were selected via scheduled match
    # Dining halls are listed in between '-' of dhall request parameter
    if '-' in dhall:
        # 
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

    netid = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(5))

    if start_time == "now":
        start_time_datetime = datetime.now()
    else:
        start_time_datetime = parser.parse(start_time)

    end_time_datetime = parser.parse(end_time)

    matcher.add_request(netid, meal_type, start_time_datetime, end_time_datetime, dhall_arr, at_dhall)
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

@app.route('/schedule', methods = ['GET'])
def schedulematch():
     html = render_template('scheduledmatch.html')
     response = make_response(html)
     return response
    

@app.route('/match', methods=['GET'])
def match():
    html = render_template('ondemandmatch.html')
    print('call match route')
    response = make_response(html)
    return response

@app.route('/logout', methods=['GET'])
def logout():
    auth.logout()

@app.route('/matches', methods = ['GET'])
def get_matches():

    session_netid = auth.authenticate()
    session_netid = "ddalia"

    all_matches = matcher.get_all_matches(session_netid)


    html = render_template('matches.html', all_matches = all_matches)
    response = make_response(html)
    return response


@app.route('/requests', methods = ['GET'])
def get_requests():

    session_netid = auth.authenticate()
    session_netid = "ddalia"

    all_requests = matcher.get_all_requests(session_netid)


    html = render_template('requests.html', all_requests = all_requests)
    response = make_response(html)
    return response

port = int(os.environ.get('PORT', 5001))
# app.run(host='0.0.0.0', port=port, debug=False)
app.run(host='localhost', port=port, debug=False)

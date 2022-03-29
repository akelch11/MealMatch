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
from dateutil import parser
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
@app.route('/homescreen', methods=['GET'])
def homescreen():
    # if not logged in 
    if not session.get('username'):
        return redirect(url_for('landing_page')) # got to landing page

    if not profile.exists(session.get('username')):
        return redirect(url_for('create_form'))
    html = render_template('homescreen.html')
    response = make_response(html)
    return response


@app.route('/create', methods=['GET'])
def create_form():
    
    # should go to home_screen if account created
    html = render_template('createaccount.html',
                           response="")
    response = make_response(html)
    return response


@app.route('/submit_create_form', methods=["GET"])
def form():
    name = request.args.get('name')
    netid = session.get('username')
    year = request.args.get('year')
    major = request.args.get('major')
    bio = request.args.get('bio')
    phonenum = request.args.get('phonenum')

    if name is None:
        name = netid

    if year is None:
        year = ""

    if major is None:
        major = ""

    if bio is None:
        bio = ""

    if phonenum is None:
        phonenum = ""

    profile.create_profile(netid, name, int(year), major, phonenum, bio)

    html = render_template('createaccount.html')
    response = make_response(html)
    return response


@app.route('/matchdummy', methods=['GET'])
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


    if meal_type == "lunch":
        meal_type = True
    else:
        meal_type = False

    dhall_list = ["WUCOX", "ROMA", "FORBES", "CJL", "WHITMAN"]
    dhall_arr = []
    for i in range(len(dhall_list)):
        if dhall_list[i].lower() == dhall.lower():
            dhall_arr.append(True)
        else:
            dhall_arr.append(False)

    netid = "avaidya"

    start_time_datetime = parser.parse(start_time)
    end_time_datetime = parser.parse(end_time)
    matcher.add_request(netid, meal_type, start_time_datetime, end_time_datetime, dhall_arr)

    html = render_template('matchlanddummy.html', meal = meal_type, location = dhall, \
                          start = start_time, end = end_time)
    response = make_response(html)
    
    if meal_type is None:
        meal_type = ""

    if dhall is None:
        dhall = ""

    if start_time is None:
        start_time = ""

    if end_time is None:
        end_time = ""
   # send match request to database
   # matcher.add_request(start_time, dhall, end_time)


    return response

@app.route('/ondemand', methods=["GET"])
def ondemand_form():
    mealtime = request.args.get('mealtime')
    dhall = request.args.get('dhall')
    endtime = request.args.get('endtime')
    if mealtime is None:
        mealtime = ""

    if dhall is None:
        dhall = ""

    if endtime is None:
        endtime = ""

    matcher.add_request(mealtime, dhall, endtime)

    html = render_template('ondemandmatch.html')
    response = make_response(html)
    return response


# Display either CAS profile login screen or
# welcome screen based on whether user is logged
# into the application
@app.route('/getloginstatus', methods=['GET'])
def login_status():
    payload = request.json
    netid = payload["netid"]
    login_status = profile.get_loginstatus(netid)
    return jsonify({
        'status': 'OK',
        'data': {"login_status": login_status}
    })


# Display either CAS profile login screen or
# welcome screen based on whether user is logged
# into the application
@app.route('/getprofilestatus', methods=['GET'])
def profile_status():
    payload = request.json
    netid = payload["netid"]
    profile_status = profile.get_profilestatus(netid)
    return jsonify({
        'status': 'OK',
        'data': {"profile_status": profile_status}
    })


@app.route('/status', methods=["GET"])
def status():
    return jsonify({"message": "ok"})


@app.route('/match', methods=['GET'])
def match():
    html = render_template('ondemandmatch.html')
    print('call match route')
    response = make_response(html)
    return response

@app.route('/logout', methods=['GET'])
def logout():
    auth.logout()

port = int(os.environ.get('PORT', 5001))
# app.run(host='0.0.0.0', port=port, debug=False)
app.run(host='localhost', port=port, debug=False)

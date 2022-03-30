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
    html = render_template('createaccount.html')
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
        year = "0"

    if major is None:
        major = ""

    if bio is None:
        bio = ""

    if phonenum is None:
        phonenum = ""

    profile.create_profile(netid, name, int(year), major, phonenum, bio)

    html = render_template('homescreen.html')
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

    netid = session.get('username')

    start_time_datetime = parser.parse(start_time)
    end_time_datetime = parser.parse(end_time)

    matcher.add_request(netid, meal_type, start_time_datetime, end_time_datetime, dhall_arr)
    return get_matches()


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
    all_matches = matcher.get_all_matches()
    html = render_template('matches.html', all_matches = all_matches)
    response = make_response(html)
    return response


port = int(os.environ.get('PORT', 5001))
# app.run(host='0.0.0.0', port=port, debug=False)
app.run(host='localhost', port=port, debug=False)




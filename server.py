from curses import endwin
import re
from sys import stderr
from urllib import response
from flask import Flask, request, make_response
from flask import render_template
import profile
import matcher
import os
app = Flask(__name__)

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def search_form():

    html = render_template('createaccount.html',
                            response = "")
    response = make_response(html)
    return response

@app.route('/form', methods=["GET"])
def form():
    
    name = request.args.get('name')
    netid = request.args.get('netid')
    year = request.args.get('year')
    major = request.args.get('major')
    bio = request.args.get('bio')
    phonenum = request.args.get('phonenum')

    if name is None:
        name = ""

    if netid is None:
        netid = ""

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


#Display either CAS profile login screen or 
#welcome screen based on whether user is logged
#into the application
@app.route('/getloginstatus', methods=['GET'])
def login_status():
    payload = request.json
    netid = payload["netid"]
    login_status = profile.get_loginstatus(netid)
    return jsonify({
        'status': 'OK',
        'data': {"login_status": login_status}
        })

#Display either CAS profile login screen or 
#welcome screen based on whether user is logged
#into the application
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

@app.route('/homescreen', methods = ['GET'])
def homescreen():
    html = render_template('homescreen.html')
    response = make_response(html)
    return response

@app.route('/match', methods = ['GET'])
def match():
    html = render_template('ondemandmatch.html')
    print('call match route')
    response = make_response(html)
    return response


port = int(os.environ.get('PORT', 5001))
app.run(host='0.0.0.0', port=port, debug=False )

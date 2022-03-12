from flask import Flask, request, jsonify
import profile
app = Flask(__name__)

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


#Create a profile for a user in MongoDB
@app.route('/createprofile', methods=['POST'])
def create_profile():
    payload = request.json
    netid = payload["netid"]
    netid_new = profile.create_profile(netid)
    return jsonify({
        'status': 'OK',
        'data': {"netid": netid_new}
        })

#Create a profile for a user in MongoDB
@app.route('/createprofile', methods=['POST'])
def create_profile():
    payload = request.json
    netid = payload["netid"]
    netid_new = profile.create_profile(netid)
    return jsonify({
        'status': 'OK',
        'data': {"netid": netid_new}
        })


@app.route('/status', methods=["GET"])
def status():
    return jsonify({"message": "ok"})


app.run(host='0.0.0.0', port=8020, debug=False )

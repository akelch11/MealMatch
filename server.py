from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/modifications', methods=['POST'])
def mod():
    payload = request.json
    num_mod, new_file = process.get_modifications(payload['filename'])
    return jsonify({
        'status': 'OK',
        'data': {"number of modifications": num_mod,
                 "new file": new_file
                }
        })


@app.route('/status', methods=["GET"])
def status():
    return jsonify({"message": "ok"})


app.run(host='0.0.0.0', port=8020, debug=False )

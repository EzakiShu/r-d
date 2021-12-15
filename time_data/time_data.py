from flask import Flask, request, jsonify

app = Flask(__name__)
time_data = {"detection1": 0, "detection2": 0, "detection3": 0}


@app.route("/send-time-detection1", methods=["POST"])
def time_detection1():
    global time_data
    time_data["detection1"] = request.form["time_detection1"]
    for t in time_data.items():
        print(t)
    return ""


@app.route("/send-time-detection2", methods=["POST"])
def time_detection2():
    global time_data
    time_data["detection2"] = request.form["time_detection2"]
    for t in time_data.items():
        print(t)
    return ""


@app.route("/send-time-detection3", methods=["POST"])
def time_detection3():
    global time_data
    time_data["detection3"] = request.form["time_detection3"]
    for t in time_data.items():
        print(t)
    return ""


@app.route("/get-time", methods=["POST"])
def get_time():
    global time_data
    for t in time_data.items():
        print(t)
    return jsonify(time_data)


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=10000, threaded=True)

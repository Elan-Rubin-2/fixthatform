from flask import Flask, render_template, Response, request,redirect,jsonify
import cv2
import os
import numpy as np
from threading import Thread
from inference import get_model
import supervision as sv
import time
import os
from models import *
from detectors import *
# Initialize Flask app
app = Flask(__name__, template_folder='./',static_folder='./static')
testModel = CerebrasModel("llama3.1-8b",1024/(2**4))
testModel.getResponse("give all future responses in one paragraph")
global egen
@app.route('/')
def home():
    return redirect('/home')

@app.route('/home')
def index():
    return render_template('index5.html')

@app.route('/prompt',methods=['POST','GET'])
def respond():
    if request.method == "POST":
        try:
            data = request.get_json()
            inp = data["input"]
        except Exception as e:
            print("Error caught:", e)
            return jsonify({"message": "failed to parse input"}), 400

    res = testModel.getResponse(inp)
    return jsonify({'response':res,'inp':inp})

@app.route('/get_user_info',methods=['POST','GET'])
def getUser():
    if request.method == "POST":
        try:
            data = request.get_json()
            name = data["name"]
            age = data["age"]
            sex = data["sex"]
            inp = f"Hi. My name is {name}. I am {age} years of age and my gender is {sex}."
        except Exception as e:
            print("Error caught:", e)
            return jsonify(data), 400

    res = testModel.getResponse(inp)
    return jsonify({'response':res,'inp':inp})
    # return "Your name is "+first_name + last_name

# Load the pose estimation model
model = get_model(model_id="person-pose-zjwnq/2")
cam = cv2.VideoCapture(0)
egen = 'def'
@app.route("/video/<ex>")
def video(ex):
    egen = ex
    # ex = request.args.get('exc', default = 'def', type = str)
    return render_template('vid.html',e=ex)

@app.route('/video_feed',methods=['POST','GET'])
def video_feed():
    # inp = 'leg-raises'
    # if request.method == "POST":
    #     data = request.get_json()
    #     inp = data["ex"]'

    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
    
@app.route('/video_stream', methods=['POST'])
def video_stream():
    global last_frame

    if 'image' not in request.files:
        return "No image part", 400

    img_bytes = request.files['image'].read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is not None:
        last_frame = img
        return "Frame received", 200
    else:
        return "Failed to decode image", 400

def gen_frames():
    global last_frame
    while True:
        frame = last_frame
        # exc = egens
        if frame is not None:
            # if exc == 'def':
            #     frame = frame
            # elif exc == 'squat':
            #     frame = SquatDetectPerFrame(frame)
            # elif exc == 'leg-raises':
            #     frame = LegRaiseDetectPerFrame(frame)
            # elif exc == 'thoracic-extensions':
            frame = SquatDetectPerFrame(frame)
            # elif exc == 'shoulder-press':
            #     frame = ShoulderPressDetectPerFrame(frame)
            # elif exc == 'shoulder-raise':
            #     frame = ShoulderRaiseDetectPerFrame(frame)
            try:
                ret, buffer = cv2.imencode('.jpg', cv2.flip(frame, 1))
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                print(f"Error in frame generation: {e}")
        else:
            pass




if __name__ == '__main__':
    app.run(debug=True)

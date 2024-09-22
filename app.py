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
# Initialize Flask app
app = Flask(__name__, template_folder='./',static_folder='./static')
testModel = CerebrasModel("llama3.1-8b",1024/(2**4))
testModel.getResponse("give all future responses in one paragraph")

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
            inp = f"Hi. My name is {name}. I am {age} years of age and my gender is {sex}"
        except Exception as e:
            print("Error caught:", e)
            return jsonify(data), 400

    res = testModel.getResponse(inp)
    return jsonify({'response':res,'inp':inp})
    # return "Your name is "+first_name + last_name

if __name__ == '__main__':
    app.run(debug=True)

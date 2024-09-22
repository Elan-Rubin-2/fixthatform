## Launching the Application
**Ensure the required dependencies are active in the virutal enviornment in the project directory:**

  python -m venv myenv && ./myenv/bin/activate && python -m pip install -r requirements.txt
  
**Run the Flask application locally:**
  
  python app.py
 

## Inspiration
Post-operation recovery is a vital aspect of healthcare. Keeping careful track of rehabilitation can ensure that patients get better as quickly as possible. We were inspired to create this project when thinking of elderly and single people who are in need of assistance when recovering from surgery. We imagined Dr. Debbie as a continuation of the initial care that patients received, which could carry on into their homes. 

## What it does
The program currently provides services like physical therapy routines aided by computer vision, and a medicine routine which the AI model reinforces. Along the way, patients can interact with a live AI assistant which speaks to them. This makes the experience feel authentic while remaining professional and informational.

## How we built it
Our application consisted of two primary machine learning models interacting with our Bootstrap frontend and Flask backend. 
- We choose to use Bootstrap in the frontend to seamlessly interact with the Rive animation avatar of Dr. Debbie and mockup a cohesive theme for our web application.
- Utilizing Flask, we were able to incorporate our model logic for the person pose detection model via Roboflow directly into Python.
- In order to support real-time physical therapy correction, we use a Deep Neural Network trained to perform keypoint recognition on your local live camera feed. It makes keypoint detections, calculating the angles of figures in the frame, allowing us to determine how correctly the patient is performing a certain physical therapy exercise.
- Additionally, we utilized Cerebus Llama 3.1-8b to interact directly with the application user, serving as the direct AI companion for the user to communicate with either through text or a text-to-speech option!

## Challenges we ran into
We ran into challenges with the computer vision models. Tracking the patient's body was a balancing act between accuracy and speed. Some models were tailored towards different applications, which meant experimenting with different training sets and parameters.
Integrating the live avatar of Dr. Debbie was a challenge because the animation service, Rive, was new to the team. Interfacing the animation in a way that felt interactive and realistic was very challenging.
Because of the time constraints of the hackathon, we were forced to prioritize certain aspects of the project, while scrapping others. For example, we found some features like medicine scanning and predictive modeling were feasible, but not worth the effort considering our resources.

## What's next for Dr. Debbie
Our next two initiatives for Dr. Debbie include converting the application to a mobile app or a Windows desktop application. To reach more users on a more diverse variety of technologies, being able to load Dr. Debbie on your phone or your home computer can be much more convenient for our users. In addition to this, we hope to expand the statistical analysis of Dr. Debbie. To improve the connection between healthcare professionals and patients when they cannot be together in person, Dr. Debbie can provide data to professionals asynchronously helping them stay current with patient status.

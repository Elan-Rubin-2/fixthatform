# from flask import Flask, render_template, Response, request
import cv2
import os
import numpy as np
from threading import Thread
from inference import get_model
import supervision as sv
import time

# Load the pose estimation model
model = get_model(model_id="person-pose-zjwnq/2")

# Constants for keypoints
NOSE = 0
nose = 1
RIGHT_SHOULDER = 2
LEFT_SHOULDER = 3
RIGHT_ELBOW = 4
LEFT_ELBOW = 5
RIGHT_hand = 6
LEFT_hand = 7
RIGHT_HIP = 8
LEFT_HIP = 9

# Thresholds for shoulder press movement
min_press_angle = 160  # Minimum elbow extension angle for proper press
max_flare_angle = 30  # Maximum angle for elbow flare (arms should go straight up)
# Thresholds for shoulder raise movement
min_raise_angle = 70  # Minimum shoulder raise angle (just below shoulder height)
max_raise_angle = 110  # Maximum shoulder raise angle (avoid over-raising)

# Helper function to calculate the angle between three points
def calculate_angle(a, b, c):
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)
    return np.degrees(angle)

# Function to check overhead shoulder press form and provide feedback
def check_overhead_shoulder_press_form(keypoints):
    feedback = []
    highlights = []

    try:
        right_shoulder = np.array(keypoints['right-shoulder'][0])
        left_shoulder = np.array(keypoints['left-shoulder'][0])
        
        right_elbow = np.array(keypoints['right-elbow'][0])
        left_elbow = np.array(keypoints['left-elbow'][0])
        
        right_hand = np.array(keypoints['right-hand'][0])
        left_hand = np.array(keypoints['left-hand'][0])
        
        right_hip = np.array(keypoints['right-hip'][0])
        left_hip = np.array(keypoints['left-hip'][0])
        
    except KeyError as e:
        print(f"Missing keypoints: {e}")
        return "Keypoints not detected", []

    # Calculate the elbow extension angles for the shoulder press
    right_press_angle = calculate_angle(right_hand, right_elbow, right_shoulder)
    left_press_angle = calculate_angle(left_hand, left_elbow, left_shoulder)

    # Calculate the angle between the shoulders and elbows to detect elbow flare
    right_flare_angle = calculate_angle(right_hip, right_shoulder, right_elbow)
    left_flare_angle = calculate_angle(left_hip, left_shoulder, left_elbow)

    # Provide feedback for the right arm press
    if right_press_angle < min_press_angle:
        feedback.append("Extend your right arm fully.")
        highlights.append(('right-shoulder', 'right-elbow', 'right-hand'))
    if right_flare_angle > max_flare_angle:
        feedback.append("Keep your right arm straight, avoid flaring out.")
        highlights.append(('right-shoulder', 'right-elbow'))

    # Provide feedback for the left arm press
    if left_press_angle < min_press_angle:
        feedback.append("Extend your left arm fully.")
        highlights.append(('left-shoulder', 'left-elbow', 'left-hand'))
    if left_flare_angle > max_flare_angle:
        feedback.append("Keep your left arm straight, avoid flaring out.")
        highlights.append(('left-shoulder', 'left-elbow'))

    if feedback:
        return " ".join(feedback), highlights
    else:
        return "Good form. Keep it up!", []

# Detect per frame logic for overhead shoulder press detection
def ShoulderPressDetectPerFrame(frame):
    frame = cv2.flip(frame, 1)
    results = model.infer(frame)[0]

    keypoints = {}
    for i in results.predictions:
        for j in i.keypoints:
            keypoints[j.class_name.lower().replace(' ', '-')] = [(int(j.x), int(j.y))]
            cv2.circle(frame, (int(j.x), int(j.y)), radius=10, color=(0, 0, 255), thickness=-1)

    # Validate the keypoints before further processing
    if not keypoints:
        return frame

    # Check overhead shoulder press form
    try:
        press_feedback, press_highlights = check_overhead_shoulder_press_form(keypoints)

        cv2.putText(frame, press_feedback, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    except Exception as e:
        print(f"Error in form detection: {e}")
        pass

    # Draw skeleton
    annotated_image = sv.EdgeAnnotator(color=sv.Color.GREEN, thickness=5).annotate(frame, sv.KeyPoints.from_inference(results))
    try:
        # Highlight incorrect form in red only for the joints involved in the shoulder press
        for joint_pair in press_highlights:
            for i in range(len(joint_pair) - 1):
                start_point = keypoints[joint_pair[i]][0]
                end_point = keypoints[joint_pair[i+1]][0]
                cv2.line(annotated_image, start_point, end_point, (0, 0, 255), 5)
    except Exception as e:
        print(f"Error in drawing highlights: {e}")

    return cv2.flip(annotated_image, 1)

# Function to check front shoulder raise form and provide feedback
def check_front_shoulder_raise_form(keypoints):
    feedback = []
    highlights = []

    try:
        # Get positions of key points for shoulder, elbow, and hand
        right_shoulder = np.array(keypoints['right-shoulder'][0])
        left_shoulder = np.array(keypoints['left-shoulder'][0])
        
        right_elbow = np.array(keypoints['right-elbow'][0])
        left_elbow = np.array(keypoints['left-elbow'][0])
        
        right_hand = np.array(keypoints['right-hand'][0])
        left_hand = np.array(keypoints['left-hand'][0])
        
        right_hip = np.array(keypoints['right-hip'][0])
        left_hip = np.array(keypoints['left-hip'][0])
        
    except KeyError as e:
        print(f"Missing keypoints: {e}")
        return "Keypoints not detected", []

    # Calculate the shoulder raise angles
    right_raise_angle = calculate_angle(right_hip, right_shoulder, right_elbow)
    left_raise_angle = calculate_angle(left_hip, left_shoulder, left_elbow)

    # Provide feedback if the shoulder raise is insufficient or exaggerated
    if right_raise_angle < min_raise_angle:
        feedback.append("Raise your right arm higher.")
        highlights.append(('right-shoulder', 'right-elbow', 'right-hand'))
    elif right_raise_angle > max_raise_angle:
        feedback.append("Lower your right arm, avoid over-raising.")
        highlights.append(('right-shoulder', 'right-elbow', 'right-hand'))

    if left_raise_angle < min_raise_angle:
        feedback.append("Raise your left arm higher.")
        highlights.append(('left-shoulder', 'left-elbow', 'left-hand'))
    elif left_raise_angle > max_raise_angle:
        feedback.append("Lower your left arm, avoid over-raising.")
        highlights.append(('left-shoulder', 'left-elbow', 'left-hand'))

    if feedback:
        return " ".join(feedback), highlights
    else:
        return "Good form. Keep it up!", []

# Detect per frame logic for front shoulder raise detection
def ShoulderRaiseDetectPerFrame(frame):
    frame = cv2.flip(frame, 1)
    results = model.infer(frame)[0]

    keypoints = {}
    for i in results.predictions:
        for j in i.keypoints:
            keypoints[j.class_name.lower().replace(' ', '-')] = [(int(j.x), int(j.y))]
            cv2.circle(frame, (int(j.x), int(j.y)), radius=10, color=(0, 0, 255), thickness=-1)

    # Validate the keypoints before further processing
    if not keypoints:
        return frame

    # Check front shoulder raise form
    try:
        shoulder_feedback, shoulder_highlights = check_front_shoulder_raise_form(keypoints)

        cv2.putText(frame, shoulder_feedback, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    except Exception as e:
        print(f"Error in form detection: {e}")
        pass

    # Draw skeleton
    annotated_image = sv.EdgeAnnotator(color=sv.Color.GREEN, thickness=5).annotate(frame, sv.KeyPoints.from_inference(results))
    try:
        # Highlight incorrect form in red only for the joints involved in the shoulder raise
        for joint_pair in shoulder_highlights:
            for i in range(len(joint_pair) - 1):
                start_point = keypoints[joint_pair[i]][0]
                end_point = keypoints[joint_pair[i+1]][0]
                cv2.line(annotated_image, start_point, end_point, (0, 0, 255), 5)
    except Exception as e:
        print(f"Error in drawing highlights: {e}")

    return cv2.flip(annotated_image, 1)

# Thresholds for thoracic extension
min_extension_angle = 10  # Minimum angle for proper extension detection
max_extension_angle = 30  # Maximum angle for controlled extension movement

# Helper function to calculate the angle between three points
def calculate_angle(a, b, c):
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)
    return np.degrees(angle)

# Function to check standing thoracic extension form and provide feedback
def check_thoracic_extension_form(keypoints):
    feedback = []
    highlights = []

    try:
        right_hip = np.array(keypoints['right-hip'][0])
        left_hip = np.array(keypoints['left-hip'][0])
        pelvis_center = (right_hip + left_hip) / 2  # Approximate pelvic center
        
        right_shoulder = np.array(keypoints['right-shoulder'][0])
        left_shoulder = np.array(keypoints['left-shoulder'][0])
        upper_back_center = (right_shoulder + left_shoulder) / 2  # Thoracic spine center

        nose = np.array(keypoints['nose'][0])

    except KeyError as e:
        print(f"Missing keypoints: {e}")
        return "Keypoints not detected", []

    # Calculate the angle between the nose, upper back, and pelvis for thoracic extension
    thoracic_extension_angle = calculate_angle(nose, upper_back_center, pelvis_center)

    # Provide feedback based on the thoracic extension angle
    if thoracic_extension_angle < min_extension_angle:
        feedback.append("Extend your upper back more.")
        highlights.append(('right-shoulder', 'left-shoulder'))
    elif thoracic_extension_angle > max_extension_angle:
        feedback.append("Extend less, avoid overextending your lower back.")
        highlights.append(('right-shoulder', 'left-shoulder'))
    else:
        feedback.append("Good thoracic extension, keep the movement controlled.")

    if feedback:
        return " ".join(feedback), highlights
    else:
        return "Good form. Keep it up!", []

# Detect per frame logic for thoracic extension detection
def ThoracicExtensionDetectPerFrame(frame):
    frame = cv2.flip(frame, 1)
    results = model.infer(frame)[0]

    keypoints = {}
    for i in results.predictions:
        for j in i.keypoints:
            keypoints[j.class_name.lower().replace(' ', '-')] = [(int(j.x), int(j.y))]
            cv2.circle(frame, (int(j.x), int(j.y)), radius=10, color=(0, 0, 255), thickness=-1)

    # Validate the keypoints before further processing
    if not keypoints:
        return frame

    # Check thoracic extension form
    try:
        thoracic_extension_feedback, thoracic_extension_highlights = check_thoracic_extension_form(keypoints)

        cv2.putText(frame, thoracic_extension_feedback, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    except Exception as e:
        print(f"Error in form detection: {e}")
        pass

    # Draw skeleton
    annotated_image = sv.EdgeAnnotator(color=sv.Color.GREEN, thickness=5).annotate(frame, sv.KeyPoints.from_inference(results))
    try:
        # Highlight incorrect form in red only for the joints involved in thoracic extension
        for joint_pair in thoracic_extension_highlights:
            for i in range(len(joint_pair) - 1):
                start_point = keypoints[joint_pair[i]][0]
                end_point = keypoints[joint_pair[i+1]][0]
                cv2.line(annotated_image, start_point, end_point, (0, 0, 255), 5)
    except Exception as e:
        print(f"Error in drawing highlights: {e}")

    return cv2.flip(annotated_image, 1)


# Constants for angles
correct_squat_angle_min = 150
correct_squat_angle_max = 180
# Constants for leg raise angles
correct_leg_raise_angle_min = 10  # Minimum angle (a slight lift)
correct_leg_raise_angle_max = 45  # Maximum angle (safe height for elderly)



# Threshold for incorrect movements
max_incorrect_reps = 5
incorrect_movement_count = 0

# Helper function to calculate the angle between three points
def calculate_angle(a, b, c):
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)
    return np.degrees(angle)

# Function to check squat form and provide feedback
def check_squat_form(keypoints):
    global incorrect_movement_count

    feedback = []
    highlights = []

    try:
        right_hip = np.array(keypoints['right-hip'][0])
        right_knee = np.array(keypoints['right-knee'][0])
        right_foot = np.array(keypoints['right-foot'][0])

        left_hip = np.array(keypoints['left-hip'][0])
        left_knee = np.array(keypoints['left-knee'][0])
        left_foot = np.array(keypoints['left-foot'][0])
    except KeyError as e:
        print(f"Missing keypoints: {e}")
        return "Keypoints not detected", []

    # Calculate angles for both legs
    right_leg_angle = calculate_angle(right_hip, right_knee, right_foot)
    left_leg_angle = calculate_angle(left_hip, left_knee, left_foot)

    # Check right leg squat form
    if right_leg_angle < correct_squat_angle_min:
        feedback.append("Raise your body, your right leg is squatting too low.")
        highlights.append(('right-hip', 'right-knee', 'right-foot'))
    elif right_leg_angle > correct_squat_angle_max:
        feedback.append("Lower your body, your right leg is not bent enough.")
        highlights.append(('right-hip', 'right-knee', 'right-foot'))

    # Check left leg squat form
    if left_leg_angle < correct_squat_angle_min:
        feedback.append("Raise your body, your left leg is squatting too low.")
        highlights.append(('left-hip', 'left-knee', 'left-foot'))
    elif left_leg_angle > correct_squat_angle_max:
        feedback.append("Lower your body, your left leg is not bent enough.")
        highlights.append(('left-hip', 'left-knee', 'left-foot'))

    # If feedback exists, increment the incorrect movement counter
    if feedback:
        incorrect_movement_count += 1
        if incorrect_movement_count >= max_incorrect_reps:
            return "Adjust your form. " + " ".join(feedback), highlights
    else:
        incorrect_movement_count = 0
        return "Good form. Keep it up!", []

    return "Continue the exercise", []

# Function to check standing leg raise form and provide feedback
def check_leg_raise_form(keypoints):
    global incorrect_movement_count
    
    feedback = []
    highlights = []

    try:
        right_hip = np.array(keypoints['right-hip'][0])
        right_knee = np.array(keypoints['right-knee'][0])
        right_foot = np.array(keypoints['right-foot'][0])

        left_hip = np.array(keypoints['left-hip'][0])
        left_knee = np.array(keypoints['left-knee'][0])
        left_foot = np.array(keypoints['left-foot'][0])
    except KeyError as e:
        print(f"Missing keypoints: {e}")
        return "Keypoints not detected", []

    # Calculate angles for both legs
    right_leg_angle = calculate_angle(right_hip, right_knee, right_foot)
    left_leg_angle = calculate_angle(left_hip, left_knee, left_foot)

    # Check right leg raise form
    if right_leg_angle < correct_leg_raise_angle_min:
        feedback.append("Lift your right leg a little higher.")
        highlights.append(('right-hip', 'right-knee', 'right-foot'))
    elif right_leg_angle > correct_leg_raise_angle_max:
        feedback.append("Lower your right leg, it's lifted too high.")
        highlights.append(('right-hip', 'right-knee', 'right-foot'))

    # Check left leg raise form
    if left_leg_angle < correct_leg_raise_angle_min:
        feedback.append("Lift your left leg a little higher.")
        highlights.append(('left-hip', 'left-knee', 'left-foot'))
    elif left_leg_angle > correct_leg_raise_angle_max:
        feedback.append("Lower your left leg, it's lifted too high.")
        highlights.append(('left-hip', 'left-knee', 'left-foot'))

    # If feedback exists, increment the incorrect movement counter
    if feedback:
        incorrect_movement_count += 1
        if incorrect_movement_count >= max_incorrect_reps:
            return "Adjust your form. " + " ".join(feedback), highlights
    else:
        incorrect_movement_count = 0
        return "Good form. Keep it up!", []

    return "Continue the exercise", []
# Detect per frame logic for squat detection
def LegRaiseDetectPerFrame(frame):
    global incorrect_movement_count
    frame = cv2.flip(frame, 1)
    results = model.infer(frame)[0]

    keypoints = {}
    for i in results.predictions:
        for j in i.keypoints:
            keypoints[j.class_name.lower().replace(' ', '-')] = [(int(j.x), int(j.y))]
            cv2.circle(frame, (int(j.x), int(j.y)), radius=10, color=(0, 0, 255), thickness=-1)

    # Validate the keypoints before further processing
    if not keypoints:
        return frame

    # Check squat form
    try:
        leg_raise_feedback, leg_raise_highlights = check_leg_raise_form(keypoints)

        cv2.putText(frame, leg_raise_feedback, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    except Exception as e:
        print(f"Error in form detection: {e}")
        pass

    # Draw skeleton
    annotated_image = sv.EdgeAnnotator(color=sv.Color.GREEN, thickness=5).annotate(frame, sv.KeyPoints.from_inference(results))
    '''
    try:
        # Highlight incorrect form in red only for the joints involved in squats
        for joint_pair in squat_highlights:
            for i in range(len(joint_pair) - 1):
                start_point = keypoints[joint_pair[i]][0]
                end_point = keypoints[joint_pair[i+1]][0]
                cv2.line(annotated_image, start_point, end_point, (0, 0, 255), 5)
    except Exception as e:
        print(f"Error in drawing highlights: {e}")
    '''
    try:
        # Highlight incorrect form in red only for the joints involved in leg raises
        for joint_pair in leg_raise_highlights:
            for i in range(len(joint_pair) - 1):
                start_point = keypoints[joint_pair[i]][0]
                end_point = keypoints[joint_pair[i+1]][0]
                cv2.line(annotated_image, start_point, end_point, (0, 0, 255), 5)
    except Exception as e:
        print(f"Error in drawing highlights: {e}")

    return cv2.flip(annotated_image,1)

def SquatDetectPerFrame(frame):
    global incorrect_movement_count
    frame = cv2.flip(frame, 1)
    results = model.infer(frame)[0]

    keypoints = {}
    for i in results.predictions:
        for j in i.keypoints:
            keypoints[j.class_name.lower().replace(' ', '-')] = [(int(j.x), int(j.y))]
            cv2.circle(frame, (int(j.x), int(j.y)), radius=10, color=(0, 0, 255), thickness=-1)

    # Validate the keypoints before further processing
    if not keypoints:
        return frame

    # Check squat form
    try:
        squat_feedback, squat_highlights = check_squat_form(keypoints)
        
        cv2.putText(frame, squat_feedback, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    except Exception as e:
        print(f"Error in form detection: {e}")
        pass

    # Draw skeleton
    annotated_image = sv.EdgeAnnotator(color=sv.Color.GREEN, thickness=5).annotate(frame, sv.KeyPoints.from_inference(results))
    '''
    try:
        # Highlight incorrect form in red only for the joints involved in squats
        for joint_pair in squat_highlights:
            for i in range(len(joint_pair) - 1):
                start_point = keypoints[joint_pair[i]][0]
                end_point = keypoints[joint_pair[i+1]][0]
                cv2.line(annotated_image, start_point, end_point, (0, 0, 255), 5)
    except Exception as e:
        print(f"Error in drawing highlights: {e}")
    '''
    try:
        # Highlight incorrect form in red only for the joints involved in leg raises
        for joint_pair in squat_highlights:
            for i in range(len(joint_pair) - 1):
                start_point = keypoints[joint_pair[i]][0]
                end_point = keypoints[joint_pair[i+1]][0]
                cv2.line(annotated_image, start_point, end_point, (0, 0, 255), 5)
    except Exception as e:
        print(f"Error in drawing highlights: {e}")

    return cv2.flip(annotated_image,1)

# Threshold for back extension
min_extension_angle = 170  # Minimum angle for detecting proper extension (near standing)
max_extension_angle = 190  # Maximum angle to avoid hyperextension

# Helper function to calculate the angle between three points

# Function to check back extension form and provide feedback
def check_back_extension_form(keypoints):
    feedback = []
    highlights = []

    try:
        nose = np.array(keypoints['nose'][0])
        right_hip = np.array(keypoints['right-hip'][0])
        left_hip = np.array(keypoints['left-hip'][0])
        hips = (right_hip + left_hip) / 2  # Averaging the hips to estimate the pelvic center

        right_knee = np.array(keypoints['right-knee'][0])
        left_knee = np.array(keypoints['left-knee'][0])
        knees = (right_knee + left_knee) / 2  # Averaging the knees for better feedback

    except KeyError as e:
        print(f"Missing keypoints: {e}")
        return "Keypoints not detected", []

    # Calculate the angle between the nose, hips, and knees to assess back extension
    back_extension_angle = calculate_angle(nose, hips, knees)

    # Provide feedback based on the back extension angle
    if back_extension_angle < min_extension_angle:
        feedback.append("Extend your back more.")
        highlights.append(('nose', 'right-hip', 'left-hip'))
    elif back_extension_angle > max_extension_angle:
        feedback.append("Reduce your extension, avoid hyperextending.")
        highlights.append(('nose', 'right-hip', 'left-hip'))
    else:
        feedback.append("Good back extension. Keep it gentle and controlled.")

    if feedback:
        return " ".join(feedback), highlights
    else:
        return "Good form. Keep it up!", []

# Detect per frame logic for back extension detection
def BackExtensionDetectPerFrame(frame):
    frame = cv2.flip(frame, 1)
    results = model.infer(frame)[0]

    keypoints = {}
    for i in results.predictions:
        for j in i.keypoints:
            keypoints[j.class_name.lower().replace(' ', '-')] = [(int(j.x), int(j.y))]
            cv2.circle(frame, (int(j.x), int(j.y)), radius=10, color=(0, 0, 255), thickness=-1)

    # Validate the keypoints before further processing
    if not keypoints:
        return frame

    # Check back extension form
    try:
        back_extension_feedback, back_extension_highlights = check_back_extension_form(keypoints)

        cv2.putText(frame, back_extension_feedback, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    except Exception as e:
        print(f"Error in form detection: {e}")
        pass

    # Draw skeleton
    annotated_image = sv.EdgeAnnotator(color=sv.Color.GREEN, thickness=5).annotate(frame, sv.KeyPoints.from_inference(results))
    try:
        # Highlight incorrect form in red only for the joints involved in back extension
        for joint_pair in back_extension_highlights:
            for i in range(len(joint_pair) - 1):
                start_point = keypoints[joint_pair[i]][0]
                end_point = keypoints[joint_pair[i+1]][0]
                cv2.line(annotated_image, start_point, end_point, (0, 0, 255), 5)
    except Exception as e:
        print(f"Error in drawing highlights: {e}")

    return cv2.flip(annotated_image, 1)


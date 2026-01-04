from flask import Flask, render_template, Response, jsonify
import cv2
import time
import numpy as np
import mediapipe as mp
import math
import tensorflow as tf
import os

app = Flask(__name__)

print("Loading AI Model...")
if not os.path.exists('gesture_model.h5'):
    print("ERROR: gesture_model.h5 tidak ada!")
    exit()

model = tf.keras.models.load_model('gesture_model.h5')
CLASSES = {0: "IDLE", 1: "PAUSE", 2: "PLAY", 3: "NEXT", 4: "PREV"}

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(model_complexity=0, max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)

cap = cv2.VideoCapture(0)
 
app_state = {
    "volume": 20,
    "command": "NONE",
    "gesture": "IDLE"
}

def pre_process_landmark(landmark_list):
    temp_landmark_list = []
    base_x, base_y = landmark_list[0].x, landmark_list[0].y
    for lm in landmark_list:
        temp_landmark_list.extend([lm.x - base_x, lm.y - base_y])
    return temp_landmark_list

def get_dist(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def generate_frames():
    volPer = 20
    last_pred_class = 0
    pred_start_time = 0
    CONFIRMATION_TIME = 0.8 

    while True:
        success, frame = cap.read()
        if not success: break

        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)
        
        lmList = []
        ai_input = []
        
        display_status = "IDLE"
        current_command = "NONE"

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                for id, lm in enumerate(hand_landmarks.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])
                ai_input = pre_process_landmark(hand_landmarks.landmark)

        if len(lmList) != 0:
            wrist_y = lmList[0][2]
            if wrist_y < h * 0.15: 
                cv2.putText(frame, "IGNORED (TOO HIGH)", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                ret, buffer = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                continue

            fingers = []
            tipIds = [4, 8, 12, 16, 20]
            
            if lmList[tipIds[0]][0] < lmList[tipIds[0] - 1][0]: fingers.append(1)
            else: fingers.append(0)
            
            for id in range(1, 5):
                if lmList[tipIds[id]][2] < lmList[tipIds[id]-2][2]: fingers.append(1)
                else: fingers.append(0)

            x1, y1 = lmList[4][1], lmList[4][2]
            x2, y2 = lmList[8][1], lmList[8][2]
            length = get_dist((x1,y1), (x2,y2))
            is_pinching = length < 60
            is_pointing = (fingers[1] == 1 and fingers[2] == 0)

            if is_pinching or is_pointing:
                
                pred_start_time = 0 
                
                if length < 30: 
                    targetVol = 0
                    display_status = "MUTE (0%)"
                    cv2.circle(frame, (x1, y1), 15, (0, 0, 255), cv2.FILLED) 
                else:
                    display_status = f"VOL: {int(volPer)}%"
                    targetVol = np.interp(length, [30, 220], [0, 100])
                    
                    cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 255), 3)
                    cv2.circle(frame, (x1, y1), 8, (0, 255, 255), cv2.FILLED)
                    cv2.circle(frame, (x2, y2), 8, (0, 255, 255), cv2.FILLED)
                
                volPer = volPer + (targetVol - volPer) / 4
                app_state["volume"] = int(volPer)

            else:
                if len(ai_input) > 0:
                    prediction = model.predict(np.array([ai_input]), verbose=0)
                    class_id = np.argmax(prediction)
                    prob = np.max(prediction)
                    
                    if class_id != 0 and prob > 0.90:
                        detected = CLASSES[class_id]
                        
                        if (detected == "NEXT" or detected == "PREV") and fingers[1] == 0:
                             detected = "IDLE"

                        if class_id == last_pred_class and detected != "IDLE":
                            elapsed = time.time() - pred_start_time
                            progress = int((elapsed / CONFIRMATION_TIME) * 100)
                            
                            cv2.rectangle(frame, (w-220, 50), (w-20, 70), (50, 50, 50), cv2.FILLED)
                            bar_w = int(2.0 * progress)
                            if bar_w > 200: bar_w = 200
                            cv2.rectangle(frame, (w-220, 50), (w-220 + bar_w, 70), (0, 255, 0), cv2.FILLED)
                            
                            display_status = f"HOLD {detected}"

                            if elapsed > CONFIRMATION_TIME:
                                current_command = detected
                                display_status = f"CMD: {detected}!"
                                print(f"COMMAND: {current_command}")
                                pred_start_time = time.time() + 1.2
                        else:
                            last_pred_class = class_id
                            pred_start_time = time.time()
                    else:
                        pred_start_time = 0
                        
        app_state["gesture"] = display_status
        app_state["command"] = current_command

        color_status = (255, 255, 255)
        if "VOL" in display_status: color_status = (0, 255, 255)
        if "MUTE" in display_status: color_status = (0, 0, 255)
        if "CMD" in display_status: color_status = (0, 255, 0)
        
        cv2.putText(frame, display_status, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color_status, 2)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_state')
def get_state():
    return jsonify(app_state)

if __name__ == "__main__":
    app.run(debug=True, threaded=True, port=5001)
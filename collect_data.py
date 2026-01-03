import cv2
import mediapipe as mp
import numpy as np
import csv
import os

FILE_NAME = 'gesture_data.csv'

CLASSES = {
    0: "IDLE (Diam/Random)",
    1: "PAUSE (Kepal)",
    2: "PLAY (5 Jari)",
    3: "NEXT (V / Angka 2)",
    4: "PREV (Angka 3)"
}

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(model_complexity=1, max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)

cap = cv2.VideoCapture(0)

def init_csv():
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, mode='w', newline='') as f:
            writer = csv.writer(f)
            header = ['label']
            for i in range(21):
                header.extend([f'x{i}', f'y{i}'])
            writer.writerow(header)
            print(f"File {FILE_NAME} berhasil dibuat!")
    else:
        print(f"Menggunakan file {FILE_NAME} yang sudah ada.")

def pre_process_landmark(landmark_list):
    temp_landmark_list = []
    
    base_x, base_y = landmark_list[0].x, landmark_list[0].y

    for lm in landmark_list:
        temp_landmark_list.extend([lm.x - base_x, lm.y - base_y])

    return temp_landmark_list

init_csv()

print("\nINSTRUKSI PEREKAMAN")
print("Tahan tombol angka berikut untuk merekam:")
for k, v in CLASSES.items():
    print(f"  [{k}] : {v}")
print("  [Q] : Keluar Program")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    
    display_text = "READY..."
    color_text = (255, 255, 255) 

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            processed_data = pre_process_landmark(hand_landmarks.landmark)
            
            key = cv2.waitKey(1)
            
            saved_label = -1
            if key == ord('0'): saved_label = 0
            elif key == ord('1'): saved_label = 1
            elif key == ord('2'): saved_label = 2
            elif key == ord('3'): saved_label = 3
            elif key == ord('4'): saved_label = 4
            
            if saved_label != -1:
                with open(FILE_NAME, mode='a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([saved_label] + processed_data)
                
                display_text = f"REKAM: {CLASSES[saved_label]}"
                color_text = (0, 255, 0) 
                print(f"📸 Data tersimpan: {CLASSES[saved_label]}")

            cv2.putText(frame, display_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color_text, 2)

    else:
        cv2.putText(frame, "Tangan Tidak Terlihat", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    h, w, c = frame.shape
    cv2.putText(frame, "0:Idle | 1:Pause | 2:Play | 3:Next | 4:Prev", (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    cv2.imshow('Data Collector', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
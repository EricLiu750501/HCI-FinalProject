import cv2
import mediapipe as mp
import numpy as np
import json
import os

# 初始化MediaPipe Hand
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7,
            min_tracking_confidence=0.7)  # 最多辨識兩隻手
mp_drawing = mp.solutions.drawing_utils

# 開啟攝影機
cap = cv2.VideoCapture(0)

gesture_hand_points = {
            'gid' : 0,
            'g_name' : 'Test',
            'hand_num' : 0,
            'left_d' : [],
            'right_d' : []
        }
def write_json():
    gesture_hand_points['hand_num'] = int(len(gesture_hand_points['left_d']) != 0) + int(len(gesture_hand_points['right_d']) != 0)
    # 定義資料夾
    directory = '../setting/custom_gestures'


    # 確保資料夾存在
    if not os.path.exists(directory):
        os.makedirs(directory)

    # 找出資料夾中已存在的 .json 檔案數量
    json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
    next_file_number = len(json_files) + 1  # 計算下個檔案編號

    # 定義新檔案名稱, set gid
    file_name = f'gesture_hand_points{next_file_number}.json'
    file_path = os.path.join(directory, file_name)
    gesture_hand_points['gid'] = next_file_number 

    # 寫入 JSON 檔案
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(gesture_hand_points, file, ensure_ascii=False, indent=4)

while cap.isOpened():
    # print('frame')
    ret, frame = cap.read()
    if not ret:
        break
    
    # 將影像轉換為RGB格式
    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # 執行手部辨識
    results = hands.process(frame_rgb)
    
    if results.multi_hand_landmarks:
        hand_count = 0
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            # 顯示手部的標誌點
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # 獲得手部的關鍵點坐標
            landmarks = hand_landmarks.landmark
            hand_type = handedness.classification[0].label  # 判斷是左手還是右手
            # print(hand_type)


            array = [ [0.0,0.0,0.0] for i in range(20)]
            for i in range(1, len(landmarks)):
                    array[i-1][0] = landmarks[i-1].x - landmarks[0].x
                    array[i-1][1] = landmarks[i-1].y - landmarks[0].y
                    array[i-1][2] = landmarks[i-1].z - landmarks[0].z
            if hand_type == 'Left':
                print(f'{hand_type}Points')
                # print(landmarks[0].x)
                
                # print(f"X {landmarks[i].x - landmarks[0].x}, {array[i][0]}")
                
                gesture_hand_points['left_d'] = array
                hand_count += 1
                
             
            
                # for idx, landmark in enumerate(landmarks):
                   
            elif hand_type == 'Right':
                gesture_hand_points['right_d'] = array
                hand_count+=1
            # 顯示手部是哪隻手
            # cv2.putText(frame, f'Hand: {hand_type}', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # 顯示每個關鍵點的座標
            # for idx, landmark in enumerate(landmarks):
            #     print(f'{hand_type}Point {idx}: ({landmark.x}, {landmark.y}, {landmark.z})')
            write_json()
        # 顯示影像
        cv2.imshow('Hand Tracking', frame)

    # 按鍵 'q' 退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()




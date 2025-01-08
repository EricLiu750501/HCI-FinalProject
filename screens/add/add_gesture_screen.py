import cv2
import mediapipe as mp
import numpy as np
from screens.base_screen import BaseScreen
from utils.constants import WINDOW_SIZE, FONT
from utils.CvDrawText import CvDrawText
import os
import json
import tkinter as tk


class AddGestureScreen(BaseScreen):
    
    def __init__(self, callback):
        # self.root = tk.Tk()
        # self.root.withdraw()
        # self.root.title("定義招式名稱")
        # self.user_input = tk.StringVar()
        # self.entry = tk.Entry(self.root, textvariable=self.user_input, width=50)
        # self.entry.pack(pady=10)


        super().__init__(callback)
        self.font_path = FONT
        self.colors = {
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "black": (0, 0, 0),
            "white": (255, 255, 255),
        }
        self.debug_mode = False

        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        # init mediaPipe
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,         # 偵測最多 1 張臉
            refine_landmarks=True,   # 啟用高精偵測
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
            )
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,                # 最多偵測2隻手
            min_detection_confidence=0.7,   # 偵測閾值
            min_tracking_confidence=0.7     # 追蹤閾值
        )


        self.FACEPOINTS = mp.solutions.face_mesh_connections
        # https://github.com/google-ai-edge/mediapipe/blob/7c28c5d58ffbcb72043cbe8c9cc32b40aaebac41/mediapipe/python/solutions/face_mesh_connections.py

        self.landmark_sections = [self.FACEPOINTS.FACEMESH_LEFT_EYEBROW,
                            self.FACEPOINTS.FACEMESH_RIGHT_EYEBROW]
        
        self.landmark_colors = [self.colors["red"], self.colors["green"]]


        self.frame_count = 30  # 只保留最近 30 幀(=1sec)的數據 
        self.frame_count_i = 0 
        self.brow_x_positions = [0] * self.frame_count
        self.brow_y_positions = [0] * self.frame_count
        self.nod_frequency_range = (2, 8)  # 點頭頻率範圍（以 Hz 為單位，假設每秒 30 幀）
        self.nod_success = 0 # 偵測成功正在點頭的 frame 數量

        self.cap = cv2.VideoCapture(0)  # Open default camera
        if not self.cap.isOpened():
            print("Cannot open camera, please check the device.")
            self.cap = None

  



    def __drawMarks(self, frame, landmark):
        # 將地標座標轉換為像素位置
        h, w, _ = frame.shape  # 取得影像大小
        x, y = int(landmark.x * w), int(landmark.y * h)
       
        if self.debug_mode: # 在畫面上畫圓標註地標（可不畫）
            cv2.circle(frame, (x, y), 3, self.colors["green"], -1)
        return x, y # return 像素位置




    def draw(self, frame):
        frame.fill(0)
        frame[:] = (50, 50, 50)  # Fill frame with gray

        # 繪製返回按鈕
        back_x, back_y = 950, WINDOW_SIZE[1] - 100
        cv2.rectangle(
            frame, (back_x, back_y), (back_x + 200, back_y + 50), (0, 0, 255), -1
        )
        CvDrawText.puttext(
            frame,
            "返回",
            (back_x + 70, back_y + 10),
            self.font_path,
            30,
            (255, 255, 255),
        )
        self.button_areas.append((back_x, back_y, back_x + 200, back_y + 50))

        # Vertical separator line
        cv2.line(frame, (900, 0), (900, WINDOW_SIZE[1]), (200, 200, 200), 2)

        image = self.__face_tracking()

        image = cv2.resize(image, (640, 480))
        frame[100:100 + 480, 100:100 + 640] = image
            
        return frame
    



    def handle_click(self, x, y):
        for x1, y1, x2, y2 in self.button_areas:
            if x1 <= x <= x2 and y1 <= y <= y2:
                self.cap.release()
                self.cap = None
                self.callback("back")
                break


    def __face_tracking(self):
        if self.cap == None:
            self.cap = cv2.VideoCapture(0)  # Open default camera
            if not self.cap.isOpened():
                print("Cannot open camera, please check the device.")
                self.cap = None
            
        success, frame = self.cap.read()
        
        if success:
            frame = cv2.flip(frame, 1)
            # 轉換 BGR 到 RGB（MediaPipe 需要 RGB 格式）
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # 禁用寫入改善效能
            rgb_frame.flags.writeable = False
            # 偵測臉部特徵
            face_results = self.face_mesh.process(rgb_frame)
            hands_results = self.hands.process(rgb_frame)
            # 恢復為可寫入格式
            rgb_frame.flags.writeable = True
            frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)

            
            # 繪製眉毛 （可不畫），加工數據(mean)
            if face_results.multi_face_landmarks:
                for face_landmarks in face_results.multi_face_landmarks:
                    tmp_set = set()
                    
                    for i in range(len(self.landmark_sections)):
                        for (idx0, idx1) in self.landmark_sections[i]:
                            tmp_set.add(idx0)
                            tmp_set.add(idx1)

                        tmp_lstx = []
                        tmp_lsty = []
                        for ele in tmp_set:
                            x,y = self.__drawMarks(frame, face_landmarks.landmark[ele]) 
                            tmp_lstx.append(x)
                            tmp_lsty.append(y)
                        self.brow_x_positions[self.frame_count_i] = int(sum(tmp_lstx)/len(tmp_lstx))
                        self.brow_y_positions[self.frame_count_i] = int(sum(tmp_lsty)/len(tmp_lsty)) # mean point of brows

            if True:  # 可能會有一些條件
                # Fourier transform time sequence of brow_y_positions
                # find the Dominant frequency whether its amplitude is in our accepted range 
                smoothed_positions = np.convolve(self.brow_y_positions, np.ones(5)/5, mode='valid') # 平滑數據
                fft_signal = np.fft.fft(smoothed_positions)
                amplitude = np.abs(fft_signal)[1:] # 30fps , 忽略 0Hz
                frequencies = np.fft.fftfreq(len(smoothed_positions), 1/30)[1:] # 30fps , 忽略 0Hz
                maximum = 0
                max_ind = 0
                for fft_i in range(len(amplitude)):
                    if maximum < amplitude[fft_i]:
                        maximum = amplitude[fft_i]
                        max_ind = fft_i
                if self.debug_mode:
                    print(frequencies[max_ind])
                if (self.nod_frequency_range[0] <= abs(frequencies[max_ind]) <= self.nod_frequency_range[1]):
                    self.nod_success += 1
                    if self.debug_mode:# for debug
                        cv2.putText(frame, "Nod Detected: Harmonic Motion", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                else:
                    self.nod_success = 0 # 中斷點頭就重新計算
                    if self.debug_mode:# for debug
                        cv2.putText(frame, "No Nod Detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                
                if self.nod_success >= self.frame_count * 0.6: # 點頭持續 0.6秒表示確定
                    self.__record_gesture(hands_results, frame)
                    self.nod_success = 0 # reset
                    self.brow_y_positions = [0] * self.frame_count # reset
                    cv2.putText(frame, "CONFIRM!!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2) 
            
            
            
            self.frame_count_i = (self.frame_count_i + 1 ) % self.frame_count
            # 繪製手 （必要）
            if hands_results.multi_hand_landmarks:
                for hand_landmarks in hands_results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(
                        frame, 
                        hand_landmarks, 
                        self.mp_hands.HAND_CONNECTIONS  # 繪製手部骨架連接
                    )


        
        return frame



    def __record_gesture(self, hands_results, frame):
        print("Recoding ...")
        gesture_hand_points = {
                'g_id' : 13,   # 前12個預設手勢是固定的，從13開始自定義
                "g_name_zh": "無",
                'g_name_en' : 'Unknow',
                # 'hand_num' : 0,
                'left_d' : [],
                'right_d' : []
            }

        if hands_results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(hands_results.multi_hand_landmarks, hands_results.multi_handedness):                            
                # 獲得手部的關鍵點坐標
                landmarks = hand_landmarks.landmark
                hand_type = handedness.classification[0].label  # 判斷是左手還是右手
                
                array = [ [0.0,0.0,0.0] for i in range(20)]
                for i in range(1, len(landmarks)):
                    cur_vector = [landmarks[i].x, landmarks[i].y, landmarks[i].z]
                    base_vector = [landmarks[0].x, landmarks[0].y, landmarks[0].z]
                    array[i-1] = np.linalg.norm(np.array(cur_vector) - np.array(base_vector))
                
                if hand_type == "Left" :
                    gesture_hand_points['left_d'] = array
                    # gesture_hand_points["hand_num"] += 1
                elif hand_type == "Right":
                    gesture_hand_points['right_d'] = array
                    # gesture_hand_points["hand_num"] += 1
        
        # 開啟 Tkinter 視窗，讓使用者輸入招式名稱
        is_add, name_zh, name_en = self.__tk_get_char()

        if not is_add:
            return 0
        
        # 儲存圖片
        # self.have_to_storage_image = True
        self.__image_storage(frame)

        # 儲存 json
        print("招式名稱:", name_zh)
        gesture_hand_points['g_name_zh'] = name_zh
        gesture_hand_points['g_name_en'] = name_en

        # 定義資料夾
        directory = 'setting/'
        file_name = f'created_gestures_d.json'
        file_path = os.path.join(directory, file_name)

        # 確保資料夾存在
        if not os.path.exists(directory):
            os.makedirs(directory)

        if not os.path.exists(file_path):
            print(f"{file_path} 不存在")
            return None
        
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            gesture_hand_points['g_id'] = len(data) + 13
            data.append(gesture_hand_points)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
       
        print("Recoding Done!")

        



    def __tk_get_char(self):
        top = tk.Toplevel()
        top.title("定義招式名稱")
        

        user_input_zh = tk.StringVar()
        user_input_en = tk.StringVar()
        error_message_zh = tk.StringVar()
        error_message_en = tk.StringVar()

        # 定義驗證函數，只允許字母和空格
        def validate_input_en(char):
            
            if char.encode( 'UTF-8' ).isalpha():
                error_message_en.set("")  # 清除錯誤訊息
                return True
            else:
                error_message_en.set("只允許輸入字母")
                return False

        def validate_input_zh(char):
            if '\u4e00' <= char <= '\u9fa5' and len(char) == 1:
                error_message_zh.set("")  # 清除錯誤訊息
                return True
            else:
                error_message_zh.set("只允許輸入一字中文")
                return False

        # 將驗證函數包裝成 Tkinter 可以使用的格式
        validate_command_zh = top.register(validate_input_zh)
        validate_command_en = top.register(validate_input_en)

        # 使用 Frame 來組織 Label 和 Entry
        frame_zh = tk.Frame(top)
        frame_zh.pack(pady=10)

        label_zh = tk.Label(frame_zh, text="請輸入一個字中文：")
        label_zh.pack(side=tk.LEFT)

        error_label_zh = tk.Label(frame_zh, textvariable=error_message_zh, fg="red")
        error_label_zh.pack(side=tk.RIGHT)

        entry_zh = tk.Entry(frame_zh, textvariable=user_input_zh, width=50, validate="key", validatecommand=(validate_command_zh, '%S'))
        entry_zh.pack(side=tk.LEFT)

        # 英文輸入框
        frame_en = tk.Frame(top)
        frame_en.pack(pady=10)

        label_en = tk.Label(frame_en, text="請輸入英文名稱：")
        label_en.pack(side=tk.LEFT)

        entry_en = tk.Entry(frame_en, textvariable=user_input_en, width=50, validate="key", validatecommand=(validate_command_en, '%S'))
        entry_en.pack(side=tk.LEFT)

        error_label_en = tk.Label(frame_en, textvariable=error_message_en, fg="red")
        error_label_en.pack(side=tk.RIGHT)

        is_add = False
        def on_submit():
            nonlocal is_add
            if not user_input_zh.get():
                error_message_zh.set("輸入不得為空")
                return
            elif len(user_input_zh.get()) != 1:
                error_message_zh.set("只允許輸入一字中文")
                return
            if not user_input_en.get():
                error_message_en.set("輸入不得為空")
                return
            is_add = True
            top.quit()  # 結束事件循環

        def on_cancel():
            nonlocal is_add
            is_add = False
            top.quit()
        
        
        submit_button = tk.Button(top, text="Submit", command=on_submit)
        cancel_button = tk.Button(top, text="Cancel Add Gesture", command=on_cancel)
        submit_button.pack(pady=10)
        cancel_button.pack(pady=20)
        top.mainloop()  # 進入事件循環
        top.withdraw()  # 隱藏視窗

        result_zh = user_input_zh.get()
        result_en = user_input_en.get()
        top.destroy()  # 銷毀視窗
        print("User input:", is_add, result_zh, result_en)
        return (is_add, result_zh, result_en)  # 返回是否新增和用戶輸入的招式名稱
  
    def __image_storage(self, frame):
        # 定義資料夾
        directory = 'assets/images/'
        if not os.path.exists(directory):
            print(f"{directory} 不存在")
            return 0

        # 查找所有名為 gesture_* 的檔案
        gesture_files = [f for f in os.listdir(directory) if f.startswith('gesture_')]
        
        file_name = f'gesture_{len(gesture_files) + 1}.jpg'
        file_path = os.path.join(directory, file_name)


        cv2.imwrite(file_path, frame)
        print(f"Image saved to {file_path}")

import cv2
import mediapipe as mp
import numpy as np
from screens.base_screen import BaseScreen
from utils.constants import WINDOW_SIZE, FONT
from utils.CvDrawText import CvDrawText


class AddGestureScreen(BaseScreen):
    
    def __init__(self, callback):
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
            min_detection_confidence=0.5,   # 偵測閾值
            min_tracking_confidence=0.5     # 追蹤閾值
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


        self.gesture_hand_points = {
            'gid' : 0,
            'g_name' : 'Test',
            'hand_num' : 0,
            'left_d' : [],
            'right_d' : []
        }

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
        back_x, back_y = 50, WINDOW_SIZE[1] - 100
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
        cv2.line(frame, (700, 0), (700, WINDOW_SIZE[1]), (200, 200, 200), 2)

        image = self.__face_tracking()

       
            



        image = cv2.resize(image, (640, 480))
        frame[50:530, 50:690] = image
        return frame
    



    def handle_click(self, x, y):
        for x1, y1, x2, y2 in self.button_areas:
            if x1 <= x <= x2 and y1 <= y <= y2:
                self.callback("back")
                break


    def __face_tracking(self):
            
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

            # 繪製手 （必要）
            if hands_results.multi_hand_landmarks:
                for hand_landmarks in hands_results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(
                        frame, 
                        hand_landmarks, 
                        self.mp_hands.HAND_CONNECTIONS  # 繪製手部骨架連接
                    )
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

                
                if self.nod_success >= self.frame_count * 0.7: # 點頭持續 0.7秒表示確定
                    if hands_results.multi_hand_landmarks:
                        for hand_landmarks, handedness in zip(hands_results.multi_hand_landmarks, hands_results.multi_handedness):                            
                            # 獲得手部的關鍵點坐標
                            landmarks = hand_landmarks.landmark
                            hand_type = handedness.classification[0].label  # 判斷是左手還是右手
                            
                            # 顯示手部是哪隻手
                            if self.debug_mode:
                                cv2.putText(frame, f'Hand: {hand_type}', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                            
                            # 顯示每個關鍵點的座標
                            for idx, landmark in enumerate(landmarks):
                                print(f'{hand_type}Point {idx}: ({landmark.x}, {landmark.y}, {landmark.z})')
                    cv2.putText(frame, "CONFIRM!!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2) 
            
            
            
            self.frame_count_i = (self.frame_count_i + 1 ) % self.frame_count


        
        return frame






        # self.button_areas = []
        # # 保存原始圖像的副本
        # temp_frame = frame.copy()
        # temp_frame[:] = (255, 255, 255)  # 白色背景
        # # 添加標題
        # CvDrawText.puttext(
        #     temp_frame, "新增手勢", (100, 100), self.font_path, 48, color=(0, 0, 0)
        # )

        # # 繪製返回按鈕
        # back_x, back_y = 50, WINDOW_SIZE[1] - 100
        # cv2.rectangle(
        #     temp_frame, (back_x, back_y), (back_x + 200, back_y + 50), (0, 0, 255), -1
        # )
        # CvDrawText.puttext(
        #     temp_frame,
        #     "返回",
        #     (back_x + 70, back_y + 10),
        #     self.font_path,
        #     30,
        #     (255, 255, 255),
        # )
        # self.button_areas.append((back_x, back_y, back_x + 200, back_y + 50))

        # # 將處理後的圖像複製回原始 frame
        # frame[:] = temp_frame
        # return frame
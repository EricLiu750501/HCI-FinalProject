import cv2 
import mediapipe as mp
import numpy as np
from scipy.signal import find_peaks


def get_pupil_center(landmarks, indices):
    # 提取地標並計算中心點
    points = np.array([[landmarks[i].x, landmarks[i].y, landmarks[i].z] for i in indices])
    center = np.mean(points, axis=0)
    return center

FACEPOINTS = mp.solutions.face_mesh_connections
# https://github.com/google-ai-edge/mediapipe/blob/7c28c5d58ffbcb72043cbe8c9cc32b40aaebac41/mediapipe/python/solutions/face_mesh_connections.py

landmark_sections = [FACEPOINTS.FACEMESH_LEFT_EYEBROW,
                     FACEPOINTS.FACEMESH_RIGHT_EYEBROW]
colors = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "black": (0, 0, 0),
    "white": (255, 255, 255),
}
landmark_colors = [colors["red"], colors["green"]]

frame_count = 30  # 只保留最近 50 幀的數據
frame_count_i = 0
brow_x_positions = [0] * frame_count
brow_y_positions = [0] * frame_count
nod_frequency_range = (1.5, 3)  # 點頭頻率範圍（以 Hz 為單位，假設每秒 30 幀）



def drawMarks(frame, landmark):
    # 將地標座標轉換為像素位置
    h, w, _ = frame.shape  # 取得影像大小
    x, y = int(landmark.x * w), int(landmark.y * h)
    # 在畫面上畫圓標註地標
    cv2.circle(frame, (x, y), 3, colors["green"], -1)
    return x, y # return 像素位置

 

def track():
    # 初始化 MediaPipe
    frame_count_i = 0 
    mp_face_mesh = mp.solutions.face_mesh
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    # 開啟攝像頭
    cap = cv2.VideoCapture(0)

    # 使用 Face Mesh 模組
    with mp_face_mesh.FaceMesh(
        max_num_faces=1,         # 偵測最多 1 張臉
        refine_landmarks=True,   # 啟用高精偵測
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as face_mesh:
        nod_success = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # 轉換 BGR 到 RGB（MediaPipe 需要 RGB 格式）
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # 禁用寫入改善效能
            rgb_frame.flags.writeable = False
            # 偵測臉部特徵
            results = face_mesh.process(rgb_frame)

            # 恢復為可寫入格式
            rgb_frame.flags.writeable = True
            frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)

            # 繪製臉部網格和虹膜
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    tmp_set = set()
                    
                    for i in range(len(landmark_sections)):
                        for (idx0, idx1) in landmark_sections[i]:
                            tmp_set.add(idx0)
                            tmp_set.add(idx1)

                        tmp_lstx = []
                        tmp_lsty = []
                        for ele in tmp_set:
                            x,y = drawMarks(frame, face_landmarks.landmark[ele]) 
                            tmp_lstx.append(x)
                            tmp_lsty.append(y)
                        brow_x_positions[frame_count_i] = int(sum(tmp_lstx)/len(tmp_lstx))
                        brow_y_positions[frame_count_i] = int(sum(tmp_lsty)/len(tmp_lsty))
            # print(brow_y_positions)

            if True:  # 可能會有一些條件
                # 平滑數據
                smoothed_positions = np.convolve(brow_y_positions, np.ones(5)/5, mode='valid')
                fft_signal = np.fft.fft(smoothed_positions)
                amplitude = np.abs(fft_signal)[1:] # 30fps , 忽略 0Hz
                frequencies = np.fft.fftfreq(len(smoothed_positions), 1/30)[1:] # 30fps , 忽略 0Hz
                maximum = 0
                max_ind = 0
                for fft_i in range(len(amplitude)):
                    if maximum < amplitude[fft_i]:
                        maximum = amplitude[fft_i]
                        max_ind = fft_i
                print(frequencies[max_ind])
                if (nod_frequency_range[0] <= frequencies[max_ind] <= nod_frequency_range[1]):
                    nod_success += 1
                    cv2.putText(frame, "Nod Detected: Harmonic Motion", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                else:
                    nod_success = 0 # 
                    cv2.putText(frame, "No Nod Detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                
                if nod_success >= frame_count * 0.7: # 點頭持續 0.7秒表示確定
                    cv2.putText(frame, "CONFIRM!!", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2) 

              
            frame_count_i = (frame_count_i + 1 ) % frame_count
                          
            # 顯示畫面
            cv2.imshow('MediaPipe Face Tracker', frame)

            # 按 'q' 鍵退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()



if __name__ == "__main__":
    track()



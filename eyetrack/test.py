import cv2
import mediapipe as mp
import numpy as np
from scipy.signal import find_peaks

# 初始化 Face Mesh 模組
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=0.5)

# 初始化攝影機
cap = cv2.VideoCapture(0)

# 存儲眉毛位置的歷史數據

frame_count = 90  # 只保留最近 50 幀的數據
frame_count_i = 0
brow_y_positions = [0] * frame_count
nod_frequency_range = (0.5, 3)  # 點頭頻率範圍（以 Hz 為單位，假設每秒 30 幀）
FACEPOINTS = mp.solutions.face_mesh_connections
landmark_sections = [FACEPOINTS.FACEMESH_LEFT_EYEBROW,
                     FACEPOINTS.FACEMESH_RIGHT_EYEBROW]

print("請正確面對攝影機，按下 'q' 結束")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # BGR 轉 RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 偵測臉部 landmarks
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # 提取左眉毛和右眉毛的中心點 (索引 74 和 304)
            left_brow_y = face_landmarks.landmark[74].y * frame.shape[0]
            right_brow_y = face_landmarks.landmark[304].y * frame.shape[0]

            # 計算平均眉毛高度
            avg_brow_y = (left_brow_y + right_brow_y) / 2

            # 保存到歷史數據中
            # brow_y_positions.append(avg_brow_y)
            # if len(brow_y_positions) > frame_count:
            #     brow_y_positions.pop(0)
            brow_y_positions[frame_count_i] = avg_brow_y
            frame_count_i = (frame_count_i + 1) % frame_count

            # 如果數據足夠，進行簡諧運動分析
            if len(brow_y_positions) == frame_count:
                # 平滑數據
                smoothed_positions = np.convolve(brow_y_positions, np.ones(5)/5, mode='valid')

                # 檢測峰值（上升）和谷值（下降）
                peaks, _ = find_peaks(smoothed_positions)
                troughs, _ = find_peaks(-smoothed_positions)

                # 計算峰谷之間的頻率
                if len(peaks) > 1:
                    peak_intervals = np.diff(peaks)  # 峰之間的間隔
                    avg_interval = np.mean(peak_intervals) / 30  # 假設每秒 30 幀
                    frequency = 1 / avg_interval if avg_interval > 0 else 0

                    # 判斷是否符合簡諧運動
                    if nod_frequency_range[0] <= frequency <= nod_frequency_range[1]:
                        cv2.putText(frame, "Nod Detected: Harmonic Motion", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    else:
                        cv2.putText(frame, "No Nod Detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # 畫出眉毛的位置
            left_brow_x = int(face_landmarks.landmark[74].x * frame.shape[1])
            right_brow_x = int(face_landmarks.landmark[304].x * frame.shape[1])
            cv2.circle(frame, (left_brow_x, int(left_brow_y)), 5, (0, 0, 255), -1)
            cv2.circle(frame, (right_brow_x, int(right_brow_y)), 5, (0, 0, 255), -1)

    # 顯示影像
    cv2.imshow('Nod Detection with Harmonic Motion', frame)

    # 按下 'q' 退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

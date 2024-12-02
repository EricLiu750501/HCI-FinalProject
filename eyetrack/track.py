import cv2 
import mediapipe as mp
import numpy as np

def get_pupil_center(landmarks, indices):
    # 提取地標並計算中心點
    points = np.array([[landmarks[i].x, landmarks[i].y, landmarks[i].z] for i in indices])
    center = np.mean(points, axis=0)
    return center


# Left eye indices list
LEFT_EYE =[ 362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385,384, 398 ]
# Right eye indices list
RIGHT_EYE=[ 33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161 , 246 ]
LEFT_IRIS = [474,475, 476, 477]
RIGHT_IRIS = [469, 470, 471, 472]
landmark_sections = [LEFT_EYE, LEFT_IRIS, RIGHT_EYE, RIGHT_IRIS]
colors = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "black": (0, 0, 0),
    "white": (255, 255, 255),
}
landmark_colors = [colors["red"], colors["green"], colors["red"], colors["green"]]




def track():
    # 初始化 MediaPipe
    mp_face_mesh = mp.solutions.face_mesh
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    # 開啟攝像頭
    cap = cv2.VideoCapture(0)

    # 使用 Face Mesh 模組
    with mp_face_mesh.FaceMesh(
        max_num_faces=1,         # 偵測最多 1 張臉
        refine_landmarks=True,   # 啟用虹膜偵測
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as face_mesh:
        
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
                    for i in range(len(landmark_sections)):

                        for idx in landmark_sections[i]:
                            landmark = face_landmarks.landmark[idx]
                            # 將地標座標轉換為像素位置
                            h, w, _ = frame.shape  # 取得影像大小
                            x, y = int(landmark.x * w), int(landmark.y * h)

                            # 在畫面上畫圓標註地標
                            cv2.circle(frame, (x, y), 3, landmark_colors[i], -1)  # 綠色小圓

                
                    

            # 顯示畫面
            cv2.imshow('MediaPipe Iris Tracker', frame)

            # 按 'q' 鍵退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()



if __name__ == "__main__":
    track()


# 繪製臉部網格
                    # mp_drawing.draw_landmarks(
                    #     frame,
                    #     face_landmarks,
                    #     mp_face_mesh.FACEMESH_TESSELATION,
                    #     landmark_drawing_spec=None,
                    #     connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style())

                    # 繪製眼睛和虹膜
                    # mp_drawing.draw_landmarks(
                    #     frame,
                    #     face_landmarks,
                    #     mp_face_mesh.FACEMESH_IRISES,
                    #     landmark_drawing_spec=None,
                    #         connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_iris_connections_style())
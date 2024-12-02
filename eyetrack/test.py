import cv2
import mediapipe as mp

# 初始化 MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

# 開啟攝像頭
cap = cv2.VideoCapture(0)
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # 翻轉影像並轉換顏色
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 進行人臉檢測
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # 遍歷所有你感興趣的地標索引
            selected_landmarks = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385,384, 398]  # 自行選擇地標索引
            for idx in selected_landmarks:
                landmark = face_landmarks.landmark[idx]
                
                # 將地標座標轉換為像素位置
                h, w, _ = frame.shape  # 取得影像大小
                x, y = int(landmark.x * w), int(landmark.y * h)

                # 在畫面上畫圓標註地標
                cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)  # 綠色小圓

            # 連接虹膜中心到眼角（示例：連接33和468）
            iris_center = face_landmarks.landmark[468]
            inner_corner = face_landmarks.landmark[33]
            x1, y1 = int(inner_corner.x * w), int(inner_corner.y * h)
            x2, y2 = int(iris_center.x * w), int(iris_center.y * h)
            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)  # 藍色線

    # 顯示結果
    cv2.imshow('Landmark Visualization', frame)
    if cv2.waitKey(1) & 0xFF == 27:  # 按下 ESC 鍵退出
        break

cap.release()
cv2.destroyAllWindows()

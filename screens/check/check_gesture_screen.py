import cv2
from screens.base_screen import BaseScreen
from utils.constants import WINDOW_SIZE, FONT
from utils.CvDrawText import CvDrawText


class CheckGestureScreen(BaseScreen):
    def __init__(self, callback):
        super().__init__(callback)
        self.font_path = FONT

    def draw(self, frame):
        self.button_areas = []

        # 保存原始圖像的副本
        temp_frame = frame.copy()
        temp_frame[:] = (255, 255, 255)  # 白色背景

        # 添加標題
        temp_frame = CvDrawText.puttext(
            temp_frame, "檢查手勢", (100, 100), self.font_path, 48, color=(0, 0, 0)
        )

        # 繪製返回按鈕
        back_x, back_y = 50, WINDOW_SIZE[1] - 100
        cv2.rectangle(
            temp_frame, (back_x, back_y), (back_x + 200, back_y + 50), (0, 0, 255), -1
        )
        temp_frame = CvDrawText.puttext(
            temp_frame,
            "返回",
            (back_x + 70, back_y + 10),
            self.font_path,
            30,
            (255, 255, 255),
        )
        self.button_areas.append((back_x, back_y, back_x + 200, back_y + 50))

        # 將處理後的圖像複製回原始 frame
        frame[:] = temp_frame
        return frame

    def handle_click(self, x, y):
        for x1, y1, x2, y2 in self.button_areas:
            if x1 <= x <= x2 and y1 <= y <= y2:
                self.callback("back")
                break

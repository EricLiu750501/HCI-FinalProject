import cv2
from screens.base_screen import BaseScreen
from utils.constants import WINDOW_SIZE
from utils.CvDrawText import CvDrawText


class ShowScreen(BaseScreen):
    def __init__(self, callback):
        super().__init__(callback)
        self.font_path = "assets/fonts/NotoSansTC-VariableFont_wght.ttf"
        self.jutsu_index = None

    def set_jutsu_index(self, index):
        self.jutsu_index = index

    def draw(self, frame):
        self.button_areas = []
        # 保存原始圖像的副本
        temp_frame = frame.copy()
        temp_frame[:] = (50, 50, 50)  # 深灰色背景
        # 添加標題
        CvDrawText.puttext(
            temp_frame,
            f"展示忍術 {self.jutsu_index}",
            (100, 100),
            self.font_path,
            48,
            color=(255, 255, 255),
        )
        # 繪製返回按鈕
        back_x, back_y = 50, WINDOW_SIZE[1] - 100
        cv2.rectangle(
            temp_frame, (back_x, back_y), (back_x + 200, back_y + 50), (0, 0, 255), -1
        )
        CvDrawText.puttext(
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
# HCI-FinalProject

## 專案結構
```
project/
├── main.py              # 主程式入口
├── assets/             # 資源檔案
│   ├── images/        # 圖片資源
│   ├── icons/         # 圖示資源
│   └── sounds/        # 音效資源
├── screens/           # 畫面模組
│   ├── __init__.py
│   ├── base_screen.py   # 基礎畫面類別
│   ├── home_screen.py   # 主畫面實作
│   └── mode_screen.py   # 模式畫面實作
└── utils/             # 工具模組
    ├── __init__.py
    ├── constants.py     # 常數定義
    └── drawing.py       # 繪圖工具函數
```

## 環境需求
- Python 3.7+
- OpenCV-Python
- Pygame
- NumPy

```bash
pip install opencv-python pygame numpy
```

## 如何新增畫面

1. 在 `screens` 資料夾中建立新的畫面檔案（例如：`new_screen.py`）：
```python
from .base_screen import BaseScreen

class NewScreen(BaseScreen):
    def __init__(self, callback):
        super().__init__(callback)
        # 初始化您的畫面變數
        
    def draw(self, frame):
        """繪製畫面內容"""
        # 實作繪製邏輯
        
    def handle_click(self, x, y):
        """處理滑鼠點擊"""
        # 實作點擊處理邏輯
        # 使用 self.callback 來觸發畫面切換
        # 例如：self.callback("back") 返回上一個畫面
```

2. 在 `main.py` 的 `GameManager` 類別中新增畫面：
```python
def __init__(self):
    # ... 其他初始化程式碼 ...
    self.new_screen = NewScreen(self._handle_button_click)

def _handle_button_click(self, action, data=None):
    # ... 其他處理程式碼 ...
    elif action == "new_screen":
        self.current_screen = self.new_screen
```

## 共用元件使用說明

### 按鈕繪製
```python
from utils.drawing import draw_button

# 繪製按鈕
draw_button(frame,            # 目標畫面
           "按鈕文字",        # 按鈕文字
           "icons/icon.png",  # 圖示路徑
           (x, y),           # 位置
           (width, height),  # 尺寸
           selected=False,   # 是否被選中
           hover=False)      # 是否懸停
```

### 圓角矩形繪製
```python
from utils.drawing import draw_rounded_rectangle

draw_rounded_rectangle(frame,        # 目標畫面
                      (x1, y1),     # 左上角座標
                      (x2, y2),     # 右下角座標
                      (255,0,0),    # 顏色 (BGR)
                      radius=15,     # 圓角半徑
                      thickness=-1)  # 線條粗細，-1為填滿
```

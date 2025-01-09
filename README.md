# HCI-FinalProject

## 專案結構
```
project/
├── README.md                          # 專案說明文件
├── assets                             # 資源文件夾
│   ├── fonts                          # 字體文件夾
│   ├── gesture_data.json              # 手勢數據文件
│   ├── icons                          # 圖標文件夾
│   ├── images                         # 圖片文件夾
│   │   └── temp_naruto_gestures       # 暫存手勢圖片文件夾
│   │       └── readme.md              # 暫存手勢圖片說明文件
│   ├── sounds                         # 聲音文件夾
│   └── video                          # 影片文件夾
├── main.py                            # 主程式入口
├── model                              # 模型文件夾
│   └── yolox                          # YOLOX 模型文件夾
│       ├── yolox_nano.onnx            # YOLOX Nano 模型文件
│       ├── yolox_nano_with_post.onnx  # YOLOX Nano 模型文件（帶後處理）
│       ├── yolox_onnx.py              # YOLOX ONNX 模型處理腳本
│       └── yolox_onnx_without_post.py  # YOLOX ONNX 模型處理腳本（無後處理）
├── schema                             # 模式文件夾
│   └── json_files                     # JSON 文件夾
│       ├── created_gestures_d.example.json  # 範例手勢數據文件
│       └── user_jutsu.example.json    # 範例忍術數據文件
├── screens                            # 畫面文件夾
│   ├── add                            # 添加畫面文件夾
│   │   └── add_gesture_screen.py      # 添加手勢畫面腳本
│   ├── base_screen.py                 # 基礎畫面腳本
│   ├── check                          # 檢查畫面文件夾
│   │   ├── check_gesture_screen.py    # 檢查手勢畫面腳本
│   │   └── perform_jutsu_screen.py    # 執行忍術畫面腳本
│   ├── edit                           # 編輯畫面文件夾
│   │   └── edit_screen.py             # 編輯畫面腳本
│   ├── gesture_model_screen.py        # 手勢模型畫面腳本
│   ├── gesture_screen.py              # 手勢畫面腳本
│   ├── home_screen.py                 # 主畫面腳本
│   ├── input_box_screen.py            # 輸入框畫面腳本
│   ├── practice                       # 練習畫面文件夾
│   │   └── practice_screen.py         # 練習畫面腳本
│   ├── remove                         # 移除畫面文件夾
│   │   └── remove_file.py             # 移除文件畫面腳本
│   └── show                           # 顯示畫面文件夾
│       └── show_screen.py             # 顯示畫面腳本
├── setting                            # 設定文件夾
│   ├── created_gestures_d.json        # 已創建手勢數據文件
│   ├── default_jutsu.json             # 預設忍術數據文件
│   ├── jutsu.csv                      # 忍術數據文件
│   ├── labels.csv                     # 標籤數據文件
│   ├── tolerance_terms.json           # 容忍術語數據文件
│   └── user_jutsu.json                # 用戶忍術數據文件
└── utils                              # 工具文件夾
    ├── CvDrawText.py                  # OpenCV 繪製文字工具腳本
    ├── constants.py                   # 常量定義腳本
    ├── drawing.py                     # 繪圖工具腳本
    └── rm_files.py                    # 刪除文件工具腳本

```

## 環境需求
- Python 3.9+
- opencv-python: 4.10.0.84
- numpy: 1.26.4
- mediapipe: 0.10.18
- pygame: 2.6.1
- Pillow: 11.0.0
- onnxruntime: 1.20.1
- speechrecognition: 3.12.0
- tkinter: 0.1.0

```bash
pip install -r requirements.txt
```

## 使用說明
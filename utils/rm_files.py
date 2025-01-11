import os
import json

import tkinter as tk
from tkinter import messagebox

def reset_created_gestures():
    file_path = 'setting/created_gestures_d.json'
    with open(file_path, 'w') as file:
        json.dump([], file)
    print(f'Reset {file_path} to an empty list.')


def reset_created_jutsu():
    file_path = 'setting/user_jutsu.json'
    with open(file_path, 'w') as file:
        json.dump([], file)
    print(f'Reset {file_path} to an empty list.')


def remove_temp_naruto_gestures():
    folder_path = 'assets/images/temp_naruto_gestures/'
    for filename in os.listdir(folder_path):
        if filename.endswith(".md"):
            continue
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f'Removed file: {file_path}')
    print(f'All files in {folder_path} have been removed.')


def remove_gesture_files():
    folder_path = 'assets/images/'
    for filename in os.listdir(folder_path):
        if filename.startswith('gesture_'):
                gesture_number = int(filename.split('_')[1] [:-4]) # .jpg suffix
                if gesture_number > 12:
                    file_path = os.path.join(folder_path, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f'Removed file: {file_path}')
            # except ValueError:
            #     continue
    print('Removed all gesture_* files with number greater than 12.')


# Example usage

def remove_all_dev():
    reset_created_gestures()
    reset_created_jutsu()
    remove_temp_naruto_gestures()
    remove_gesture_files()

# def remove_gestures():
#     remove_gesture_files()
#     reset_created_gestures()
#     reset_created_jutsu()

# def remove_jutsu():
#     reset_created_jutsu()

# def remove_temp(): # 移除偷截圖的暫存檔
#     remove_temp_naruto_gestures()

def confirm_and_execute(action):
    top = tk.Toplevel()
    top.withdraw()  # 隱藏主視窗

    if messagebox.askyesno("確認", "您確定要執行此操作嗎？"):
        action()
    else:
        print("操作已取消")

    top.destroy()

def remove_gestures():
    confirm_and_execute(lambda: (remove_gesture_files(), reset_created_gestures(), reset_created_jutsu()))

def remove_jutsu():
    confirm_and_execute(reset_created_jutsu)

def remove_temp():  # 移除偷截圖的暫存檔
    confirm_and_execute(remove_temp_naruto_gestures)

def remove_all():
    confirm_and_execute(remove_all_dev)

# Run for just testing
if __name__ == '__main__':
    # remove_all_dev()
    pass



# 移除序列手勢 setting/user_jutsu.json
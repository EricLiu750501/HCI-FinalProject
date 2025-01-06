import os
import json

def reset_created_gestures():
    file_path = 'setting/created_gestures_d.json'
    with open(file_path, 'w') as file:
        json.dump([], file)
    print(f'Reset {file_path} to an empty list.')
    reset_created_jutsu() # 重置手勢時，也重置忍術


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
                print(filename)
                gesture_number = int(filename.split('_')[1] [:-4]) # .jpg suffix
                print(gesture_number)
                if gesture_number > 12:
                    file_path = os.path.join(folder_path, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        print(f'Removed file: {file_path}')
            # except ValueError:
            #     continue
    print('Removed all gesture_* files with number greater than 12.')


# Example usage

def remove_all():
    reset_created_gestures()
    reset_created_jutsu()
    remove_temp_naruto_gestures()
    remove_gesture_files()

# Run for just testing
if __name__ == '__main__':
    # remove_all()
    pass



# 移除序列手勢 setting/user_jutsu.json
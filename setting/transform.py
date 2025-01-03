import json
import csv


# 讀取 label.csv 生成手勢名稱到 ID 的對應關係
def load_labels(label_file):
    gesture_map = {}
    with open(label_file, "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for i, row in enumerate(reader):
            if i == 0:
                continue  # 跳過標題行
            if len(row) >= 2:
                gesture_map[row[0]] = i  # 用序號作為 ID
    print(gesture_map)
    return gesture_map


# 將 sequence 手勢名稱轉換為 ID
def convert_sequence_to_ids(data, gesture_map):
    for jutsu in data:
        jutsu["sequence"] = [gesture_map[gesture] for gesture in jutsu["sequence"]]
    return data


# 主程式
label_file = "./setting/labels.csv"
json_file = "./setting/default_jutsu.json"
output_file = "converted_jutsu.json"

# 載入資料
gesture_map = load_labels(label_file)

with open(json_file, "r", encoding="utf-8") as file:
    jutsu_data = json.load(file)

# 轉換 sequence
converted_data = convert_sequence_to_ids(jutsu_data, gesture_map)

# 保存轉換後的資料
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(converted_data, file, ensure_ascii=False, indent=4)

print(f"已完成轉換，輸出到 {output_file}")

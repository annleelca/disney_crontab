import requests as req
import json
import pandas as pd
from fake_useragent import UserAgent
import random
import os

# 隨機取得 User-Agent
ua = UserAgent()

# edge
my_headers = {
    'User-Agent': ua.random,
        'Accept-Language': 'ja-JP,ja;q=0.9,en;q=0.8',
        'Referer': 'https://www.tokyodisneyresort.jp/'
}

url = "https://www.tokyodisneyresort.jp/_/realtime/tdl_attraction.json?1714465511332"

res = req.get(url, headers=my_headers)

        
# 如果請求成功
if res.status_code == 200:
    # 將 JSON 解析為 Python 字典
    new_data = res.json()

    # 讀取現有的 JSON 文件
    file_path = "/Users/chianlee/Desktop/disney/data/land_data.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
                    existing_data = json.load(f)
    else:
        existing_data = []
# 合併新舊資料並去重複
combined_data = existing_data.copy()
for item in new_data:
    exists = False
    for existing_item in existing_data:
        if existing_item['FacilityID'] == item['FacilityID'] and existing_item['UpdateTime'] == item['UpdateTime']:exists = True
        break
                
    if not exists:
        combined_data.append({
            'StandbyTime': item['StandbyTime'],
            'FacilityID': item['FacilityID'],
            'UpdateTime': item['UpdateTime'],
            'datetime': pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
            })

# 寫入 JSON 文件
with open(file_path, "w") as f:
    json.dump(combined_data, f, indent=4) 
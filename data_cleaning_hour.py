# 導入必要的庫
import pandas as pd
import json
from datetime import timedelta

# 讀取 JSON 檔案
file_path = '/Users/chianlee/Desktop/disney/data/testing_data_sea.json'
file_path_names = '/Users/chianlee/Desktop/disney/data/sea_namelist.json'

with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

with open(file_path_names, 'r', encoding='utf-8') as file:
    names = json.load(file)

# 轉換為 DataFrame
df_data = pd.DataFrame(data)
df_names = pd.DataFrame(names)

# 刪除 'FacilityName' 欄位並移除 'StandbyTime' 為 null 的行
df_data = df_data.drop(columns=['FacilityName'])
df_data = df_data[df_data['StandbyTime'].notna()]
df_data = df_data[df_data['StandbyTime'] != False]

# 解析日期時間欄位
df_data['UpdateTime'] = pd.to_datetime(df_data['UpdateTime'], format='%H:%M')
df_data['datetime'] = pd.to_datetime(df_data['datetime'])

# 將所有 datetime 欄位加上一小時
df_data['datetime'] = df_data['datetime'] + pd.Timedelta(hours=1)

# 提取日期並應用於 UpdateTime
df_data['UpdateTime'] = df_data.apply(
    lambda row: row['UpdateTime'].replace(year=row['datetime'].year, month=row['datetime'].month, day=row['datetime'].day),
    axis=1
)

# 計算 UpdateTime 和 datetime 之間的時間差（以小時為單位）
df_data['time_difference'] = (df_data['datetime'] - df_data['UpdateTime'])

# 刪除時間差超過2小時的資料
df_filtered = df_data[df_data['time_difference'] <= timedelta(hours=2)]

# 刪除多餘的時間差欄位
df_filtered = df_filtered.drop(columns=['time_difference'])

# 將 StandbyTime 轉換為數值型
df_filtered['StandbyTime'] = pd.to_numeric(df_filtered['StandbyTime'], errors='coerce')

# 提取設施名稱和小時
df_filtered['Hour'] = df_filtered['datetime'].dt.hour

# 篩選 8 點到 20 點之間的數據
df_filtered = df_filtered[(df_filtered['Hour'] >= 8) & (df_filtered['Hour'] <= 20)]

# 合併數據框以添加英文設施名稱
df_filtered = df_filtered.merge(df_names[['FacilityID', 'FacilityEnglish']], on='FacilityID', how='left')

# 確保每個設施在 8 點到 20 點都有數據
all_hours = pd.DataFrame({'Hour': range(8, 21)})
all_facilities = df_filtered['FacilityEnglish'].unique()

full_df = pd.DataFrame()
for facility in all_facilities:
    facility_data = pd.merge(all_hours, df_filtered[df_filtered['FacilityEnglish'] == facility], on='Hour', how='left')
    facility_data['FacilityEnglish'] = facility
    
    # 對該設施的 StandbyTime 進行線性插值和前後填充
    facility_data['StandbyTime'] = facility_data['StandbyTime'].interpolate(method='linear').ffill().bfill()
    full_df = pd.concat([full_df, facility_data], ignore_index=True)

# 計算每個設施每個小時的平均等待時間
average_wait_times_per_hour = full_df.groupby(['FacilityEnglish', 'Hour'])['StandbyTime'].mean().reset_index()

# 保存為 CSV 格式
output_csv_path = '/Users/chianlee/Desktop/disney/data/hour_avg_data.csv'
average_wait_times_per_hour.to_csv(output_csv_path, index=False, encoding='utf-8-sig')

# 將結果存成 JSON 格式
output_file_path = '/Users/chianlee/Desktop/disney/data/hour_avg_data.json'

# 轉換 DataFrame 為 JSON
average_wait_times_per_hour.to_json(output_file_path, orient='records', lines=True, force_ascii=False)

# 計算每個設施在 8 點到 20 點之間的平均等待時間
average_wait_times = full_df.groupby('FacilityEnglish')['StandbyTime'].mean().reset_index()
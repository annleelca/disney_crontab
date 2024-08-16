# 導入必要的庫
import pandas as pd
import json
from datetime import timedelta

# 讀取 JSON 檔案

# 設定資料類型為 'land' 或 'sea'
data_region = 'sea'  

# 根據資料類型設定檔案路徑
file_path = f'/Users/chianlee/Desktop/disney/data/{data_region}_data.json'
file_path_names = f'/Users/chianlee/Desktop/disney/data/{data_region}_namelist.json'


with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

with open(file_path_names, 'r', encoding='utf-8') as file:
    names = json.load(file)

# 轉換為 DataFrame
df_data = pd.DataFrame(data)
df_names = pd.DataFrame(names)

# 刪除 'FacilityName' 欄位並移除 'StandbyTime' 為 null, false 的行
df_data = df_data.drop(columns=['FacilityName'])
df_data = df_data[df_data['StandbyTime'].notna()]
df_data = df_data.dropna()  # 移除包含 NaN 的行
df_data = df_data[df_data['StandbyTime'] != False]

# 解析日期時間欄位
df_data['UpdateTime'] = pd.to_datetime(df_data['UpdateTime'], format='%H:%M')
df_data['datetime'] = pd.to_datetime(df_data['datetime'])

# # 將所有 datetime 欄位加上一小時
# df_data['datetime'] = df_data['datetime'] + pd.Timedelta(hours=1)

# 根據日期條件來調整 datetime 欄位(考量時差)
df_data['datetime'] = df_data['datetime'].apply(
    lambda dt: dt + pd.Timedelta(hours=1) if dt.date() < pd.Timestamp('2023-08-16').date() else dt + pd.Timedelta(hours=2)
)

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

# 提取設施名稱、日期和小時
df_filtered['Hour'] = df_filtered['datetime'].dt.hour
df_filtered['Date'] = df_filtered['datetime'].dt.date

# 篩選 8 點到 20 點之間的數據
df_filtered = df_filtered[(df_filtered['Hour'] >= 8) & (df_filtered['Hour'] <= 20)]

# 合併數據框以添加英文設施名稱
df_filtered = df_filtered.merge(df_names[['FacilityID', 'FacilityEnglish']], on='FacilityID', how='left')

# 確保每個設施在每個日期的 8 點到 20 點都有數據
all_hours = pd.DataFrame({'Hour': range(8, 21)})
all_dates = df_filtered['Date'].unique()
all_facilities = df_filtered['FacilityEnglish'].unique()

full_df = pd.DataFrame()
for date in all_dates:
    for facility in all_facilities:
        facility_data = pd.merge(all_hours, df_filtered[(df_filtered['FacilityEnglish'] == facility) & (df_filtered['Date'] == date)], on='Hour', how='left')
        facility_data['FacilityEnglish'] = facility
        facility_data['Date'] = date
        
        # 對該設施在該日期的 StandbyTime 進行線性插值和前後填充
        facility_data['StandbyTime'] = facility_data['StandbyTime'].interpolate(method='linear').ffill().bfill()
        full_df = pd.concat([full_df, facility_data], ignore_index=True)

# 計算每個設施每個日期每個小時的平均等待時間
average_wait_times_per_day_hour = full_df.groupby(['FacilityEnglish', 'Date', 'Hour'])['StandbyTime'].mean().reset_index()


# 根據資料區域設定輸出檔案路徑
output_file_path = f'/Users/chianlee/Desktop/disney/data/day_hour_avg_data_{data_region}.json'

# 將結果存成 JSON 格式
average_wait_times_per_day_hour.to_json(output_file_path, orient='records', lines=True, force_ascii=False)
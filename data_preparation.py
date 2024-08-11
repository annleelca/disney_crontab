import pandas as pd
import numpy as np
import json
from datetime import datetime

def read_and_prepare_data(wait_times_path, visitor_predictions_path, maintenance_data_path):
    # 讀取等候時間數據
    with open(wait_times_path) as f:
        wait_times = pd.read_json(f, lines=True)

    # 讀取遊客量預測數據
    with open(visitor_predictions_path) as f:
        visitor_predictions = pd.read_json(f)

    # 讀取維修設施數據
    with open(maintenance_data_path) as f:
        maintenance_data = json.load(f)

    # 將維修數據轉換為 DataFrame
    maintenance_df = pd.DataFrame(maintenance_data)
    maintenance_df['Date'] = pd.to_datetime(maintenance_df['Date']).dt.normalize()

    # 擴展維修數據
    expanded_maintenance = []
    for _, row in maintenance_df.iterrows():
        for facility in row['Not_open_facility']:
            expanded_maintenance.append({
                'Date': row['Date'],
                'FacilityEnglish': facility,
                'IsUnderMaintenance': 1
            })

    expanded_maintenance_df = pd.DataFrame(expanded_maintenance)

    # 時間格式處理
    wait_times['Date'] = pd.to_datetime(wait_times['Date'], unit='ms')
    wait_times['Day'] = wait_times['Date'].dt.normalize()
    visitor_predictions['date'] = pd.to_datetime(visitor_predictions['date']).dt.normalize()

    # 篩選與合併數據
    min_date = wait_times['Day'].min()
    max_date = wait_times['Day'].max()
    filtered_visitor_predictions = visitor_predictions[(visitor_predictions['date'] >= min_date) & (visitor_predictions['date'] <= max_date)]

    expanded_predictions = []
    for _, row in filtered_visitor_predictions.iterrows():
        for hour in range(8, 22):
            expanded_predictions.append({
                'region': row['region'],
                'date': row['date'],
                'weekday': row['weekday'],
                'prediction': row['prediction'],
                'Hour': hour
            })

    expanded_predictions = pd.DataFrame(expanded_predictions)
    data = wait_times.merge(expanded_predictions, left_on=['Day', 'Hour'], right_on=['date', 'Hour'], how='left')
    data = data.dropna(subset=['StandbyTime'])
    data = data.merge(expanded_maintenance_df, left_on=['Day', 'FacilityEnglish'], right_on=['Date', 'FacilityEnglish'], how='left')
    data['IsUnderMaintenance'] = data['IsUnderMaintenance'].fillna(0)

    return data, visitor_predictions, expanded_maintenance_df

def assign_time_window(hour):
    if 8 <= hour < 12:
        return 'Morning'
    elif 12 <= hour < 18:
        return 'Afternoon'
    elif 18 <= hour < 22:
        return 'Evening'
    else:
        return 'Unknown'


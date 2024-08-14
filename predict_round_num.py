import pandas as pd
import numpy as np
import joblib
import json
from collections import defaultdict
from data_preparation import read_and_prepare_data
from model_training import feature_engineering

# 定義 weekday_map 和 weekday_to_num 用於特徵工程
weekday_map = {
    'Monday': 1, 'Tuesday': 1, 'Wednesday': 1, 'Thursday': 1, 'Friday': 1, 
    'Saturday': 0, 'Sunday': 0
}
weekday_to_num = {
    'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 
    'Saturday': 5, 'Sunday': 6
}

def load_facility_name_mapping(data_region):
    with open(f'data/{data_region}_namelist.json', 'r') as f:
        name_list = json.load(f)
    facility_name_mapping = {item['FacilityEnglish']: item for item in name_list}
    return facility_name_mapping

def round_to_nearest_five(x):
    """將數值四捨五入到最接近的5的倍數"""
    return int(round(x / 5) * 5)

def predict_future_wait_times(date, visitor_predictions, data, maintenance_df, model, facility_mapping, facility_name_mapping):
    date = pd.to_datetime(date).normalize()
    visitor_prediction = visitor_predictions[visitor_predictions['date'] == date]
    
    if visitor_prediction.empty:
        print(f"No visitor prediction found for date: {date}")
        return {}

    prediction_value = visitor_prediction['prediction'].values[0]
    is_weekend = visitor_prediction['weekday'].map(weekday_map).values[0]
    day_of_week = visitor_prediction['weekday'].map(weekday_to_num).values[0]

    future_data = {}
    time_slot_recommendations = defaultdict(list)
    detailed_times_data = {}

    for facility in data['FacilityCode'].unique():
        # 排除維修中的設施
        is_under_maintenance = maintenance_df[
            (maintenance_df['Date'] == date) &
            (maintenance_df['FacilityEnglish'] == facility_mapping[facility])
        ]['IsUnderMaintenance'].any()

        if is_under_maintenance:
            continue  # 跳過維修中的設施

        predicted_times = {}

        for hour in range(8, 20):
            predicted_wait_time = int(np.round(np.maximum(
                model.predict(pd.DataFrame([{
                    'Hour': hour,
                    'prediction': prediction_value,
                    'IsWeekend': is_weekend,
                    'DayOfWeek': day_of_week,
                    'FacilityCode': facility,
                    'TimeWindow': 0 if hour < 12 else (1 if hour < 18 else 2),
                    'IsUnderMaintenance': 0  # 保留特徵，但設定為0表示未維修
                }])), 0)).astype(int)[0])

            # 使用 round_to_nearest_five 函數將預測等待時間四捨五入到5的倍數
            rounded_wait_time = round_to_nearest_five(predicted_wait_time)

            predicted_times[f"{hour}:00"] = rounded_wait_time

        sorted_times = sorted(predicted_times.items(), key=lambda x: x[1])[:62]

        facility_info = facility_name_mapping.get(facility_mapping[facility], {})
        facility_key = facility_info.get('FacilityMandarin', '未知設施')
        future_data[facility_key] = sorted_times
        detailed_times_data[facility_key] = predicted_times

        for hour_str, wait_time in sorted_times:
            hour = int(hour_str.split(":")[0])
            time_slot_recommendations[hour].append({
                facility_key: f"wait {wait_time} min"
            })

    sorted_time_slot_recommendations = dict(sorted(time_slot_recommendations.items()))

    return future_data, sorted_time_slot_recommendations, detailed_times_data

def generate_future_land(date, data_region):
    model = joblib.load(f'models/wait_time_model_{data_region}.pkl')
    facility_mapping = joblib.load(f'models/facility_mapping_{data_region}.pkl')
    facility_name_mapping = load_facility_name_mapping(data_region)

    data, visitor_predictions, maintenance_df = read_and_prepare_data(
        f'data/day_hour_avg_data_{data_region}.json',
        f'data/disney{data_region}_predict.json',
        f'data/maintenance_{data_region}.json'
    )
    data, _ = feature_engineering(data)
    
    future_data, sorted_time_slot_recommendations, detailed_times_data = predict_future_wait_times(date, visitor_predictions, data, maintenance_df, model, facility_mapping, facility_name_mapping)

    return future_data, sorted_time_slot_recommendations, detailed_times_data

def save_recommendations(future_data, sorted_time_slot_recommendations, detailed_times_data, date, data_region):
    output_file = f'data/predict/recom_{data_region}_{date}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(future_data, f, indent=4, ensure_ascii=False)

    output_file_by_time = f'data/predict/recom_{data_region}_{date}_by_time.json'
    with open(output_file_by_time, 'w', encoding='utf-8') as f:
        json.dump(sorted_time_slot_recommendations, f, indent=4, ensure_ascii=False)

    output_file_detailed = f'data/predict/detailed_{data_region}_{date}.json'
    with open(output_file_detailed, 'w', encoding='utf-8') as f:
        json.dump(detailed_times_data, f, indent=4, ensure_ascii=False)

def predict_and_save_recommendations(date, data_region):
    future_data, sorted_time_slot_recommendations, detailed_times_data = generate_future_land(date, data_region)
    save_recommendations(future_data, sorted_time_slot_recommendations, detailed_times_data, date, data_region)

def predict_and_return_recommendations(date, data_region):
    future_data, _, detailed_times_data = generate_future_land(date, data_region)
    
    time_slots = {
        "morning": range(8, 11),
        "noon": range(11, 14),
        "afternoon": range(14, 17),
        "evening": range(17, 20)
    }
    
    recommendations = {}
    
    for facility, times in detailed_times_data.items():
        slot_predictions = {}
        for slot, hours in time_slots.items():
            wait_times = [times[f"{hour}:00"] for hour in hours if f"{hour}:00" in times]
            if wait_times:
                average_wait_time = round_to_nearest_five(np.mean(wait_times)+20)
            else:
                average_wait_time = None
            slot_predictions[slot] = average_wait_time
        
        recommendations[facility] = slot_predictions
    print(recommendations)
    return recommendations

if __name__ == "__main__":
    date = input("請輸入要預測的日期 (格式：YYYY-MM-DD)：")
    data_region = input("請輸入資料區域 (Land 或 Sea)：").strip().lower()
    results = predict_and_return_recommendations(date, data_region)
    print(results)

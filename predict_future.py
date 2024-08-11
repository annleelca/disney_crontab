# import pandas as pd
# import numpy as np
# import joblib
# import os
# import json
# from data_preparation import read_and_prepare_data, assign_time_window
# from model_training import feature_engineering

# # 定義 weekday_map 和 weekday_to_num 用於特徵工程
# weekday_map = {
#     'Monday': 1, 'Tuesday': 1, 'Wednesday': 1, 'Thursday': 1, 'Friday': 1, 
#     'Saturday': 0, 'Sunday': 0
# }
# weekday_to_num = {
#     'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 
#     'Saturday': 5, 'Sunday': 6
# }

# def predict_future_wait_times(date_str, visitor_predictions, data, maintenance_df, model, facility_mapping):
#     date = pd.to_datetime(date_str).normalize()
#     visitor_prediction = visitor_predictions[visitor_predictions['date'] == date]
    
#     if visitor_prediction.empty:
#         print(f"No visitor prediction found for date: {date_str}")
#         return {}

#     prediction_value = visitor_prediction['prediction'].values[0]
#     is_weekend = visitor_prediction['weekday'].map(weekday_map).values[0]
#     day_of_week = visitor_prediction['weekday'].map(weekday_to_num).values[0]

#     future_data = {}
#     for facility in data['FacilityCode'].unique():
#         # 排除維修中的設施
#         is_under_maintenance = maintenance_df[
#             (maintenance_df['Date'] == date) &
#             (maintenance_df['FacilityEnglish'] == facility_mapping[facility])
#         ]['IsUnderMaintenance'].any()

#         if is_under_maintenance:
#             continue  # 跳過維修中的設施

#         predicted_times = []
#         for hour in range(8, 22):
#             predicted_wait_time = int(np.round(np.maximum(
#                 model.predict(pd.DataFrame([{
#                     'Hour': hour,
#                     'prediction': prediction_value,
#                     'IsWeekend': is_weekend,
#                     'DayOfWeek': day_of_week,
#                     'FacilityCode': facility,
#                     'TimeWindow': 0 if hour < 12 else (1 if hour < 18 else 2),
#                     'IsUnderMaintenance': 0  # 保留特徵，但設定為0表示未維修
#                 }])), 0)).astype(int)[0])

#             predicted_times.append((hour, predicted_wait_time))

#         # 排序並提取最短和最長的三個時間段
#         sorted_times = sorted(predicted_times, key=lambda x: x[1])
#         shortest_times = [{"Hour": time[0], "PredictedWaitTime": time[1]} for time in sorted_times[:3]]
#         longest_times = [{"Hour": time[0], "PredictedWaitTime": time[1]} for time in sorted_times[-3:]]

#         future_data[facility_mapping[facility]] = {
#             "shortest_times": shortest_times,
#             "longest_times": longest_times
#         }

#     return future_data

# def generate_future_land(date):
#     date_str = date
#     model = joblib.load('/Users/chianlee/Desktop/disney/models/wait_time_model.pkl')
#     facility_mapping = joblib.load('/Users/chianlee/Desktop/disney/models/facility_mapping.pkl')
#     data, visitor_predictions, maintenance_df = read_and_prepare_data(
#         '/Users/chianlee/Desktop/disney/data/day_hour_avg_data_land.json',
#         '/Users/chianlee/Desktop/disney/data/disneyland_predict.json',
#         '/Users/chianlee/Desktop/disney/data/maintenance_land.json'
#     )
#     data, _ = feature_engineering(data)
#     future_data = predict_future_wait_times(date_str, visitor_predictions, data, maintenance_df, model, facility_mapping)

#     return future_data

# def save_recommendations(future_data, date_str):
#     output_file = f'/Users/chianlee/Desktop/disney/data/recom_time_land_{date_str}.json'
#     with open(output_file, 'w') as f:
#         json.dump(future_data, f, indent=4)
#     print(f"Recommendation saved to {output_file}")

# if __name__ == "__main__":
#     date_str = input("請輸入要預測的日期 (格式：YYYY-MM-DD)：")
#     future_data = generate_future_land(date_str)
#     save_recommendations(future_data, date_str)

import pandas as pd
import numpy as np
import joblib
import os
import json
from data_preparation import read_and_prepare_data, assign_time_window
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

def predict_future_wait_times(date_str, visitor_predictions, data, maintenance_df, model, facility_mapping):
    date = pd.to_datetime(date_str).normalize()
    visitor_prediction = visitor_predictions[visitor_predictions['date'] == date]
    
    if visitor_prediction.empty:
        print(f"No visitor prediction found for date: {date_str}")
        return {}

    prediction_value = visitor_prediction['prediction'].values[0]
    is_weekend = visitor_prediction['weekday'].map(weekday_map).values[0]
    day_of_week = visitor_prediction['weekday'].map(weekday_to_num).values[0]

    future_data = {}
    for facility in data['FacilityCode'].unique():
        # 排除維修中的設施
        is_under_maintenance = maintenance_df[
            (maintenance_df['Date'] == date) &
            (maintenance_df['FacilityEnglish'] == facility_mapping[facility])
        ]['IsUnderMaintenance'].any()

        if is_under_maintenance:
            continue  # 跳過維修中的設施

        predicted_times = []
        for hour in range(8, 22):
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

            predicted_times.append((hour, predicted_wait_time))

        # 排序並提取最短和最長的三個時間段
        sorted_times = sorted(predicted_times, key=lambda x: x[1])
        shortest_times = [{"Hour": time[0], "PredictedWaitTime": time[1]} for time in sorted_times[:3]]
        longest_times = [{"Hour": time[0], "PredictedWaitTime": time[1]} for time in sorted_times[-3:]]

        future_data[facility_mapping[facility]] = {
            "shortest_times": shortest_times,
            "longest_times": longest_times
        }

    return future_data

def generate_future_land(date):
    model = joblib.load('/Users/chianlee/Desktop/disney/models/wait_time_model.pkl')
    facility_mapping = joblib.load('/Users/chianlee/Desktop/disney/models/facility_mapping.pkl')
    data, visitor_predictions, maintenance_df = read_and_prepare_data(
        '/Users/chianlee/Desktop/disney/data/day_hour_avg_data_land.json',
        '/Users/chianlee/Desktop/disney/data/disneyland_predict.json',
        '/Users/chianlee/Desktop/disney/data/maintenance_land.json'
    )
    data, _ = feature_engineering(data)
    future_data = predict_future_wait_times(date, visitor_predictions, data, maintenance_df, model, facility_mapping)

    return future_data

def save_recommendations(future_data, date_str):
    output_file = f'/Users/chianlee/Desktop/disney/data/recom_time_land_{date_str}.json'
    with open(output_file, 'w') as f:
        json.dump(future_data, f, indent=4)
    print(f"Recommendation saved to {output_file}")

def predict_and_save_recommendations(date_str):
    """
    包裝所有步驟為一個函數，根據指定日期生成未來排隊時間的預測並保存結果。
    """
    future_data = generate_future_land(date_str)
    # save_recommendations(future_data, date_str)
    return future_data

# 主程式調用範例
if __name__ == "__main__":
    date_str = input("請輸入要預測的日期 (格式：YYYY-MM-DD)：")
    predict_and_save_recommendations(date_str)

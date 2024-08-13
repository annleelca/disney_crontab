# # # import pandas as pd
# # # import numpy as np
# # # import joblib
# # # import json
# # # from data_preparation import read_and_prepare_data
# # # from model_training import feature_engineering

# # # # 定義 weekday_map 和 weekday_to_num 用於特徵工程
# # # weekday_map = {
# # #     'Monday': 1, 'Tuesday': 1, 'Wednesday': 1, 'Thursday': 1, 'Friday': 1, 
# # #     'Saturday': 0, 'Sunday': 0
# # # }
# # # weekday_to_num = {
# # #     'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 
# # #     'Saturday': 5, 'Sunday': 6
# # # }

# # # def load_facility_name_mapping(data_region):
# # #     with open(f'/Users/chianlee/Desktop/disney/data/{data_region}_namelist.json', 'r') as f:
# # #         name_list = json.load(f)
# # #     facility_name_mapping = {item['FacilityEnglish']: item for item in name_list}
# # #     return facility_name_mapping

# # # def predict_future_wait_times(date, visitor_predictions, data, maintenance_df, model, facility_mapping, facility_name_mapping):
# # #     date = pd.to_datetime(date).normalize()
# # #     visitor_prediction = visitor_predictions[visitor_predictions['date'] == date]
    
# # #     if visitor_prediction.empty:
# # #         print(f"No visitor prediction found for date: {date}")
# # #         return {}

# # #     prediction_value = visitor_prediction['prediction'].values[0]
# # #     is_weekend = visitor_prediction['weekday'].map(weekday_map).values[0]
# # #     day_of_week = visitor_prediction['weekday'].map(weekday_to_num).values[0]

# # #     future_data = {}
# # #     for facility in data['FacilityCode'].unique():
# # #         # 排除維修中的設施
# # #         is_under_maintenance = maintenance_df[
# # #             (maintenance_df['Date'] == date) &
# # #             (maintenance_df['FacilityEnglish'] == facility_mapping[facility])
# # #         ]['IsUnderMaintenance'].any()

# # #         if is_under_maintenance:
# # #             continue  # 跳過維修中的設施

# # #         predicted_times = []
# # #         for hour in range(8, 22):
# # #             predicted_wait_time = int(np.round(np.maximum(
# # #                 model.predict(pd.DataFrame([{
# # #                     'Hour': hour,
# # #                     'prediction': prediction_value,
# # #                     'IsWeekend': is_weekend,
# # #                     'DayOfWeek': day_of_week,
# # #                     'FacilityCode': facility,
# # #                     'TimeWindow': 0 if hour < 12 else (1 if hour < 18 else 2),
# # #                     'IsUnderMaintenance': 0  # 保留特徵，但設定為0表示未維修
# # #                 }])), 0)).astype(int)[0])

# # #             predicted_times.append({"Hour": hour, "WaitTime": predicted_wait_time})

# # #         # 排序並提取最短的三個時間段
# # #         sorted_times = sorted(predicted_times, key=lambda x: x['WaitTime'])[:3]

# # #         facility_info = facility_name_mapping.get(facility_mapping[facility], {})
# # #         facility_key = facility_info.get('FacilityMandarin', '未知設施')
# # #         future_data[facility_key] = sorted_times

# # #     return future_data

# # # def generate_future_land(date, data_region):
# # #     model = joblib.load(f'/Users/chianlee/Desktop/disney/models/wait_time_model_{data_region}.pkl')
# # #     facility_mapping = joblib.load(f'/Users/chianlee/Desktop/disney/models/facility_mapping_{data_region}.pkl')
# # #     facility_name_mapping = load_facility_name_mapping(data_region)

# # #     data, visitor_predictions, maintenance_df = read_and_prepare_data(
# # #         f'/Users/chianlee/Desktop/disney/data/day_hour_avg_data_{data_region}.json',
# # #         f'/Users/chianlee/Desktop/disney/data/disney{data_region}_predict.json',
# # #         f'/Users/chianlee/Desktop/disney/data/maintenance_{data_region}.json'
# # #     )
# # #     data, _ = feature_engineering(data)
# # #     future_data = predict_future_wait_times(date, visitor_predictions, data, maintenance_df, model, facility_mapping, facility_name_mapping)

# # #     return future_data

# # # def save_recommendations(future_data, date, data_region):
# # #     output_file = f'/Users/chianlee/Desktop/disney/data/predict/recom_{data_region}_{date}.json'
# # #     with open(output_file, 'w', encoding='utf-8') as f:
# # #         json.dump(future_data, f, indent=4, ensure_ascii=False)

# # # def predict_and_return_recommendations(date, data_region):
# # #     future_data = generate_future_land(date, data_region)
# # #     print(future_data)
# # #     return future_data  # 直接返回資料

# # # def predict_and_save_recommendations(date, data_region):
# # #     future_data = generate_future_land(date, data_region)
# # #     save_recommendations(future_data, date, data_region)  # 原先將資料保存到文件

# # # # 驗證並修正行程
# # # def validate_and_correct_itinerary(itinerary, predictions):
# # #     validated_itinerary = []
# # #     seen_attractions = set()

# # #     for item in itinerary:
# # #         official_name = item["Attraction"]
# # #         if official_name in predictions and official_name not in seen_attractions:
# # #             valid_times = [p["WaitTime"] for p in predictions[official_name]]
# # #             if item["WaitTime"] in valid_times:
# # #                 validated_itinerary.append(item)
# # #                 seen_attractions.add(official_name)
# # #             else:
# # #                 print(f"預測時間不一致：{item['Attraction']}，請檢查數據。")

# # #     return validated_itinerary


# # # # 主程式調用範例
# # # if __name__ == "__main__":
# # #     date = input("請輸入要預測的日期 (格式：YYYY-MM-DD)：")
# # #     data_region = input("請輸入資料區域 (Land 或 Sea)：").strip().lower()
# # #     predict_and_save_recommendations(date, data_region)

# # import pandas as pd
# # import numpy as np
# # import joblib
# # import json
# # from collections import defaultdict
# # from data_preparation import read_and_prepare_data
# # from model_training import feature_engineering

# # # 定義 weekday_map 和 weekday_to_num 用於特徵工程
# # weekday_map = {
# #     'Monday': 1, 'Tuesday': 1, 'Wednesday': 1, 'Thursday': 1, 'Friday': 1, 
# #     'Saturday': 0, 'Sunday': 0
# # }
# # weekday_to_num = {
# #     'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 
# #     'Saturday': 5, 'Sunday': 6
# # }

# # def load_facility_name_mapping(data_region):
# #     with open(f'/Users/chianlee/Desktop/disney/data/{data_region}_namelist.json', 'r') as f:
# #         name_list = json.load(f)
# #     facility_name_mapping = {item['FacilityEnglish']: item for item in name_list}
# #     return facility_name_mapping

# # def predict_future_wait_times(date, visitor_predictions, data, maintenance_df, model, facility_mapping, facility_name_mapping):
# #     date = pd.to_datetime(date).normalize()
# #     visitor_prediction = visitor_predictions[visitor_predictions['date'] == date]
    
# #     if visitor_prediction.empty:
# #         print(f"No visitor prediction found for date: {date}")
# #         return {}

# #     prediction_value = visitor_prediction['prediction'].values[0]
# #     is_weekend = visitor_prediction['weekday'].map(weekday_map).values[0]
# #     day_of_week = visitor_prediction['weekday'].map(weekday_to_num).values[0]

# #     future_data = {}
# #     time_slot_recommendations = defaultdict(list)

# #     for facility in data['FacilityCode'].unique():
# #         # 排除維修中的設施
# #         is_under_maintenance = maintenance_df[
# #             (maintenance_df['Date'] == date) &
# #             (maintenance_df['FacilityEnglish'] == facility_mapping[facility])
# #         ]['IsUnderMaintenance'].any()

# #         if is_under_maintenance:
# #             continue  # 跳過維修中的設施

# #         predicted_times = []
# #         for hour in range(8, 21):
# #             predicted_wait_time = int(np.round(np.maximum(
# #                 model.predict(pd.DataFrame([{
# #                     'Hour': hour,
# #                     'prediction': prediction_value,
# #                     'IsWeekend': is_weekend,
# #                     'DayOfWeek': day_of_week,
# #                     'FacilityCode': facility,
# #                     'TimeWindow': 0 if hour < 12 else (1 if hour < 18 else 2),
# #                     'IsUnderMaintenance': 0  # 保留特徵，但設定為0表示未維修
# #                 }])), 0)).astype(int)[0])

# #             predicted_times.append({"Hour": hour, "WaitTime": predicted_wait_time})

# #         # 排序並提取最短的三個時間段
# #         sorted_times = sorted(predicted_times, key=lambda x: x['WaitTime'])[:1]

# #         facility_info = facility_name_mapping.get(facility_mapping[facility], {})
# #         facility_key = facility_info.get('FacilityMandarin', '未知設施')
# #         future_data[facility_key] = sorted_times

# #         # 將每個設施的最佳時段加到時間段推薦列表中
# #         for time in sorted_times:
# #             time_slot_recommendations[time['Hour']].append(facility_key)

# #     # 按時間段對 time_slot_recommendations 進行排序
# #     sorted_time_slot_recommendations = dict(sorted(time_slot_recommendations.items()))


# #     return future_data, sorted_time_slot_recommendations

# # def generate_future_land(date, data_region):
# #     model = joblib.load(f'/Users/chianlee/Desktop/disney/models/wait_time_model_{data_region}.pkl')
# #     facility_mapping = joblib.load(f'/Users/chianlee/Desktop/disney/models/facility_mapping_{data_region}.pkl')
# #     facility_name_mapping = load_facility_name_mapping(data_region)

# #     data, visitor_predictions, maintenance_df = read_and_prepare_data(
# #         f'/Users/chianlee/Desktop/disney/data/day_hour_avg_data_{data_region}.json',
# #         f'/Users/chianlee/Desktop/disney/data/disney{data_region}_predict.json',
# #         f'/Users/chianlee/Desktop/disney/data/maintenance_{data_region}.json'
# #     )
# #     data, _ = feature_engineering(data)
# #     future_data, sorted_time_slot_recommendations = predict_future_wait_times(date, visitor_predictions, data, maintenance_df, model, facility_mapping, facility_name_mapping)

# #     return future_data, sorted_time_slot_recommendations

# # def save_recommendations(future_data, sorted_time_slot_recommendations, date, data_region):
# #     # 保存未整理的推薦時間數據
# #     output_file = f'/Users/chianlee/Desktop/disney/data/predict/recom_{data_region}_{date}.json'
# #     with open(output_file, 'w', encoding='utf-8') as f:
# #         json.dump(future_data, f, indent=4, ensure_ascii=False)

# #     # 保存按時段整理的推薦設施數據
# #     output_file_by_time = f'/Users/chianlee/Desktop/disney/data/predict/recom_{data_region}_{date}_by_time.json'
# #     with open(output_file_by_time, 'w', encoding='utf-8') as f:
# #         json.dump(sorted_time_slot_recommendations, f, indent=4, ensure_ascii=False)
    

# # def predict_and_save_recommendations(date, data_region):
# #     future_data, sorted_time_slot_recommendations = generate_future_land(date, data_region)
# #     save_recommendations(future_data, sorted_time_slot_recommendations, date, data_region)

# # # 驗證並修正行程
# # def validate_and_correct_itinerary(itinerary, predictions):
# #     validated_itinerary = []
# #     seen_attractions = set()

# #     for item in itinerary:
# #         official_name = item["Attraction"]
# #         if official_name in predictions and official_name not in seen_attractions:
# #             valid_times = [p["WaitTime"] for p in predictions[official_name]]
# #             if item["WaitTime"] in valid_times:
# #                 validated_itinerary.append(item)
# #                 seen_attractions.add(official_name)
# #             else:
# #                 print(f"預測時間不一致：{item['Attraction']}，請檢查數據。")

# #     return validated_itinerary

# # # 主程式調用範例
# # if __name__ == "__main__":
# #     date = input("請輸入要預測的日期 (格式：YYYY-MM-DD)：")
# #     data_region = input("請輸入資料區域 (Land 或 Sea)：").strip().lower()
# #     predict_and_save_recommendations(date, data_region)

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
    with open(f'/Users/chianlee/Desktop/disney/data/{data_region}_namelist.json', 'r') as f:
        name_list = json.load(f)
    facility_name_mapping = {item['FacilityEnglish']: item for item in name_list}
    return facility_name_mapping

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

        predicted_times = []
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

            predicted_times.append({"Hour": hour, "WaitTime": predicted_wait_time})

        # 排序並提取最短的n個時間段
        sorted_times = sorted(predicted_times, key=lambda x: x['WaitTime'])[:62]

        facility_info = facility_name_mapping.get(facility_mapping[facility], {})
        facility_key = facility_info.get('FacilityMandarin', '未知設施')
        future_data[facility_key] = sorted_times
        detailed_times_data[facility_key] = predicted_times

        # 將每個設施的最佳時段加到時間段推薦列表中
        for time in predicted_times:
            time_slot_recommendations[time['Hour']].append({
                facility_key: f"wait {time['WaitTime']} min"
            })

    # 按時間段對 time_slot_recommendations 進行排序
    sorted_time_slot_recommendations = dict(sorted(time_slot_recommendations.items()))

    return future_data, sorted_time_slot_recommendations, detailed_times_data

def generate_future_land(date, data_region):
    model = joblib.load(f'/Users/chianlee/Desktop/disney/models/wait_time_model_{data_region}.pkl')
    facility_mapping = joblib.load(f'/Users/chianlee/Desktop/disney/models/facility_mapping_{data_region}.pkl')
    facility_name_mapping = load_facility_name_mapping(data_region)

    data, visitor_predictions, maintenance_df = read_and_prepare_data(
        f'/Users/chianlee/Desktop/disney/data/day_hour_avg_data_{data_region}.json',
        f'/Users/chianlee/Desktop/disney/data/disney{data_region}_predict.json',
        f'/Users/chianlee/Desktop/disney/data/maintenance_{data_region}.json'
    )
    data, _ = feature_engineering(data)
    future_data, sorted_time_slot_recommendations, detailed_times_data = predict_future_wait_times(date, visitor_predictions, data, maintenance_df, model, facility_mapping, facility_name_mapping)

    return future_data, sorted_time_slot_recommendations, detailed_times_data

def save_recommendations(future_data, sorted_time_slot_recommendations, detailed_times_data, date, data_region):
    # 保存未整理的推薦時間數據
    output_file = f'/Users/chianlee/Desktop/disney/data/predict/recom_{data_region}_{date}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(future_data, f, indent=4, ensure_ascii=False)

    # 保存按時段整理的推薦設施數據
    output_file_by_time = f'/Users/chianlee/Desktop/disney/data/predict/recom_{data_region}_{date}_by_time.json'
    with open(output_file_by_time, 'w', encoding='utf-8') as f:
        json.dump(sorted_time_slot_recommendations, f, indent=4, ensure_ascii=False)

    # 保存每個設施各時段等候時間數據
    output_file_detailed = f'/Users/chianlee/Desktop/disney/data/predict/detailed_{data_region}_{date}.json'
    with open(output_file_detailed, 'w', encoding='utf-8') as f:
        json.dump(detailed_times_data, f, indent=4, ensure_ascii=False)

def predict_and_save_recommendations(date, data_region):
    future_data, sorted_time_slot_recommendations, detailed_times_data = generate_future_land(date, data_region)
    save_recommendations(future_data, sorted_time_slot_recommendations, detailed_times_data, date, data_region)

def predict_and_return_recommendations(date, data_region):
    detailed_times_data = generate_future_land(date, data_region)
    print(detailed_times_data)
    return detailed_times_data  # 直接返回資料

# 主程式調用範例
if __name__ == "__main__":
    date = input("請輸入要預測的日期 (格式：YYYY-MM-DD)：")
    data_region = input("請輸入資料區域 (Land 或 Sea)：").strip().lower()
    predict_and_save_recommendations(date, data_region)


# import pandas as pd
# import numpy as np
# import joblib
# import json
# from collections import defaultdict
# from data_preparation import read_and_prepare_data
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

# def load_facility_name_mapping(data_region):
#     with open(f'/Users/chianlee/Desktop/disney/data/{data_region}_namelist.json', 'r') as f:
#         name_list = json.load(f)
#     facility_name_mapping = {item['FacilityEnglish']: item for item in name_list}
#     return facility_name_mapping

# def predict_future_wait_times(date, visitor_predictions, data, maintenance_df, model, facility_mapping, facility_name_mapping):
#     date = pd.to_datetime(date).normalize()
#     visitor_prediction = visitor_predictions[visitor_predictions['date'] == date]
    
#     if visitor_prediction.empty:
#         print(f"No visitor prediction found for date: {date}")
#         return {}

#     prediction_value = visitor_prediction['prediction'].values[0]
#     is_weekend = visitor_prediction['weekday'].map(weekday_map).values[0]
#     day_of_week = visitor_prediction['weekday'].map(weekday_to_num).values[0]

#     detailed_times_data = {}

#     for facility in data['FacilityCode'].unique():
#         # 排除維修中的設施
#         is_under_maintenance = maintenance_df[
#             (maintenance_df['Date'] == date) &
#             (maintenance_df['FacilityEnglish'] == facility_mapping[facility])
#         ]['IsUnderMaintenance'].any()

#         if is_under_maintenance:
#             continue  # 跳過維修中的設施

#         predicted_times = []
#         for hour in range(8, 21):
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

#             predicted_times.append({"Hour": hour, "WaitTime": predicted_wait_time})

#         facility_info = facility_name_mapping.get(facility_mapping[facility], {})
#         facility_key = facility_info.get('FacilityMandarin', '未知設施')
#         detailed_times_data[facility_key] = predicted_times

#     return detailed_times_data

# def generate_future_land(date, data_region):
#     model = joblib.load(f'/Users/chianlee/Desktop/disney/models/wait_time_model_{data_region}.pkl')
#     facility_mapping = joblib.load(f'/Users/chianlee/Desktop/disney/models/facility_mapping_{data_region}.pkl')
#     facility_name_mapping = load_facility_name_mapping(data_region)

#     data, visitor_predictions, maintenance_df = read_and_prepare_data(
#         f'/Users/chianlee/Desktop/disney/data/day_hour_avg_data_{data_region}.json',
#         f'/Users/chianlee/Desktop/disney/data/disney{data_region}_predict.json',
#         f'/Users/chianlee/Desktop/disney/data/maintenance_{data_region}.json'
#     )
#     data, _ = feature_engineering(data)
#     detailed_times_data = predict_future_wait_times(date, visitor_predictions, data, maintenance_df, model, facility_mapping, facility_name_mapping)

#     return detailed_times_data

# def save_recommendations(future_data, sorted_time_slot_recommendations, detailed_times_data, date, data_region):
#     # 保存每個設施各時段等候時間數據
#     output_file_detailed = f'/Users/chianlee/Desktop/disney/data/predict/detailed_{data_region}_{date}.json'
#     with open(output_file_detailed, 'w', encoding='utf-8') as f:
#         json.dump(detailed_times_data, f, indent=4, ensure_ascii=False)

# def predict_and_save_recommendations(date, data_region):
#     detailed_times_data = generate_future_land(date, data_region)
#     save_recommendations({}, {}, detailed_times_data, date, data_region)

# def predict_and_return_recommendations(date, data_region):
#     detailed_times_data = generate_future_land(date, data_region)
#     print(detailed_times_data)
#     return detailed_times_data  # 直接返回資料

# # 主程式調用範例
# if __name__ == "__main__":
#     date = input("請輸入要預測的日期 (格式：YYYY-MM-DD)：")
#     data_region = input("請輸入資料區域 (Land 或 Sea)：").strip().lower()
#     predict_and_save_recommendations(date, data_region)

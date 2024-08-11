import os
import joblib
from data_preparation import read_and_prepare_data
from model_training import feature_engineering, train_model

def train_and_save_model():
    # 設定新數據的路徑
    wait_times_path = '/Users/chianlee/Desktop/disney/data/day_hour_avg_data_land.json'
    visitor_predictions_path = '/Users/chianlee/Desktop/disney/data/disneyland_predict.json'
    maintenance_data_path = '/Users/chianlee/Desktop/disney/data/maintenance_land.json'

    # 讀取並準備數據
    data, visitor_predictions, expanded_maintenance_df = read_and_prepare_data(wait_times_path, visitor_predictions_path, maintenance_data_path)

    # 特徵工程
    data, facility_mapping = feature_engineering(data)

    # 訓練模型
    model, rmse = train_model(data)
    print(f"模型的RMSE: {rmse}")

    # 確保目錄存在
    model_dir = '/Users/chianlee/Desktop/disney/models/'
    os.makedirs(model_dir, exist_ok=True)

    #保存模型和映射，自動覆蓋舊文件
    joblib.dump(model, os.path.join(model_dir, 'wait_time_model.pkl'))
    joblib.dump(facility_mapping, os.path.join(model_dir, 'facility_mapping.pkl'))
# 執行訓練並保存模型
train_and_save_model()

from sklearn.model_selection import train_test_split
import xgboost as xgb
from sklearn.metrics import mean_squared_error
import numpy as np
from data_preparation import assign_time_window

def feature_engineering(data):
    weekday_map = {
        'Monday': 1, 'Tuesday': 1, 'Wednesday': 1, 'Thursday': 1, 'Friday': 1, 
        'Saturday': 0, 'Sunday': 0
    }
    weekday_to_num = {
        'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 
        'Saturday': 5, 'Sunday': 6
    }
    data['IsWeekend'] = data['weekday'].map(weekday_map)
    data['DayOfWeek'] = data['weekday'].map(weekday_to_num)
    data['TimeWindow'] = data['Hour'].apply(assign_time_window).astype('category').cat.codes
    data['FacilityCode'] = data['FacilityEnglish'].astype('category').cat.codes
    facility_mapping = dict(enumerate(data['FacilityEnglish'].astype('category').cat.categories))
    
    return data, facility_mapping

def train_model(data):
    features = ['Hour', 'prediction', 'IsWeekend', 'DayOfWeek', 'FacilityCode', 'TimeWindow', 'IsUnderMaintenance']
    X = data[features]
    y = data['StandbyTime']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = xgb.XGBRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_pred = np.maximum(y_pred, 0)

    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    
    return model, rmse


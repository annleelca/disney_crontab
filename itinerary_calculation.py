import re
from collections import defaultdict
from datetime import datetime, timedelta

def parse_itinerary(content):
    itinerary = defaultdict(list)
    current_period = None

    lines = content.splitlines()
    for line in lines:
        if '###' in line:
            current_period = line.strip('# ').strip()
        elif re.match(r'^\d+\.', line):  # 匹配項目行
            match = re.match(r'\d+\.\s*(.*?)\s*\((\d+)\s*分鐘\)', line)
            if match and current_period:
                name, duration = match.groups()
                itinerary[current_period].append((name, f"{duration} 分鐘"))
    
    return itinerary

def calculate_schedule(itinerary):
    current_time = datetime.strptime("08:30", "%H:%M")
    end_time = datetime.strptime("20:00", "%H:%M")
    schedule = []

    for period, activities in itinerary.items():
        for activity in activities:
            name, duration_str = activity
            duration = int(duration_str.split()[0])
            start_time = current_time
            finish_time = start_time + timedelta(minutes=duration)

            # 檢查是否會超過 20:00
            if finish_time > end_time:
                # 檢查剩餘時間是否足夠進行完整的活動
                if start_time < end_time:
                    remaining_time = (end_time - start_time).seconds // 60
                    if remaining_time > 0:
                        schedule.append(f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')} {name} (部分)")
                break  # 結束安排，因為已達到時間限制
            else:
                schedule.append(f"{start_time.strftime('%H:%M')} - {finish_time.strftime('%H:%M')} {name}")
                current_time = finish_time

    return schedule



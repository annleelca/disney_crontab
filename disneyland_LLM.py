import requests
import os
import json
from dotenv import load_dotenv
import predict_round_num as recom
import re

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

def get_completion(messages, model="gpt-4o", temperature=0, max_tokens=1000, tools=None):
    payload = { "model": model, "temperature": temperature, "messages": messages, "max_tokens": max_tokens }
    if tools:
        payload["tools"] = tools

    headers = { "Authorization": f'Bearer {openai_api_key}', "Content-Type": "application/json" }
    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, data=json.dumps(payload))

    try:
        obj = response.json()
    except json.JSONDecodeError:
        print("Error: Response decoding failed")
        return {"error": "Response decoding failed"}

    if response.status_code == 200:
        print("Success: API call successful")
        return obj["choices"][0]["message"]
    else:
        print(f"Error: API call failed with status code {response.status_code}")
        return obj.get("error", "Unknown error occurred")

available_tools = {
    "itinerary_making": recom.predict_and_return_recommendations,  
}

function_prompt = {
    "itinerary_making": """ 
    資料：各設施在不同時段適合的行程時間
            morning = 8:00-11:00
            noon = 11:00-14:00
            afternoon = 14:00-17:00
            evening = 17:00 -20:00  

    任務：安排從8:00到20:00整天的行程，行程時間必須與資料中的時間完全一致，每個設施限安排一次。

    行程安排步驟：
    1. 列出使用者指定的遊樂設施名稱。
    2. 安排時段給指定的遊樂設施，行程時間嚴格遵守資料。
    3. 剩餘時段安排其他設施，若有空擋則安排逛街、用餐。
    4. 對每個設施的行程時間進行預檢查：
        檢查該行程是否與資料中的行程時間完全相符。
        若檢查中發現時間錯誤，應自動調整該行程段的時間，並動態調整後續行程段的安排。
    5. 注意！不允許重複安排相似的設施，美國海濱、地中海港灣視為同設施。
    6. 確保行程從8:00-20:00
    7. 確保設施名稱正確無誤且為官方全名。    

    輸出範例：
    8:00 - 8:25 茉莉公主的飛天魔毯 
    （行程時間：25分鐘）
    8:25 - 9:00 安娜與艾莎的冰雪之旅
    （行程時間：35分鐘）
    """,
}

def remove_calculation_details(response_content):
    # 移除包含 "行程時間" 的整行
    filtered_content = re.sub(r'^.*行程時間.*$', '', response_content, flags=re.MULTILINE)
    return filtered_content


def get_completion_with_function_execution(messages, model="gpt-4o", temperature=0, max_tokens=800, tools=None):
    response = get_completion(messages, model, temperature, max_tokens, tools)
    
    if isinstance(response, dict) and "content" in response:
        print("Content received from GPT-4:", response["content"])
        messages.append(response)
    else:
        print(f"Error: Unexpected response format - {response}")
        return {"content": "抱歉，無法處理您的請求。"}

    if isinstance(response, dict) and 'tool_calls' in response:
        print("Tool calls detected.")
        for tool_call in response["tool_calls"]:
            function_name = tool_call["function"]["name"]
            id = tool_call["id"]
            function_args = json.loads(tool_call["function"]["arguments"])
            function_to_call = available_tools[function_name]
            
            # 動態傳遞參數給函數，並獲取資料
            function_response = function_to_call(**function_args)
            
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": id,
                    "name": function_name,
                    "content": json.dumps(function_response, indent=4)  
                }
            )
            messages.append(
                {
                    "role": "system",
                    "content": function_prompt[function_name]
                }
            )
        
        response = get_completion(messages, model, temperature, max_tokens)
        print(f"Final response from GPT-4: {response}")

        # # 移除包含 "行程時間" 的行
        # response["content"] = remove_calculation_details(response["content"])
        # messages.append(response)
    else:
        print("No tool calls found in the response.")

    return response


def function_call(user_input, messages):
    system_input = "你是使用者的迪士尼使用助手，可以幫忙安排行程，務必顯示正確的設施名稱，不能回答不相關的問題"
    if len(messages) == 0:
        messages.append({"role": "system", "content": system_input})
    
    messages.append({"role": "user", "content": user_input})

    tools = [        
       {
            "type": "function",
            "function": {
                "name": "itinerary_making",
                "description": "依照使用者需求，根據預測的設施等候時間，排出最佳行程",
                "parameters": {
                    "type": "object",
                    "properties": {
                       "date": {
                            "type": "string",
                            "description": "遊玩日期",
                        },
                        "data_region": {
                            "type": "string",
                            "description": "region(land or sea)",
                        },
                    },
                    "required": ["date", "data_region"],
                },
            },
        },
    ]
    
    response = get_completion_with_function_execution(messages, tools=tools)
    if isinstance(response, dict) and "content" in response:
        return response["content"]
    else:
        print(f"Error: No content returned - {response}")
        return "抱歉，發生錯誤，無法生成行程。"

if __name__ == "__main__":
    messages = []
    user_input = "我2024-08-25想去東京迪士尼海洋，一定要玩到海底兩萬哩、安娜與艾莎的冰雪之旅"
    response = function_call(user_input, messages)
    print(response)

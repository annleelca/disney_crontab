import requests
import os
import json
from dotenv import load_dotenv
import predict_round_num as itin
import itinerary_calculation as cal
import recommend as recom

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

def get_completion(messages, model="gpt-4o", temperature=0, max_tokens=1000, tools=None):
    payload = { "model": model, "temperature": temperature, "messages": messages, "max_tokens": max_tokens }
    if tools:
        payload["tools"] = tools

    headers = { "Authorization": f'Bearer {openai_api_key}', "Content-Type": "application/json" }
    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, data=json.dumps(payload))

    try:
        # 先將回應內容解碼為 UTF-8 編碼，然後再轉換為 JSON 物件
        response_text = response.content.decode('utf-8')
        obj = json.loads(response_text)
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
    "itinerary_making": itin.predict_and_return_recommendations, 
    "recommend": recom.recommend,   
}
function_prompt = {
    "itinerary_making": """ 
    任務：根據使用者需求安排一日多元行程，整個行程中各設施僅安排一次，禁止在不同時段重複安排同一設施。

    安排行程步驟：
    1. 列出使用者指定的遊樂設施名稱。
    2. 根據各設施在不同時段的預測等待時間，優先選擇尚未安排過的設施，以確保行程多樣且無重複。
    3. 嚴格避免在不同時段內安排同類型或名稱相似的設施。
    4. 剩餘時段安排其他尚未安排的設施，確保整個行程豐富多樣。
    5. 確保各時段的行程總計接近180分鐘，無需重複安排設施來填滿時間。
    6. 生成行程後，檢查整個行程，確保沒有設施在不同時段內重複安排。若有重複，則重新生成行程。

    輸出格式：
    morning: 設施1, 設施2, ...
    noon: 設施3, 設施4, ...
    afternoon: 設施5, 設施6, ...
    evening: 設施7, 設施8, ...

    注意！生成行程後，檢查整個行程，確保沒有設施在不同時段內重複安排。如果發現重複，則重新生成行程。
    """,
    "recommend": """
    根據使用者問題，依照事實回答問題，精簡回答，限定最多150字
    """,
}

def get_completion_with_function_execution(messages, model="gpt-4o", temperature=0, max_tokens=800, tools=None):
    response = get_completion(messages, model, temperature, max_tokens, tools)
    
    if isinstance(response, dict) and "content" in response:
        print("Content received from GPT-4:", response["content"])
        messages.append(response)
    else:
        print(f"Error: Unexpected response format - {response}")
        return "抱歉，無法處理您的請求。"

    if 'tool_calls' in response:
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
        
    itinerary = cal.parse_itinerary(response["content"])  # 解析行程
    print(itinerary)
    schedule = cal.calculate_schedule(itinerary)  # 使用 calculate_schedule 計算具體時間表

    # 格式化並返回結果
    return "\n".join(schedule)

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
                "description": "依照使用者需求，根據預測的行程時間，排出行程",
                "parameters": {
                    "type": "object",
                    "properties": {
                       "date": {
                            "type": "string",
                            "description": "遊玩日期，預測為2024年",
                        },
                        "data_region": {
                            "type": "string",
                            "description": "region(land or sea)",
                        },
                    },
                    "required": ["date", "data region"],
                },
            },
        },
        {
    "type": "function",
    "function": {
        "name": "recommend",
        "description": "依照使用者需求，提供適合的遊樂設施、商店或餐廳資訊",
        "parameters": {
            "type": "object",
            "properties": {
                "data_region": {
                    "type": "string",
                    "description": "region (land or sea)"
                },
                "recommend_type": {
                    "type": "string",
                    "description": "facility, store, or food"
                }
            },
            "required": ["data_region", "recommend_type"]
        }
    }
}
    ]
    
    response = get_completion_with_function_execution(messages, tools=tools)
    return response  # 確保返回結果

if __name__ == "__main__":
    messages = []
    user_input = "我10/30想去東京迪士尼海洋，幫我排行程一定要玩到安娜與艾莎的冰雪之旅、玩具總動員瘋狂遊戲屋"
    # user_input = "請推薦我迪士尼海洋區刺激的設施"
    response = function_call(user_input, messages)
    print(response)  

import requests
import os
import json
from dotenv import load_dotenv
import predict_future as recom

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
    依照使用者需求安排行程，你得到的資訊為各設施從8:00-20:00每小時的預測等候時間。
    行程時間 = 預測排隊時間 + 20 分鐘，然後無條件進位到最近的10的倍數。

    注意事項：
    1. 嚴格依據提供的預測數據進行時間安排，確保每個設施的排隊時間正確性。
    2. 務必檢查設施名稱是否正確且為官方全名，避免使用非標準或簡化名稱。
    3. 確保每個設施只出現在行程中一次，避免重複安排。
    確認行程時間安排符合規定：
    預測排隊時間 + 20 分鐘 = 行程時間（無條件進位至10的倍數）

    行程格式範例：
    8:00-8:50 美女與野獸「城堡奇緣」
        -預測排隊時間：27分鐘

    8:50-9:20 巨雷山
        -預測排隊時間：5分鐘

    9:20-10:00 幽靈公館
        -預測排隊時間：15分鐘
    """,
}



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
        messages.append(response)
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
    user_input = "我2024-08-25想去東京迪士尼陸地，請安排一整天的行程，一定要玩到茉莉公主的飛天魔毯、安娜與艾莎的冰雪之旅"
    response = function_call(user_input, messages)
    print(response)

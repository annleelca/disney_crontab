import requests
import os
import json
from dotenv import load_dotenv
import predict_future as recom

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

def get_completion(messages, model="gpt-4o-mini", temperature=0, max_tokens=1000, tools=None):
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
    "itinerary_making": recom.predict_and_save_recommendations,
}

function_prompt = {
    "itinerary_making": "請根據使用者需求安排出遊玩期間最有效率的行程，並標示每個設施預測的排隊時間。",
}

def get_completion_with_function_execution(messages, model="gpt-4o-mini", temperature=0, max_tokens=800, tools=None):
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
            
            # 直接將 'date' 鍵的值作為參數傳遞給函數
            date_str = function_args['date']
            function_response = function_to_call(date_str)
            
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": id,
                    "name": function_name,
                    "content": str(function_response)
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
    system_input = "你是使用者的迪士尼使用助手，可以幫忙安排行程，不能回答不相關的問題"
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
                    },
                    "required": ["date"],
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
    user_input = "我2024-08-15想去東京迪士尼陸地區，請安排行程"
    response = function_call(user_input, messages)
    print(response)

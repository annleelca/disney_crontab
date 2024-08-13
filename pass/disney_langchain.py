import os
from dotenv import load_dotenv
from langchain_openai.chat_models import ChatOpenAI  
from langchain_core.runnables import RunnableSequence, RunnableLambda
from pydantic import BaseModel

import predict_future as recom

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

# 定義函數參數的Pydantic模型
class ItineraryMakingArgs(BaseModel):
    date: str
    data_region: str

# 定義工具函數
def itinerary_making_tool(date: str, data_region: str):
    return recom.predict_and_return_recommendations(date=date, data_region=data_region)

# 設置LangChain的聊天模型
llm = ChatOpenAI(model="gpt-4o-mini", api_key=openai_api_key)

# 定義一個處理 LLM 輸出的自定義函數
def process_llm_output(output):
    print(f"Processing with tool using LLM output: {output}")
    # 在這裡我們假設 LLM 的輸出可以直接用於工具函數
    final_result = itinerary_making_tool(date, data_region)
    return final_result

# 使用 RunnableLambda 包裝自定義函數
custom_step = RunnableLambda(process_llm_output)

# 使用 RunnableSequence 來構建模型和工具的執行順序，直接傳遞步驟
sequence = RunnableSequence(llm, custom_step)

def function_call(user_input, messages):
    system_input = "你是使用者的迪士尼使用助手，可以幫忙安排行程，不能回答不相關的問題"
    if len(messages) == 0:
        messages.append({"role": "system", "content": system_input})

    messages.append({"role": "user", "content": user_input})
    
    # 使用 RunnableSequence 來處理模型回應並傳遞給工具
    final_result = sequence.invoke(messages)
    
    if isinstance(final_result, dict):
        return final_result
    else:
        print(f"Error: Unexpected result format - {final_result}")
        return "抱歉，發生錯誤，無法生成行程。"

if __name__ == "__main__":
    messages = []
    user_input = "我2024-08-20想去東京迪士尼陸地區，請安排行程"
    response = function_call(user_input, messages)
    print(response)



import json

def recommend(data_region, recommend_type):
    """根據使用者選擇的地區和推薦類型讀取 JSON 文件並提供推薦"""
    # 動態生成文件路徑
    file_path = f'data/{recommend_type}_recom_{data_region}.json'

    # 讀取 JSON 文件並返回其內容
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            recommendations = json.load(file)
    except FileNotFoundError:
        return {"error": f"無法找到文件: {file_path}"}
    except json.JSONDecodeError:
        return {"error": f"無法解析文件: {file_path}"}

    # 根據推薦類型返回對應的推薦資訊
    return {f"recommended_{recommend_type}": recommendations}

# 測試
if __name__ == "__main__":
    data_region = "sea"  # 假設使用者選擇了 Sea 區域
    recommend_type = "facility"  # 假設使用者想要設施推薦

    recommendations = recommend(data_region, recommend_type)
    print(json.dumps(recommendations, ensure_ascii=False, indent=2))

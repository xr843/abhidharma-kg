# llm_concept_extractor.py
import os
import json
import requests
import time
import sys  # 添加这一行
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# API配置
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-pro")

def extract_concepts_with_llm(text_segment):
    """使用大模型从文本段落中提取阿毗达摩法相概念"""
    # 这里是简化的示例，实际实现取决于你使用的具体大模型API
    prompt = f"""
    分析以下阿毗达摩文本，提取所有法相概念及其关系：
    
    {text_segment}
    
    请以JSON格式返回提取的概念和关系：
    {{
        "concepts": [
            {{"id": "unique_id", "name": "概念名称", "description": "概念描述", "category": "概念类别"}}
        ],
        "relations": [
            {{"source": "source_concept_id", "target": "target_concept_id", "type": "关系类型", "weight": 关系强度}}
        ]
    }}
    """
    
    # 根据你使用的API调整相应的请求代码
    response = call_llm_api(prompt)
    
    # 解析响应并返回提取的概念和关系
    return parse_llm_response(response)

def call_llm_api(prompt):
    """调用大模型API"""
    # 示例：调用Google的Gemini API，实际使用时请替换为你的API实现
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LLM_API_KEY}"
    }
    data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2}
    }
    
    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1/models/{LLM_MODEL}:generateContent",
        headers=headers,
        json=data
    )
    
    return response.json()

def parse_llm_response(response):
    """解析大模型API的响应"""
    # 示例：解析Gemini API的响应，实际使用时请根据你的API调整
    try:
        text = response['candidates'][0]['content']['parts'][0]['text']
        # 提取JSON部分
        json_str = text[text.find('{'):text.rfind('}')+1]
        return json.loads(json_str)
    except Exception as e:
        print(f"解析响应失败: {e}")
        return {"concepts": [], "relations": []}

def process_all_segments(segments_file, output_dir):
    """处理所有文本段落，提取概念和关系"""
    # 加载文本段落
    with open(segments_file, 'r', encoding='utf-8') as f:
        segments = json.load(f)
    
    all_concepts = {}
    all_relations = []
    
    # 处理每个段落
    for i, segment in enumerate(segments):
        print(f"处理段落 {i+1}/{len(segments)}")
        
        # 调用大模型提取概念和关系
        result = extract_concepts_with_llm(segment)
        
        # 合并概念（避免重复）
        for concept in result.get("concepts", []):
            concept_id = concept["id"]
            if concept_id not in all_concepts:
                all_concepts[concept_id] = concept
        
        # 添加关系
        all_relations.extend(result.get("relations", []))
        
        # 避免API限流
        time.sleep(2)
    
    # 保存结果
    os.makedirs(output_dir, exist_ok=True)
    
    with open(os.path.join(output_dir, "concepts.json"), 'w', encoding='utf-8') as f:
        json.dump(list(all_concepts.values()), f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(output_dir, "relations.json"), 'w', encoding='utf-8') as f:
        json.dump(all_relations, f, ensure_ascii=False, indent=2)
    
    print(f"共提取出 {len(all_concepts)} 个概念和 {len(all_relations)} 个关系")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python llm_concept_extractor.py <segments.json文件> <输出目录>")
        sys.exit(1)
    
    segments_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    process_all_segments(segments_file, output_dir)
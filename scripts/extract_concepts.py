# coding: utf-8
import os
import sys
import json
import re

def extract_concepts(segments):
    """从文本段落中提取法相概念"""
    concepts = []
    categories = {}
    
    # 解析章节结构，提取概念
    for segment in segments:
        # 提取五位七十五法相关内容
        if "五位七十五法" in segment or "列五位七十五法" in segment:
            concept = {
                "name": "五位七十五法",
                "category": "核心概念",
                "description": "阿毗达摩系统将一切法分为五大类七十五种"
            }
            concepts.append(concept)
            
        # 提取色法相关内容
        if re.search(r'色法|1\.1', segment):
            concept = {
                "name": "色法",
                "category": "五位",
                "description": "物质现象相关的概念，共十一种"
            }
            concepts.append(concept)
            categories["色法"] = True
            
        # 提取心法相关内容
        if re.search(r'心法|1\.2', segment):
            concept = {
                "name": "心法",
                "category": "五位",
                "description": "心识相关的概念，共一种"
            }
            concepts.append(concept)
            categories["心法"] = True
            
        # 提取心所法相关内容
        if re.search(r'心所法|1\.3', segment):
            concept = {
                "name": "心所法",
                "category": "五位",
                "description": "心的作用相关的概念，共五十一种"
            }
            concepts.append(concept)
            categories["心所法"] = True
            
        # 提取心不相应行法相关内容
        if re.search(r'心不相应行法|1\.4', segment):
            concept = {
                "name": "心不相应行法",
                "category": "五位",
                "description": "非心性但与心相关的概念，共十四种"
            }
            concepts.append(concept)
            categories["心不相应行法"] = True
            
        # 检测细分概念（根据标点和数字模式来识别）
        match = re.search(r'(\d+\.\d+\.\d+)\.(\d+)([^\d]+)', segment)
        if match:
            section = match.group(1)
            subsection = match.group(2)
            name = match.group(3).strip()
            
            # 根据章节号确定类别
            category = ""
            if section.startswith("1.1"):
                category = "色法"
            elif section.startswith("1.2"):
                category = "心法"
            elif section.startswith("1.3"):
                category = "心所法"
            elif section.startswith("1.4"):
                category = "心不相应行法"
            
            if category and name:
                concept = {
                    "name": name,
                    "category": category,
                    "section": f"{section}.{subsection}",
                    "description": f"{name}是{category}的一种"
                }
                concepts.append(concept)
    
    # 去重，合并同名概念
    unique_concepts = {}
    for concept in concepts:
        name = concept["name"]
        if name not in unique_concepts:
            unique_concepts[name] = concept
    
    return list(unique_concepts.values())

def process_segments(segments_file, output_dir):
    """处理所有文本段落并提取概念"""
    with open(segments_file, "r", encoding="utf-8") as f:
        segments = json.load(f)
    
    print(f"处理 {len(segments)} 个文本段落")
    concepts = extract_concepts(segments)
    
    # 保存结果
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "concepts.json"), "w", encoding="utf-8") as f:
        json.dump(concepts, f, ensure_ascii=False, indent=2)
    
    print(f"共提取出 {len(concepts)} 个唯一概念")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python extract_concepts.py <segments.json文件> <输出目录>")
        sys.exit(1)
    segments_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    process_segments(segments_file, output_dir)
    print("概念提取完成!")

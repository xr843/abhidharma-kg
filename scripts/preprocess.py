# -*- coding: utf-8 -*-

import os
import json
import sys
import re
from typing import List, Dict

def load_text(file_path: str) -> str:
    """加载文本文件内容，确保UTF-8编码"""
    with open(file_path, "r", encoding="utf-8-sig") as f:  # 使用utf-8-sig处理可能的BOM
        return f.read()

def segment_text(text: str) -> List[Dict]:
    """
    改进的文本分段函数，保留层次结构
    返回包含标题层级和内容的字典列表
    """
    lines = text.strip().split('\n')
    segments = []
    current_segment = []
    current_level = 0
    current_title = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 检测标题行 (如 "1.1色法")
        title_match = re.match(r'^(\d+(\.\d+)*)\s+(.+)$', line)
        if title_match:
            if current_segment:
                segments.append({
                    "title": current_title,
                    "level": current_level,
                    "content": " ".join(current_segment)
                })
                current_segment = []
                
            # 计算标题层级 (如 "1.2.3" → 3)
            current_level = len(title_match.group(1).split('.'))
            current_title = title_match.group(3)
            continue
            
        # 普通内容行
        current_segment.append(line)
    
    # 添加最后一个段落
    if current_segment:
        segments.append({
            "title": current_title, 
            "level": current_level,
            "content": " ".join(current_segment)
        })
        
    return segments

def save_segments(segments: List[Dict], output_dir: str) -> None:
    """保存分段结果到JSON文件"""
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "segments.json")
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(segments, f, ensure_ascii=False, indent=2)
    
    print(f"保存 {len(segments)} 个段落到 {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python preprocess.py <输入文件> <输出目录>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    print(f"处理文件: {input_file}")
    text = load_text(input_file)
    segments = segment_text(text)
    save_segments(segments, output_dir)
    print("处理完成")

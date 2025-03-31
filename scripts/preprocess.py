# coding: utf-8
import os
import sys
import re
import json

def load_text(filepath):
    """加载原始文本文件"""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def segment_text(text):
    """将文本分段为段落"""
    # 按行分割文本
    lines = text.strip().split('\n')
    
    # 过滤掉空行和仅包含数字的行
    segments = []
    for line in lines:
        line = line.strip()
        if line and not re.match(r'^\d+$', line):
            segments.append(line)
    
    return segments

def save_segments(segments, output_dir):
    """将分段保存到文件"""
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "segments.json"), "w", encoding="utf-8") as f:
        json.dump(segments, f, ensure_ascii=False, indent=2)
    print(f"保存了 {len(segments)} 个文本段落")

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
    print("预处理完成!")

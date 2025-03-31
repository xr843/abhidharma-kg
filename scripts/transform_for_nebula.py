# coding: utf-8
import os
import sys
import json
import hashlib

def generate_id(text):
    """生成稳定的ID，用于NebulaGraph的VID"""
    return hashlib.md5(text.encode("utf-8")).hexdigest()[:30]

def transform_concepts(concepts_file, output_dir):
    """将概念转换为NebulaGraph格式"""
    with open(concepts_file, "r", encoding="utf-8") as f:
        concepts = json.load(f)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 节点文件
    with open(os.path.join(output_dir, "concepts.csv"), "w", encoding="utf-8") as f:
        f.write("concept_id,name,description,category\n")
        for concept in concepts:
            concept_id = generate_id(concept["name"])
            name = concept["name"].replace(",", "，")  # 避免CSV分隔符冲突
            description = concept.get("description", "").replace(",", "，")
            category = concept.get("category", "").replace(",", "，")
            f.write(f"{concept_id},{name},{description},{category}\n")
    
    # 生成关系数据
    with open(os.path.join(output_dir, "belongs_to_relations.csv"), "w", encoding="utf-8") as f:
        f.write("src_id,dst_id,description\n")
        
        # 创建类别映射
        category_concepts = {}
        for concept in concepts:
            if concept.get("category") == "五位":
                category_concepts[concept["name"]] = generate_id(concept["name"])
        
        # 创建属于关系
        for concept in concepts:
            category = concept.get("category")
            if category in category_concepts and concept["name"] != category:
                src_id = generate_id(concept["name"])
                dst_id = category_concepts[category]
                description = f"属于{category}"
                f.write(f"{src_id},{dst_id},{description}\n")
    
    # 生成层次关系
    with open(os.path.join(output_dir, "hierarchy_relations.csv"), "w", encoding="utf-8") as f:
        f.write("src_id,dst_id,relation_type,weight\n")
        
        # 核心概念与五位的关系
        core_id = None
        for concept in concepts:
            if concept.get("name") == "五位七十五法":
                core_id = generate_id(concept["name"])
        
        if core_id:
            for concept in concepts:
                if concept.get("category") == "五位":
                    dst_id = generate_id(concept["name"])
                    f.write(f"{core_id},{dst_id},包含,5\n")
    
    print(f"已将 {len(concepts)} 个概念转换为NebulaGraph格式")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python transform_for_nebula.py <concepts.json文件> <输出目录>")
        sys.exit(1)
    concepts_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    transform_concepts(concepts_file, output_dir)
    print("数据转换完成!")

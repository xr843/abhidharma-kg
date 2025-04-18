# coding: utf-8
import os
import sys
import json
import hashlib

def generate_id(text):
    """生成唯一ID适用于NebulaGraph的VID"""
    return hashlib.md5(text.encode("utf-8")).hexdigest()[:30]

def transform_concepts_and_relations(concepts_file, relations_file, output_dir):
    """将概念和关系转换为NebulaGraph格式"""
    # 读取概念数据
    with open(concepts_file, "r", encoding="utf-8") as f:
        concepts = json.load(f)
    
    # 读取关系数据
    with open(relations_file, "r", encoding="utf-8") as f:
        relations = json.load(f)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 构建概念ID映射
    concept_id_map = {}
    for concept in concepts:
        if "id" in concept and "name" in concept:
            concept_id = generate_id(concept["name"])
            concept_id_map[concept["id"]] = concept_id
    
    # 输出概念CSV
    with open(os.path.join(output_dir, "concepts.csv"), "w", encoding="utf-8") as f:
        f.write("concept_id,name,description,category,pali,sanskrit\n")
        for concept in concepts:
            concept_id = generate_id(concept["name"])
            name = concept["name"].replace(",", "，")  # 避免CSV格式冲突
            description = concept.get("description", "").replace(",", "，")
            category = concept.get("category", "").replace(",", "，")
            pali = concept.get("pali", "").replace(",", "，")
            sanskrit = concept.get("sanskrit", "").replace(",", "，")
            f.write(f"{concept_id},{name},{description},{category},{pali},{sanskrit}\n")
    
    # 输出关系CSV
    with open(os.path.join(output_dir, "relations.csv"), "w", encoding="utf-8") as f:
        f.write("src_id,dst_id,type,description\n")
        for relation in relations:
            if "source" in relation and "target" in relation:
                # 使用映射获取NebulaGraph格式的ID
                source_id = concept_id_map.get(relation["source"])
                target_id = concept_id_map.get(relation["target"])
                
                if source_id and target_id:
                    relation_type = relation.get("type", "关联").replace(",", "，")
                    description = relation.get("description", "").replace(",", "，")
                    f.write(f"{source_id},{target_id},{relation_type},{description}\n")
    
    # 创建类别关系CSV（从概念的category属性生成）
    with open(os.path.join(output_dir, "category_relations.csv"), "w", encoding="utf-8") as f:
        f.write("src_id,dst_id,type\n")
        
        # 构建类别映射
        categories = {}
        for concept in concepts:
            if concept.get("category"):
                category = concept["category"]
                if category not in categories:
                    # 为每个类别创建一个节点ID
                    categories[category] = generate_id("category_" + category)
        
        # 创建概念到类别的关系
        for concept in concepts:
            if concept.get("category") and concept["category"] in categories:
                src_id = generate_id(concept["name"])
                dst_id = categories[concept["category"]]
                f.write(f"{src_id},{dst_id},属于\n")
    
    print(f"已将 {len(concepts)} 个概念和 {len(relations)} 个关系转换为NebulaGraph格式")

def transform_concepts(concepts_file, output_dir):
    """转换概念到NebulaGraph格式（兼容旧接口）"""
    # 读取概念数据
    with open(concepts_file, "r", encoding="utf-8") as f:
        concepts = json.load(f)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 输出概念CSV
    with open(os.path.join(output_dir, "concepts.csv"), "w", encoding="utf-8") as f:
        f.write("concept_id,name,description,category\n")
        for concept in concepts:
            concept_id = generate_id(concept["name"])
            name = concept["name"].replace(",", "，")  # 避免CSV格式冲突
            description = concept.get("description", "").replace(",", "，")
            category = concept.get("category", "").replace(",", "，")
            f.write(f"{concept_id},{name},{description},{category}\n")
    
    # 输出类别关系
    with open(os.path.join(output_dir, "belongs_to_relations.csv"), "w", encoding="utf-8") as f:
        f.write("src_id,dst_id,description\n")
        
        # 构建类别概念
        category_concepts = {}
        for concept in concepts:
            if concept.get("category") == "类别":
                category_concepts[concept["name"]] = generate_id(concept["name"])
        
        # 构建从属关系
        for concept in concepts:
            category = concept.get("category")
            if category in category_concepts and concept["name"] != category:
                src_id = generate_id(concept["name"])
                dst_id = category_concepts[category]
                description = f"属于{category}"
                f.write(f"{src_id},{dst_id},{description}\n")
    
    # 输出层次关系
    with open(os.path.join(output_dir, "hierarchy_relations.csv"), "w", encoding="utf-8") as f:
        f.write("src_id,dst_id,relation_type,weight\n")
        
        # 查找核心概念的关系
        core_id = None
        for concept in concepts:
            if concept.get("name") == "阿毗达摩七十五法":
                core_id = generate_id(concept["name"])
        
        if core_id:
            for concept in concepts:
                if concept.get("category") == "类别":
                    dst_id = generate_id(concept["name"])
                    f.write(f"{core_id},{dst_id},包含,5\n")
    
    print(f"已将 {len(concepts)} 个概念转换为NebulaGraph格式")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python transform_for_nebula.py <概念JSON文件> <输出目录> [关系JSON文件]")
        sys.exit(1)
    
    concepts_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    if len(sys.argv) > 3:
        relations_file = sys.argv[3]
        transform_concepts_and_relations(concepts_file, relations_file, output_dir)
    else:
        transform_concepts(concepts_file, output_dir)
    
    print("转换完成!")

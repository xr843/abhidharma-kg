# coding: utf-8
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import time
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 文件图存储实现
class FileGraphStore:
    def __init__(self, data_dir="./graph_data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.concepts_file = os.path.join(data_dir, "concepts.json")
        self.relations_file = os.path.join(data_dir, "relations.json")
        self.load_data()
    
    def load_data(self):
        # 加载概念
        if os.path.exists(self.concepts_file):
            with open(self.concepts_file, "r", encoding="utf-8") as f:
                self.concepts = json.load(f)
        else:
            self.concepts = []
        
        # 加载关系
        if os.path.exists(self.relations_file):
            with open(self.relations_file, "r", encoding="utf-8") as f:
                self.relations = json.load(f)
        else:
            self.relations = []
    
    def save_data(self):
        # 保存概念
        with open(self.concepts_file, "w", encoding="utf-8") as f:
            json.dump(self.concepts, f, ensure_ascii=False, indent=2)
        
        # 保存关系
        with open(self.relations_file, "w", encoding="utf-8") as f:
            json.dump(self.relations, f, ensure_ascii=False, indent=2)
    
    def get_concepts(self, category=None):
        if category:
            return [c for c in self.concepts if c.get("category") == category]
        return self.concepts
    
    def get_concept(self, concept_id):
        for concept in self.concepts:
            if concept.get("id") == concept_id:
                # 查找相关概念
                concept_copy = concept.copy()
                concept_copy["relations"] = []
                
                for relation in self.relations:
                    if relation.get("src_id") == concept_id:
                        target_id = relation.get("dst_id")
                        target_concept = None
                        for c in self.concepts:
                            if c.get("id") == target_id:
                                target_concept = c
                                break
                        
                        if target_concept:
                            concept_copy["relations"].append({
                                "type": relation.get("relation_type"),
                                "target_id": target_concept.get("id"),
                                "target_name": target_concept.get("name"),
                                "target_category": target_concept.get("category")
                            })
                
                return concept_copy
        return None
    
    def get_categories(self):
        categories = set()
        for concept in self.concepts:
            category = concept.get("category")
            if category:
                categories.add(category)
        return list(categories)
    
    # 添加基本的示例数据
    def add_sample_data(self):
        if not self.concepts:  # 只在没有数据时添加示例数据
            self.concepts = [
                {"id": "concept1", "name": "五位七十五法", "description": "阿毗达摩系统将一切法分为五大类七十五种", "category": "核心概念"},
                {"id": "concept2", "name": "色法", "description": "物质现象相关的概念，共十一种", "category": "五位"},
                {"id": "concept3", "name": "心法", "description": "心识相关的概念，共一种", "category": "五位"},
                {"id": "concept4", "name": "心所法", "description": "心的作用相关的概念，共五十一种", "category": "五位"},
                {"id": "concept5", "name": "心不相应行法", "description": "非心性但与心相关的概念，共十四种", "category": "五位"},
                {"id": "concept6", "name": "无为法", "description": "不生不灭的概念，共三种", "category": "五位"},
                {"id": "concept7", "name": "眼", "description": "眼根，色法之一", "category": "色法"},
                {"id": "concept8", "name": "耳", "description": "耳根，色法之一", "category": "色法"},
                {"id": "concept9", "name": "心王", "description": "心识本体", "category": "心法"}
            ]
            
            self.relations = [
                {"src_id": "concept1", "dst_id": "concept2", "relation_type": "包含", "weight": 5},
                {"src_id": "concept1", "dst_id": "concept3", "relation_type": "包含", "weight": 5},
                {"src_id": "concept1", "dst_id": "concept4", "relation_type": "包含", "weight": 5},
                {"src_id": "concept1", "dst_id": "concept5", "relation_type": "包含", "weight": 5},
                {"src_id": "concept1", "dst_id": "concept6", "relation_type": "包含", "weight": 5},
                {"src_id": "concept2", "dst_id": "concept7", "relation_type": "包含", "weight": 3},
                {"src_id": "concept2", "dst_id": "concept8", "relation_type": "包含", "weight": 3},
                {"src_id": "concept3", "dst_id": "concept9", "relation_type": "包含", "weight": 3}
            ]
            
            self.save_data()

# 初始化文件图存储
graph_store = FileGraphStore()
# 添加示例数据
graph_store.add_sample_data()

@app.route('/api/health')
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "ok", 
        "timestamp": time.time(), 
        "message": "API服务正常运行"
    })

@app.route('/api/concepts')
def get_concepts():
    """获取所有概念接口"""
    category = request.args.get('category', '')
    return jsonify(graph_store.get_concepts(category))

@app.route('/api/concept/<concept_id>')
def get_concept(concept_id):
    """获取特定概念的详细信息接口"""
    concept = graph_store.get_concept(concept_id)
    if concept:
        return jsonify(concept)
    return jsonify({"id": concept_id, "name": "未知概念", "description": "未找到该概念", "category": "未知", "relations": []}), 404

@app.route('/api/categories')
def get_categories():
    """获取所有分类接口"""
    return jsonify(graph_store.get_categories())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
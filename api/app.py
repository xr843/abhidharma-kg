# coding: utf-8
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import time
from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# NebulaGraph连接设置
NEBULA_HOST = os.getenv("NEBULA_HOST", "localhost")
NEBULA_PORT = int(os.getenv("NEBULA_PORT", "9669"))
NEBULA_USER = os.getenv("NEBULA_USER", "root")
NEBULA_PASSWORD = os.getenv("NEBULA_PASSWORD", "nebula")
SPACE_NAME = "abhidharma"

# 连接池
connection_pool = None

def init_connection_pool():
    """初始化NebulaGraph连接池"""
    global connection_pool
    config = Config()
    config.max_connection_pool_size = 10
    
    connection_pool = ConnectionPool()
    try:
        connection_pool.init([NEBULA_HOST], NEBULA_PORT, config)
        print(f"成功初始化连接池 - 连接到 {NEBULA_HOST}:{NEBULA_PORT}")
        return True
    except Exception as e:
        print(f"连接失败: {e}")
        return False

def get_session():
    """获取NebulaGraph会话"""
    global connection_pool
    if connection_pool is None:
        if not init_connection_pool():
            return None
    
    try:
        session = connection_pool.get_session(NEBULA_USER, NEBULA_PASSWORD)
        # 使用指定空间
        result = session.execute(f"USE {SPACE_NAME};")
        if not result.is_succeeded():
            print(f"使用空间失败: {result.error_msg()}")
            session.release()
            return None
        return session
    except Exception as e:
        print(f"获取会话失败: {e}")
        return None

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
    
    try:
        session = get_session()
        if session is None:
            # 数据库连接失败，返回示例数据
            print("数据库连接失败，返回示例数据")
            sample_concepts = [
                {"id": "sample1", "name": "色法", "description": "物质现象相关的概念，共十一种", "category": "五位"},
                {"id": "sample2", "name": "心法", "description": "心识相关的概念，共一种", "category": "五位"},
                {"id": "sample3", "name": "心所法", "description": "心的作用相关的概念，共五十一种", "category": "五位"},
                {"id": "sample4", "name": "心不相应行法", "description": "非心性但与心相关的概念，共十四种", "category": "五位"},
                {"id": "sample5", "name": "无为法", "description": "不生不灭的概念，共三种", "category": "五位"}
            ]
            
            if category:
                return jsonify([c for c in sample_concepts if c["category"] == category])
            return jsonify(sample_concepts)
            
        # 以下是原来的数据库查询逻辑
        query = "MATCH (v:Concept)"
        if category:
            query += f" WHERE v.category == '{category}'"
        query += " RETURN v LIMIT 100"
        
        result = session.execute(query)
        if not result.is_succeeded():
            return jsonify({"error": result.error_msg()}), 500
        
        concepts = []
        result_set = result.result_set()
        for record in result_set:
            node_val = record.values()[0].as_node()
            concept = {
                "id": node_val.vid.as_string(),
                "name": node_val.properties.get("name").as_string(),
                "description": node_val.properties.get("description").as_string(),
                "category": node_val.properties.get("category").as_string()
            }
            concepts.append(concept)
        
        return jsonify(concepts)
    except Exception as e:
        print(f"获取概念时出错: {e}")
        # 出错时返回示例数据
        return jsonify([
            {"id": "error1", "name": "色法", "description": "物质现象相关的概念，共十一种", "category": "五位"},
            {"id": "error2", "name": "心法", "description": "心识相关的概念，共一种", "category": "五位"}
        ])

@app.route('/api/concept/<concept_id>')
def get_concept(concept_id):
    """获取特定概念的详细信息接口"""
    try:
        session = get_session()
        if session is None:
            # 数据库连接失败，返回示例数据
            print("数据库连接失败，返回示例概念详情")
            sample_concepts = {
                "sample1": {
                    "id": "sample1",
                    "name": "色法",
                    "description": "物质现象相关的概念，共十一种",
                    "category": "五位",
                    "relations": [
                        {"type": "CONTAINS", "target_id": "sample6", "target_name": "眼", "target_category": "色法"}
                    ]
                },
                "sample2": {
                    "id": "sample2",
                    "name": "心法",
                    "description": "心识相关的概念，共一种",
                    "category": "五位",
                    "relations": []
                }
            }
            
            if concept_id in sample_concepts:
                return jsonify(sample_concepts[concept_id])
            else:
                return jsonify({"id": concept_id, "name": "示例概念", "description": "这是一个示例概念", "category": "示例", "relations": []})
            
        # 以下是原来的数据库查询逻辑
        # ...原代码保持不变...
    except Exception as e:
        print(f"获取概念详情时出错: {e}")
        return jsonify({
            "id": concept_id,
            "name": "示例概念",
            "description": "这是一个示例概念（出错时返回）",
            "category": "示例",
            "relations": []
        })

@app.route('/api/categories')
def get_categories():
    """获取所有分类接口"""
    try:
        session = get_session()
        if session is None:
            # 数据库连接失败，返回示例分类
            print("数据库连接失败，返回示例分类")
            return jsonify(["五位", "色法", "心法", "心所法", "心不相应行法", "无为法"])
            
        # 以下是原来的数据库查询逻辑
        # ...原代码保持不变...
    except Exception as e:
        print(f"获取分类时出错: {e}")
        return jsonify(["五位", "示例分类"])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
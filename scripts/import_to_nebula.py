# coding: utf-8
import os
import sys
import time
from nebula3.gclient.net import ConnectionPool
from nebula3.Config import Config
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# NebulaGraph连接设置
NEBULA_HOST = os.getenv("NEBULA_HOST", "localhost")
NEBULA_PORT = int(os.getenv("NEBULA_PORT", "9669"))
NEBULA_USER = os.getenv("NEBULA_USER", "root")
NEBULA_PASSWORD = os.getenv("NEBULA_PASSWORD", "nebula")

def connect_nebula():
    """连接到NebulaGraph数据库"""
    config = Config()
    config.max_connection_pool_size = 10
    
    # 初始化连接池
    connection_pool = ConnectionPool()
    try:
        connection_pool.init([NEBULA_HOST], NEBULA_PORT, config)
        print(f"成功初始化连接池 - 连接到 {NEBULA_HOST}:{NEBULA_PORT}")
        return connection_pool
    except Exception as e:
        print(f"连接失败: {e}")
        return None

def execute_query(session, query):
    """执行NebulaGraph查询"""
    try:
        result = session.execute(query)
        if not result.is_succeeded():
            print(f"查询执行失败: {result.error_msg()}")
            return False
        return True
    except Exception as e:
        print(f"查询执行异常: {e}")
        return False

def import_schema(session):
    """导入Schema定义"""
    schema_file = "../schema/nebula_schema.ngql"
    if not os.path.exists(schema_file):
        print(f"错误: Schema文件不存在 - {schema_file}")
        return False
    
    print("正在导入Schema...")
    with open(schema_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 分割文件中的语句执行
    statements = content.split(';')
    for stmt in statements:
        stmt = stmt.strip()
        if stmt and not stmt.startswith('#'):
            if "CREATE SPACE" in stmt:
                # 执行创建空间语句
                if not execute_query(session, stmt + ';'):
                    print("创建空间失败")
                    continue
                
                # 等待空间创建完成
                print("等待空间创建完成...")
                time.sleep(10)
                
                # 使用空间
                use_space = "USE abhidharma;"
                if not execute_query(session, use_space):
                    print("使用空间失败")
                    return False
            else:
                # 执行其他语句
                if not execute_query(session, stmt + ';'):
                    print(f"执行语句失败: {stmt}")
                    continue
    
    print("Schema导入完成")
    return True

def import_data(session, data_dir):
    """导入节点和边数据"""
    # 导入概念节点
    concepts_file = os.path.join(data_dir, "concepts.csv")
    if not os.path.exists(concepts_file):
        print(f"错误: 节点文件不存在 - {concepts_file}")
        return False
    
    print("正在导入概念节点...")
    with open(concepts_file, 'r', encoding='utf-8') as f:
        # 读取标题行
        header = next(f).strip().split(',')
        has_pali = 'pali' in header
        has_sanskrit = 'sanskrit' in header
        
        for line in f:
            try:
                parts = line.strip().split(',')
                if len(parts) >= 4:
                    vid = parts[0]
                    name = parts[1].replace('"', '\\"')
                    description = parts[2].replace('"', '\\"')
                    category = parts[3].replace('"', '\\"')
                    
                    # 检查是否有梵语和巴利语字段
                    pali = parts[4].replace('"', '\\"') if has_pali and len(parts) > 4 else ""
                    sanskrit = parts[5].replace('"', '\\"') if has_sanskrit and len(parts) > 5 else ""
                    
                    if has_pali and has_sanskrit:
                        query = f'INSERT VERTEX Concept(name, description, category, pali, sanskrit) VALUES "{vid}":("{name}", "{description}", "{category}", "{pali}", "{sanskrit}");'
                    else:
                        query = f'INSERT VERTEX Concept(name, description, category) VALUES "{vid}":("{name}", "{description}", "{category}");'
                    
                    if not execute_query(session, query):
                        print(f"插入节点失败: {vid}")
                        continue
            except Exception as e:
                print(f"处理节点出错: {e}")
                continue
    
    # 导入概念关系
    relations_file = os.path.join(data_dir, "relations.csv")
    if os.path.exists(relations_file):
        print("正在导入概念关系...")
        with open(relations_file, 'r', encoding='utf-8') as f:
            # 跳过标题行
            next(f)
            for line in f:
                try:
                    parts = line.strip().split(',')
                    if len(parts) >= 4:
                        src_id = parts[0]
                        dst_id = parts[1]
                        relation_type = parts[2].replace('"', '\\"')
                        description = parts[3].replace('"', '\\"')
                        
                        query = f'INSERT EDGE RELATES_TO(relation_type, description) VALUES "{src_id}" -> "{dst_id}":("{relation_type}", "{description}");'
                        if not execute_query(session, query):
                            print(f"插入概念关系失败: {src_id} -> {dst_id}")
                            continue
                except Exception as e:
                    print(f"处理概念关系出错: {e}")
                    continue
    
    # 导入类别关系
    category_file = os.path.join(data_dir, "category_relations.csv")
    if os.path.exists(category_file):
        print("正在导入类别关系...")
        with open(category_file, 'r', encoding='utf-8') as f:
            # 跳过标题行
            next(f)
            for line in f:
                try:
                    parts = line.strip().split(',')
                    if len(parts) >= 3:
                        src_id = parts[0]
                        dst_id = parts[1]
                        relation_type = parts[2].replace('"', '\\"')
                        
                        query = f'INSERT EDGE BELONGS_TO(description) VALUES "{src_id}" -> "{dst_id}":("{relation_type}");'
                        if not execute_query(session, query):
                            print(f"插入类别关系失败: {src_id} -> {dst_id}")
                            continue
                except Exception as e:
                    print(f"处理类别关系出错: {e}")
                    continue
                    
    # 导入从属关系(兼容旧格式)
    relations_file = os.path.join(data_dir, "belongs_to_relations.csv")
    if os.path.exists(relations_file):
        print("正在导入从属关系(兼容模式)...")
        with open(relations_file, 'r', encoding='utf-8') as f:
            # 跳过标题行
            next(f)
            for line in f:
                try:
                    parts = line.strip().split(',')
                    if len(parts) >= 3:
                        src_id = parts[0]
                        dst_id = parts[1]
                        description = parts[2].replace('"', '\\"')
                        
                        query = f'INSERT EDGE BELONGS_TO(description) VALUES "{src_id}" -> "{dst_id}":("{description}");'
                        if not execute_query(session, query):
                            print(f"插入从属关系失败: {src_id} -> {dst_id}")
                            continue
                except Exception as e:
                    print(f"处理从属关系出错: {e}")
                    continue
    
    # 导入层次关系(兼容旧格式)
    hierarchy_file = os.path.join(data_dir, "hierarchy_relations.csv")
    if os.path.exists(hierarchy_file):
        print("正在导入层次关系(兼容模式)...")
        with open(hierarchy_file, 'r', encoding='utf-8') as f:
            # 跳过标题行
            next(f)
            for line in f:
                try:
                    parts = line.strip().split(',')
                    if len(parts) >= 4:
                        src_id = parts[0]
                        dst_id = parts[1]
                        relation_type = parts[2].replace('"', '\\"')
                        weight = int(parts[3])
                        
                        query = f'INSERT EDGE RELATES_TO(relation_type, weight) VALUES "{src_id}" -> "{dst_id}":("{relation_type}", {weight});'
                        if not execute_query(session, query):
                            print(f"插入层次关系失败: {src_id} -> {dst_id}")
                            continue
                except Exception as e:
                    print(f"处理层次关系出错: {e}")
                    continue
    
    print("数据导入完成")
    return True

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python import_to_nebula.py <数据目录>")
        sys.exit(1)
    
    data_dir = sys.argv[1]
    if not os.path.exists(data_dir):
        print(f"错误: 数据目录不存在 - {data_dir}")
        sys.exit(1)
    
    # 连接NebulaGraph
    connection_pool = connect_nebula()
    if connection_pool is None:
        sys.exit(1)
    
    try:
        # 获取会话
        session = connection_pool.get_session(NEBULA_USER, NEBULA_PASSWORD)
        
        # 导入Schema
        if not import_schema(session):
            print("Schema导入失败")
            sys.exit(1)
        
        # 导入数据
        if not import_data(session, data_dir):
            print("数据导入失败")
            sys.exit(1)
        
        print("所有数据成功导入到NebulaGraph")
    except Exception as e:
        print(f"导入过程中发生错误: {e}")
        sys.exit(1)
    finally:
        # 释放资源
        if connection_pool is not None:
            connection_pool.close()

if __name__ == "__main__":
    main()

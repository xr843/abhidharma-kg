# llm_concept_extractor.py
import os
import json
import requests
import time
import sys
import logging
from dotenv import load_dotenv
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("concept_extraction.log"),
        logging.StreamHandler()
    ]
)

# 加载环境变量
load_dotenv()

# DeepSeek API配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.3))
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", 4000))

# 检查API密钥
if not DEEPSEEK_API_KEY:
    logging.error("ERROR: DeepSeek API密钥未设置，请在.env文件中配置DEEPSEEK_API_KEY")
    sys.exit(1)

def extract_concepts_with_llm(text_segment):
    """使用DeepSeek从文本段落中提取阿毗达摩法相概念"""
    prompt = f"""
    你是一位精通佛教阿毗达摩的专家，请分析以下《法宗原》文本：
    
    {text_segment}
    
    请识别以下内容：
    1. 法相概念：包括心所法、色法、心王法等
    2. 概念属性：定义、分类、特征
    3. 概念关系：相生、相克、包含等
    
    返回格式要求：
    {{
        "concepts": [
            {{
                "id": "唯一ID(英文)",
                "name": "概念名(中文)",
                "description": "详细定义",
                "category": "类别",
                "pali": "巴利语名(可选)",
                "sanskrit": "梵语名(可选)"
            }}
        ],
        "relations": [
            {{
                "source": "源概念ID",
                "target": "目标概念ID", 
                "type": "关系类型",
                "description": "关系说明"
            }}
        ]
    }}
    
    注意：
    1. 确保每个概念的ID是唯一的英文标识符(例如：rupa, vedana, samjna)
    2. 确保关系的source和target字段使用对应概念的ID值
    3. 严格按照JSON格式返回，不要添加任何额外的说明文字
    """
    
    response = call_deepseek_api(prompt)
    return parse_deepseek_response(response)

def call_deepseek_api(prompt):
    """调用DeepSeek API"""
    headers = {
        "Content-Type": "application/json", 
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    data = {
        "model": DEEPSEEK_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS
    }
    
    max_retries = 5
    retry_delay = 3  # 秒
    
    for attempt in range(max_retries):
        try:
            logging.info(f"调用API (尝试 {attempt + 1}/{max_retries})")
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=120  # 延长超时时间至120秒
            )
            
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', retry_delay * (2 ** attempt)))
                logging.warning(f"API限流 (429)，等待 {retry_after} 秒后重试")
                time.sleep(retry_after)
                continue
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logging.error(f"API请求失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
            
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)  # 指数退避
                logging.info(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                logging.error(f"段落处理最终失败，放弃此段落")
                return None

def parse_deepseek_response(response):
    """解析DeepSeek API的响应"""
    if not response:
        return {"concepts": [], "relations": []}
    
    try:
        # DeepSeek返回格式
        content = response['choices'][0]['message']['content']
        
        # 提取JSON部分（处理可能存在的markdown代码块）
        json_str = content
        if '```json' in content:
            json_str = content.split('```json')[1].split('```')[0]
        elif '```' in content:
            json_str = content.split('```')[1].split('```')[0]
        
        # 清理可能导致解析错误的前导和尾随空白    
        json_str = json_str.strip()
        
        # 尝试解析JSON
        result = json.loads(json_str)
        
        # 验证必要字段
        if not all(k in result for k in ["concepts", "relations"]):
            logging.warning("响应缺少必要字段 (concepts/relations)")
            # 添加缺少的字段
            if "concepts" not in result:
                result["concepts"] = []
            if "relations" not in result:
                result["relations"] = []
                
        # 验证概念和关系数量
        logging.info(f"成功解析响应: {len(result['concepts'])} 个概念, {len(result['relations'])} 个关系")    
        return result
        
    except Exception as e:
        logging.error(f"解析DeepSeek响应失败: {str(e)}")
        if response:
            logging.debug(f"原始响应: {response}")
        return {"concepts": [], "relations": []}

def process_all_segments(segments_file, output_dir, start_index=0):
    """处理所有文本段落，提取概念和关系"""
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 检查是否有现有进度文件
    progress_file = os.path.join(output_dir, "progress.json")
    checkpoint_file = os.path.join(output_dir, "checkpoint.json")
    
    # 尝试从检查点恢复
    all_concepts = {}
    all_relations = []
    
    if os.path.exists(checkpoint_file) and start_index == 0:
        try:
            logging.info(f"尝试从检查点恢复...")
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
                all_concepts = checkpoint.get("concepts", {})
                all_relations = checkpoint.get("relations", [])
                start_index = checkpoint.get("last_processed_index", 0) + 1
                logging.info(f"成功从检查点恢复，从段落 {start_index+1} 开始继续处理")
        except Exception as e:
            logging.warning(f"无法从检查点恢复: {str(e)}，将从头开始处理")
            start_index = 0
            all_concepts = {}
            all_relations = []
    
    # 加载文本段落
    try:
        with open(segments_file, 'r', encoding='utf-8') as f:
            segments = json.load(f)
    except Exception as e:
        logging.error(f"无法加载段落文件 {segments_file}: {str(e)}")
        sys.exit(1)
    
    total_segments = len(segments)
    logging.info(f"开始处理，共 {total_segments} 个段落，从段落 {start_index+1} 开始")
    
    # 统计信息
    start_time = time.time()
    success_count = 0
    error_count = 0
    empty_result_count = 0
    
    # 处理每个段落
    for i in range(start_index, total_segments):
        segment = segments[i]
        logging.info(f"处理段落 {i+1}/{total_segments}")
        
        try:
            # 调用大模型提取概念和关系
            result = extract_concepts_with_llm(segment)
            
            # 处理结果
            if result and (result.get("concepts") or result.get("relations")):
                # 合并概念（避免重复）
                for concept in result.get("concepts", []):
                    concept_id = concept.get("id")
                    if not concept_id:
                        logging.warning(f"概念缺少ID，跳过：{concept}")
                        continue
                        
                    if concept_id not in all_concepts:
                        all_concepts[concept_id] = concept
                    else:
                        # 如果已存在，可能需要合并某些字段
                        logging.info(f"合并重复概念: {concept_id}")
                
                # 添加关系
                new_relations = result.get("relations", [])
                for relation in new_relations:
                    # 验证source和target都存在
                    if not relation.get("source") or not relation.get("target"):
                        logging.warning(f"关系缺少source或target，跳过：{relation}")
                        continue
                    all_relations.append(relation)
                
                success_count += 1
                logging.info(f"成功提取: +{len(result.get('concepts', []))} 概念, +{len(new_relations)} 关系")
            else:
                empty_result_count += 1
                logging.warning(f"段落 {i+1} 未提取出概念或关系")
            
            # 每10个段落保存一次进度
            if (i + 1) % 10 == 0 or i == total_segments - 1:
                save_checkpoint(checkpoint_file, all_concepts, all_relations, i)
                
            # 避免API限流，动态调整等待时间
            wait_time = 3 if success_count > error_count else 5
            logging.info(f"等待 {wait_time} 秒后继续...")
            time.sleep(wait_time)
            
        except Exception as e:
            error_count += 1
            logging.error(f"处理段落 {i+1} 时发生错误: {str(e)}")
            # 如果连续出错，增加等待时间
            if error_count > 2:
                logging.warning("连续多次出错，等待30秒后继续...")
                time.sleep(30)
    
    # 完成处理，保存最终结果
    save_final_results(output_dir, all_concepts, all_relations)
    
    # 记录统计信息
    elapsed_time = time.time() - start_time
    logging.info(f"处理完成！用时 {elapsed_time:.2f} 秒")
    logging.info(f"统计信息:")
    logging.info(f"  - 总段落数: {total_segments}")
    logging.info(f"  - 成功处理: {success_count}")
    logging.info(f"  - 空结果数: {empty_result_count}")
    logging.info(f"  - 错误数: {error_count}")
    logging.info(f"  - 提取概念: {len(all_concepts)}")
    logging.info(f"  - 提取关系: {len(all_relations)}")

def save_checkpoint(checkpoint_file, concepts, relations, last_index):
    """保存检查点"""
    try:
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump({
                "concepts": concepts,
                "relations": relations,
                "last_processed_index": last_index,
                "timestamp": datetime.now().isoformat()
            }, f, ensure_ascii=False)
        logging.info(f"检查点已保存 (处理至段落 {last_index+1})")
    except Exception as e:
        logging.error(f"保存检查点失败: {str(e)}")

def save_final_results(output_dir, concepts_dict, relations_list):
    """保存最终结果"""
    try:
        # 保存概念
        concepts_file = os.path.join(output_dir, "concepts.json")
        with open(concepts_file, 'w', encoding='utf-8') as f:
            json.dump(list(concepts_dict.values()), f, ensure_ascii=False, indent=2)
        
        # 保存关系
        relations_file = os.path.join(output_dir, "relations.json")
        with open(relations_file, 'w', encoding='utf-8') as f:
            json.dump(relations_list, f, ensure_ascii=False, indent=2)
        
        logging.info(f"结果已保存:")
        logging.info(f"  - 概念文件: {concepts_file} ({len(concepts_dict)} 个概念)")
        logging.info(f"  - 关系文件: {relations_file} ({len(relations_list)} 个关系)")
    except Exception as e:
        logging.error(f"保存结果文件失败: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python llm_concept_extractor.py <segments.json文件> <输出目录> [--start-index=N] [--verbose]")
        sys.exit(1)
    
    segments_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    # 解析可选参数
    start_index = 0
    verbose = False
    
    for arg in sys.argv[3:]:
        if arg.startswith("--start-index="):
            try:
                start_index = int(arg.split("=")[1])
            except:
                logging.error(f"无效的起始索引: {arg}")
                sys.exit(1)
        elif arg == "--verbose":
            verbose = True
            logging.getLogger().setLevel(logging.DEBUG)
    
    logging.info(f"======== 阿毗达摩法相概念提取 ========")
    logging.info(f"开始时间: {datetime.now().isoformat()}")
    logging.info(f"输入文件: {segments_file}")
    logging.info(f"输出目录: {output_dir}")
    logging.info(f"起始段落: {start_index+1}")
    logging.info(f"======================================")
    
    try:
        process_all_segments(segments_file, output_dir, start_index)
    except KeyboardInterrupt:
        logging.warning("用户中断处理")
        sys.exit(130)
    except Exception as e:
        logging.critical(f"处理过程中发生严重错误: {str(e)}", exc_info=True)
        sys.exit(1)

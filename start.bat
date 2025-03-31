@echo off
echo 安装依赖并准备环境...
pip install -r requirements.txt

echo 预处理《法宗原》文本...
if not exist processed_data\segments mkdir processed_data\segments
python scripts\preprocess.py data\fazongyuan.txt processed_data\segments

echo 提取法相概念...
if not exist processed_data\concepts mkdir processed_data\concepts
python scripts\extract_concepts.py processed_data\segments\segments.json processed_data\concepts

echo 转换数据为NebulaGraph格式...
if not exist processed_data\nebula mkdir processed_data\nebula
python scripts\transform_for_nebula.py processed_data\concepts\concepts.json processed_data\nebula

echo 启动API服务...
start cmd /k "cd api && python app.py"
timeout /t 3

echo 打开前端页面...
start "" "frontend\index.html"

echo 所有服务已启动！
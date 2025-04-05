@echo off
echo 安装基本依赖...
pip install flask flask-cors python-dotenv requests

echo 创建必要的目录...
mkdir processed_data\segments
mkdir processed_data\concepts
mkdir processed_data\nebula

echo 启动API服务...
start cmd /k "cd api && python app.py"
timeout /t 3

echo 打开前端页面...
start "" "frontend\index.html"

echo 所有服务已启动！
@echo off
echo 启动API服务...
set FLASK_APP=app.py
set FLASK_ENV=development
python -m flask run --host=0.0.0.0 --port=5000
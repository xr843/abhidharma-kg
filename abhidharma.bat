@echo off
setlocal enabledelayedexpansion

echo ===== 阿毗达摩法相知识图谱项目 =====

if "%1"=="" (
    echo 用法: abhidharma.bat [命令]
    echo 可用命令:
    echo   setup        - 安装依赖并准备环境
    echo   preprocess   - 预处理《法宗原》文本
    echo   extract      - 提取法相概念
    echo   transform    - 转换数据为NebulaGraph格式
    echo   import       - 导入数据到NebulaGraph
    echo   start-api    - 启动API服务
    echo   start-web    - 打开前端页面
    echo   start-all    - 启动所有服务
    echo   full-pipeline - 执行完整处理流程
    goto :eof
)

if "%1"=="setup" (
    echo 安装依赖并准备环境...
    pip install -r requirements.txt
    goto :eof
)

if "%1"=="preprocess" (
    echo 预处理《法宗原》文本...
    if not exist processed_data\segments mkdir processed_data\segments
    python scripts\preprocess.py data\fazongyuan.txt processed_data\segments
    goto :eof
)

if "%1"=="extract" (
    echo 提取法相概念...
    if not exist processed_data\concepts mkdir processed_data\concepts
    python scripts\extract_concepts.py processed_data\segments\segments.json processed_data\concepts
    goto :eof
)

if "%1"=="transform" (
    echo 转换数据为NebulaGraph格式...
    if not exist processed_data\nebula mkdir processed_data\nebula
    python scripts\transform_for_nebula.py processed_data\concepts\concepts.json processed_data\nebula
    goto :eof
)

if "%1"=="import" (
    echo 导入数据到NebulaGraph...
    python scripts\import_to_nebula.py processed_data\nebula
    goto :eof
)

if "%1"=="start-api" (
    echo 启动API服务...
    cd api
    python app.py
    cd ..
    goto :eof
)

if "%1"=="start-web" (
    echo 打开前端页面...
    start "" "frontend\index.html"
    goto :eof
)

if "%1"=="start-all" (
    echo 启动所有服务...
    start cmd /k "%~dp0abhidharma.bat start-api"
    timeout /t 3
    start "" "frontend\index.html"
    goto :eof
)

if "%1"=="full-pipeline" (
    echo 执行完整处理流程...
    call %~dp0abhidharma.bat preprocess
    if %ERRORLEVEL% neq 0 goto :error
    
    call %~dp0abhidharma.bat extract
    if %ERRORLEVEL% neq 0 goto :error
    
    call %~dp0abhidharma.bat transform
    if %ERRORLEVEL% neq 0 goto :error
    
    call %~dp0abhidharma.bat import
    if %ERRORLEVEL% neq 0 goto :error
    
    echo 完整处理流程执行完毕！
    goto :eof
)

echo 未知命令: %1
goto :eof

:error
echo 处理过程中出现错误，流程已中止。
exit /b 1
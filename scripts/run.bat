@echo off
setlocal enabledelayedexpansion

set INPUT_FILE=..\data\fazongyuan.txt
set SEGMENT_DIR=..\processed_data\segments
set CONCEPT_DIR=..\processed_data\concepts
set NEBULA_DIR=..\processed_data\nebula

echo ===== 阿毗达摩法相知识图谱处理流程 =====

echo 1. 预处理文本
if not exist %SEGMENT_DIR% mkdir %SEGMENT_DIR%
python preprocess.py %INPUT_FILE% %SEGMENT_DIR%
if %ERRORLEVEL% neq 0 (
    echo 错误: 预处理失败
    exit /b 1
)

echo 2. 提取法相概念
if not exist %CONCEPT_DIR% mkdir %CONCEPT_DIR%
python extract_concepts.py %SEGMENT_DIR%\segments.json %CONCEPT_DIR%
if %ERRORLEVEL% neq 0 (
    echo 错误: 概念提取失败
    exit /b 1
)

echo 3. 转换为NebulaGraph格式
if not exist %NEBULA_DIR% mkdir %NEBULA_DIR%
python transform_for_nebula.py %CONCEPT_DIR%\concepts.json %NEBULA_DIR%
if %ERRORLEVEL% neq 0 (
    echo 错误: 数据转换失败
    exit /b 1
)

echo ===== 处理完成 =====
echo 结果文件位于:
echo - 文本分段: %SEGMENT_DIR%\segments.json
echo - 概念数据: %CONCEPT_DIR%\concepts.json
echo - NebulaGraph节点: %NEBULA_DIR%\concepts.csv
echo - NebulaGraph关系: %NEBULA_DIR%\belongs_to_relations.csv, %NEBULA_DIR%\hierarchy_relations.csv
echo 4. 导入数据到NebulaGraph（可选）
set /p IMPORT=是否要导入数据到NebulaGraph？(y/n): 
if /i "%IMPORT%"=="y" (
    python import_to_nebula.py %NEBULA_DIR%
    if %ERRORLEVEL% neq 0 (
        echo 错误: 数据导入失败
        exit /b 1
    )
)
pause

# 阿毗达摩法相知识图谱项目开发纲要

## 项目概述

阿毗达摩法相知识图谱项目旨在构建佛教阿毗达摩法相体系的知识图谱，通过先进的自然语言处理和图数据库技术，将佛教经典文献中的概念和关系进行结构化提取与可视化呈现，为佛学研究和学习提供数字化工具。

## 系统架构

本项目采用模块化设计，包含以下核心组件：

1. **文本预处理模块**
2. **概念提取模块**
3. **数据转换模块**
4. **数据库导入模块**
5. **可视化展示模块**

## 技术栈

- **大语言模型**：DeepSeek API
- **图数据库**：NebulaGraph
- **开发语言**：Python
- **部署环境**：Docker

## 功能模块详解

### 1. 文本预处理模块

**主要功能**：

- 将《七十五法名目》《法宗原》等佛教经典文本进行分段处理
- 对文本进行清洗和标准化
- 准备适合大语言模型处理的文本片段

### 2. 概念提取模块

**主要功能**：

- 调用DeepSeek API提取法相概念和关系
- 处理API响应，解析JSON格式数据
- 保存提取结果到中间文件

**优化亮点**：

- 详细日志记录系统，便于问题定位
- 断点续传功能，支持长时间任务中断后继续执行
- 指数退避重试机制，应对API调用失败情况
- 健壮的错误处理和超时控制
- 灵活的JSON解析功能，适应不同格式的API响应

### 3. 数据转换模块

**主要功能**：

- 将概念和关系转换为NebulaGraph所需的CSV格式
- 处理概念属性和关系类型

**优化亮点**：

- 支持更丰富的概念属性（梵语、巴利语、藏文等字段）
- 类别关系自动生成功能
- 新旧数据格式兼容处理
- 数据验证和清洗

### 4. 数据库导入模块

**主要功能**：

- 将CSV格式数据导入NebulaGraph数据库
- 执行数据库操作和查询

**优化亮点**：

- 支持新增概念属性和关系类型
- 优化CSV解析逻辑
- 改进错误处理机制
- 批量导入支持

### 5. 数据库Schema设计

**主要内容**：

- 概念节点结构设计，包含中文、梵语、巴利语、藏文等字段
- 关系边定义，包含类型、描述等属性
- 索引设计，优化查询性能

**优化亮点**：

- 扩展字段支持多语言表达
- 优化关系边定义
- 保持向后兼容性

## 项目流程

1. **数据准备阶段**

   - 收集和整理阿毗达摩相关经典文献
   - 使用预处理模块进行文本分段
2. **概念提取阶段**

   - 调用DeepSeek API
   - 提取法相概念和关系
   - 保存中间结果
3. **数据转换阶段**

   - 转换数据
   - 生成符合NebulaGraph要求的CSV文件
4. **数据导入阶段**

   - 执行导入操作
   - 验证数据完整性
5. **可视化展示阶段**

   - 使用NebulaGraph Studio或自定义前端进行可视化
   - 支持图谱浏览和查询

## 部署指南

1. 确保已安装Docker Desktop和NebulaGraph Studio
2. 按顺序执行各模块脚本
3. 通过NebulaGraph Studio界面进行可视化和查询

## 后续优化方向

1. **增强概念提取精度**：优化大语言模型提示工程
2. **扩展多语言支持**：增加更多语言版本的法相术语
3. **改进可视化界面**：提供更直观的图谱浏览体验
4. **优化查询性能**：完善数据库索引和查询策略
5. **拓展文献范围**：纳入更多阿毗达摩典籍

## 预期成果

1. 完整的阿毗达摩法相知识图谱数据库
2. 用户友好的图谱浏览和查询界面
3. 支持多语言的法相术语检索系统
4. 可扩展的知识图谱构建流程

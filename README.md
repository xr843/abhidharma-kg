# 阿毗达摩法相知识图谱

基于《法宗原》构建的阿毗达摩法相知识图谱，使用NebulaGraph存储和查询，提供可视化界面和分析功能。

## 项目简介

阿毗达摩法相知识图谱旨在将佛教阿毗达摩系统中的"五位七十五法"概念结构化为图形数据库，便于检索、可视化和分析。本项目基于《法宗原》经典文本，使用大语言模型API进行法相概念提取，并构建基于NebulaGraph的图数据库系统。

项目特点：
* 基于NebulaGraph构建的知识图谱数据库
* 使用大型语言模型API进行法相概念自动抽取
* 直观的概念浏览和关系可视化界面
* 强大的图谱分析和查询功能
* 完全容器化部署，方便安装和使用

## 系统架构

系统由以下主要组件组成：
* **数据处理模块**：文本预处理和概念抽取
* **NebulaGraph数据库**：存储和管理图数据
* **API服务**：提供数据访问接口
* **前端应用**：用户界面和可视化

## 功能特性

* **概念浏览**：按类型浏览和搜索法相概念
* **关系查询**：查找概念之间的直接和间接关系
* **图谱可视化**：动态、交互式的图谱展示
* **统计分析**：概念分布和关系统计图表
* **五位七十五法分析**：阿毗达摩基本分类体系分析
* **五蕴分析**：佛教对人类经验的基本分类分析
* **因果链分析**：探索概念之间的因果关系链

## 安装与使用

### 前提条件
* Docker及Docker Compose
* Python 3.9+（用于数据处理）
* LLM API密钥（Gemini或Qwen）

### 快速开始

1. 克隆仓库

```bash
git clone https://github.com/yourusername/abhidharma-kg.git
cd abhidharma-kg
```

2. 设置环境变量

```bash
cp .env.example .env
# 编辑.env文件，设置API密钥
```

3. 运行主控脚本

```bash
# 安装依赖并准备环境
./abhidharma.sh setup

# 执行完整处理流程
./abhidharma.sh full-pipeline
```

4. 访问应用
   * 前端界面: http://localhost
   * API文档: http://localhost:5000/api/health
   * NebulaGraph Studio: http://localhost:7001

### 手动步骤

如果您想逐步执行处理流程，可以使用以下命令：

```bash
# 预处理《法宗原》文本
./abhidharma.sh preprocess

# 提取法相概念
./abhidharma.sh extract

# 转换数据为NebulaGraph格式
./abhidharma.sh transform

# 构建Docker镜像
./abhidharma.sh build

# 启动服务
./abhidharma.sh start

# 导入数据
./abhidharma.sh import
```

## 数据模型

系统基于阿毗达摩的"五位七十五法"构建，主要概念类型包括：
* **色法**：物质现象相关的概念（11种）
* **心法**：心识相关的概念（1种）
* **心所法**：心的作用相关的概念（46种）
* **心不相应行法**：非心性但与心相关的概念（14种）
* **无为法**：不生不灭的概念（3种）

关系类型包括但不限于：组成、包含、对立、依赖、导致等。

## 项目目录结构

```
abhidharma-kg/
├── api/               # API服务
│   ├── database/      # 数据库连接
│   └── routes/        # API路由
├── data/              # 原始数据
├── docker/            # Docker配置
├── frontend/          # React前端应用
│   ├── src/           # 源代码
│   └── public/        # 静态资源
├── processed_data/    # 处理后的数据
│   ├── concepts/      # 概念数据
│   ├── relations/     # 关系数据
│   ├── segments/      # 文本分段
│   └── nebula/        # NebulaGraph导入数据
├── schema/            # NebulaGraph模式定义
├── scripts/           # 处理脚本
└── utils/             # 工具函数
```

## 技术栈

* **后端**：Python, Flask, NebulaGraph
* **前端**：React, Chakra UI, D3.js
* **数据处理**：Python, Pandas, LLM API
* **部署**：Docker, Docker Compose

## 常见问题

**Q: 如何修改NebulaGraph的连接配置？**  
A: 编辑`.env`文件中的`NEBULA_*`相关参数，然后重启服务。

**Q: 如何备份知识图谱数据？**  
A: 使用`docker-compose exec metad nebula-backup`命令进行备份。

**Q: 前端无法连接到API服务？**  
A: 确保API服务已正常启动，并检查前端环境变量`REACT_APP_API_URL`设置是否正确。如果您使用了自定义的网络设置，可能需要更新此配置。

**Q: 如何添加新的法相概念？**  
A: 您可以通过两种方式添加：1）更新`data/fazongyuan.txt`文件后重新运行整个流程；2）直接使用NebulaGraph控制台手动添加概念和关系。

**Q: 为什么某些概念之间没有关系连接？**  
A: 这可能是由于原始文本中未明确描述这些关系，或者概念抽取过程未能捕获这些关系。您可以通过NebulaGraph控制台手动添加关系。

## 许可证

本项目采用MIT许可证 - 详情请查看LICENSE文件。

## 致谢

* 感谢所有为本项目做出贡献的开发者
* 感谢NebulaGraph团队提供的强大图数据库系统
* 感谢Google和阿里云提供的大语言模型API
* 感谢佛教经典《法宗原》的作者和译者
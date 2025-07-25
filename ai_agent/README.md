# Qrent AI Agent

基于知识库的智能租房推荐系统，拆分自原始的 `agent/Agent.py` 文件。

## 项目结构

```
ai_agent/
├── Agent/
│   ├── agent.py          # 核心Agent逻辑类
│   └── rag.py           # RAG向量存储构建
├── ui/
│   └── streamlit.py     # Streamlit用户界面
├── database/
│   └── faiss_index/     # FAISS向量存储
├── documents/
│   ├── Qrent攻略.pdf
│   └── Qrent澳洲租房最全全流程攻略.pdf
├── run_streamlit.py     # Streamlit启动脚本
├── test_agent.py        # Agent功能测试脚本
└── README.md           # 本文件
```

## 功能特性

### 核心功能

- **智能问答**: 基于知识库回答租房相关问题
- **向量检索**: 使用 FAISS 进行语义搜索
- **数据库集成**: 从 PostgreSQL 数据库获取房源信息
- **多轮对话**: 支持上下文感知的对话历史
- **优先级分析**: 智能分析用户租房优先级

### 技术栈

- **AI 模型**: Qwen (通过 DashScope API)
- **向量存储**: FAISS
- **嵌入模型**: Qwen3-Embedding-0.6B
- **数据库**: PostgreSQL
- **UI 框架**: Streamlit
- **文档处理**: LangChain

## 安装和配置

### 1. 环境要求

```bash
Python 3.8+
pip install -r requirements.txt
```

### 2. 环境变量配置

创建 `.env` 文件并设置以下变量：

```env
# 数据库配置
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=your_db_port
DB_NAME=your_db_name

# API配置
API_KEY_POINT=your_dashscope_api_key
```

### 3. 向量存储构建

首次使用前需要构建向量存储：

```bash
cd Agent
python rag.py
```

这将：

- 加载 PDF 文档
- 创建文档嵌入
- 保存 FAISS 索引到 `database/faiss_index/`

## 使用方法

### 1. 测试 Agent 功能

```bash
python test_agent.py
```

### 2. 启动 Streamlit 应用

```bash
python run_streamlit.py
```

或者直接运行：

```bash
streamlit run ui/streamlit.py
```

### 3. 编程接口使用

```python
from Agent.agent import QrentAgent

# 创建Agent实例
agent = QrentAgent()

# 处理查询
result = agent.process_query("我想找一个两室一厅的房子，预算500澳元每周")

# 获取结果
print(result['answer'])
print(result['db_data'])
print(result['vector_context'])
```

## API 接口

### QrentAgent 类

#### 主要方法

- `process_query(query: str, top_k: int = 5) -> dict`

  - 处理用户查询
  - 返回包含答案、检索上下文和数据库数据的字典

- `clear_history()`

  - 清空对话历史

- `get_history() -> list`
  - 获取对话历史

#### 返回格式

```python
{
    "query": "用户查询",
    "vector_context": "检索到的相关上下文",
    "db_data": [...],  # 相关房源数据
    "answer": "AI生成的回答",
    "history": [...]   # 对话历史
}
```

## 文件说明

### Agent/agent.py

核心 Agent 类，包含：

- 数据库连接管理
- 向量存储加载
- AI 模型调用
- 查询处理逻辑

### Agent/rag.py

RAG 系统构建，包含：

- 文档加载和处理
- 向量存储构建
- 错误处理和调试

### ui/streamlit.py

Streamlit 用户界面，包含：

- 交互式聊天界面
- 检索信息显示
- 对话历史管理
- 参数配置

## 故障排除

### 常见问题

1. **Agent 初始化失败**

   - 检查数据库连接配置
   - 确认环境变量设置正确
   - 验证向量存储文件存在

2. **向量存储加载失败**

   - 运行 `python Agent/rag.py` 重新构建
   - 检查 PDF 文档是否存在
   - 确认嵌入模型下载成功

3. **API 调用失败**
   - 验证 `API_KEY_POINT` 设置正确
   - 检查网络连接
   - 确认 API 配额充足

### 调试模式

在代码中添加调试信息：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 开发说明

### 代码结构

- **分离关注点**: UI 和业务逻辑分离
- **模块化设计**: 每个组件独立可测试
- **错误处理**: 完善的异常处理机制
- **类型提示**: 提供类型注解便于维护

### 扩展指南

1. **添加新的文档类型**: 修改 `Agent/rag.py` 中的文档加载逻辑
2. **自定义 UI 组件**: 在 `ui/streamlit.py` 中添加新的界面元素
3. **集成新的 AI 模型**: 修改 `Agent/agent.py` 中的模型调用逻辑

## 许可证

本项目遵循 MIT 许可证。

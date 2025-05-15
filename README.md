# 淘宝智能导购助手

本项目旨在开发一个淘宝智能导购助手，后端基于 FastAPI 和 LangGraph 构建，前端将以浏览器插件的形式，在淘宝商品页为用户提供选购手机等商品的辅助决策。

## 核心功能

1.  **信息展示窗口**：
    *   分析商品核心参数。
    *   商品评论情感分析与真实性评估。
    *   搜索相似商品并进行对比。
2.  **对话窗口**：
    *   基于LLM的智能问答和商品推荐。

## 技术选型

*   **后端框架**: FastAPI
*   **AI Agent**: LangGraph, LangChain
*   **数据模型与配置**: Pydantic, Pydantic-Settings
*   **LLM**: 阿里云千问模型 (通过 `langchain-openai` 兼容层)
*   **商品数据API**: 万邦淘宝API (支持模拟 `mock` 和真实 `prod` 模式)
*   **异步处理**: `asyncio`

## 环境要求

*   Python 3.10+
*   依赖库见 `requirements.txt`

## 项目结构

```
.
├── app/                  # 应用核心代码
│   ├── core/             # 核心逻辑 (Agent, API处理, 模拟数据等)
│   ├── main.py           # FastAPI 应用入口
│   └── config.py         # 应用配置管理
├── docs/                 # API 文档 (如万邦API文档)
├── .env.example          # 环境变量示例文件 (需复制为 .env)
├── README.md             # 项目说明
└── requirements.txt      # Python 依赖
```

## 安装与配置

1.  **克隆项目** (如果尚未克隆)

2.  **创建并激活虚拟环境**:
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/macOS
    source venv/bin/activate
    ```

3.  **安装依赖**:
    ```bash
    pip install -r requirements.txt
    ```
    (如果网络慢，可以指定国内镜像源，如：`pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/`)

4.  **配置环境变量**:
    复制 `.env.example` (如果提供了) 或手动创建 `.env` 文件在项目根目录下，并填入以下内容：
    ```env
    WANBANG_APP_KEY="YOUR_WANBANG_APP_KEY"         # 万邦API Key
    WANBANG_APP_SECRET="YOUR_WANBANG_APP_SECRET"   # 万邦API Secret
    QIANWEN_API_KEY="YOUR_QIANWEN_API_KEY"         # 千问API Key
    QIANWEN_API_BASE="YOUR_QIANWEN_API_BASE_URL"   # 千问API Base URL (例如：https://dashscope.aliyuncs.com/api/v1)
    RUN_MODE="mock"                                # 运行模式: "mock" 使用模拟数据, "prod" 使用真实API
    ```
    请将 `"YOUR_..."` 替换为你的实际配置。

## 运行应用

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
*   `--reload`: 开发模式下，代码更改后自动重启。
*   访问 `http://localhost:8000/docs` 查看 FastAPI 自动生成的 API 文档 (如果定义了HTTP路由)。
*   访问 `http://localhost:8000/agent_chat/` (或你在 `main.py` 中定义的 WebSocket 路径) 与 Agent 进行交互。

## 运行测试

```bash
python app.test_agent.py
```

## 未来展望 (浏览器插件)

前端将作为浏览器插件，与此后端服务进行通信，实现淘宝商品页面侧边栏助手功能。 
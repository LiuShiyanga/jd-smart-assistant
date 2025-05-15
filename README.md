# 京东智能导购助手

基于 FastAPI 和 LangGraph 的智能导购系统，帮助用户分析商品信息，提供购买建议。

## 环境要求

- Python 3.10
- 其他依赖见 requirements.txt

## 安装

1. 创建虚拟环境：
```bash
python -m venv venv
```

2. 激活虚拟环境：
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

3. 安装依赖：
```bash
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

## 运行

```bash
uvicorn app.main:app --reload
```

访问 http://localhost:8000/docs 查看API文档

## 功能

1. 商品详情分析
2. 商品评论分析
3. 相似商品对比
4. 智能问答 
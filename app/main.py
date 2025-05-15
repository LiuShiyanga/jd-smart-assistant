"""
FastAPI 应用主入口
"""
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from app.core.agent import ProductAnalysisAgent
from app.config import RUN_MODE
import json
import asyncio
from typing import Dict, Any

app = FastAPI(
    title="京东智能导购助手",
    description="基于大语言模型的智能导购系统",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建 Agent 实例
agent = ProductAnalysisAgent()

@app.get("/")
async def root():
    """健康检查接口"""
    return {"status": "ok", "mode": RUN_MODE}

@app.get("/api/analyze/{item_id}")
async def analyze_product(item_id: str):
    """商品分析接口（SSE）"""
    async def event_generator():
        try:
            # 运行 Agent
            result = await agent.run(item_id)
            
            # 发送商品信息
            if result["item_info"]:
                yield {
                    "event": "item_info",
                    "data": json.dumps(result["item_info"])
                }
            
            # 发送商品分析
            if "product" in result["analysis"]:
                yield {
                    "event": "product_analysis",
                    "data": result["analysis"]["product"]
                }
            
            # 发送评论分析
            if "comments" in result["analysis"]:
                yield {
                    "event": "comments_analysis",
                    "data": result["analysis"]["comments"]
                }
            
            # 发送相似商品比较
            if "comparison" in result["analysis"]:
                yield {
                    "event": "similar_items",
                    "data": json.dumps({
                        "items": result["similar_items"],
                        "analysis": result["analysis"]["comparison"]
                    })
                }
            
            # 发送错误信息（如果有）
            if result["error"]:
                yield {
                    "event": "error",
                    "data": result["error"]
                }
            
        except Exception as e:
            yield {
                "event": "error",
                "data": str(e)
            }
    
    return EventSourceResponse(event_generator())

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 聊天接口"""
    await websocket.accept()
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 运行 Agent
            result = await agent.run(message["item_id"])
            
            # 发送分析结果
            await websocket.send_json({
                "type": "analysis",
                "data": result["analysis"]
            })
            
            # 发送相似商品
            if result["similar_items"]:
                await websocket.send_json({
                    "type": "similar_items",
                    "data": result["similar_items"]
                })
            
            # 发送错误信息（如果有）
            if result["error"]:
                await websocket.send_json({
                    "type": "error",
                    "data": result["error"]
                })
                
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "data": str(e)
        })
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
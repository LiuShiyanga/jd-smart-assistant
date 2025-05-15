"""
测试商品分析 Agent
"""
import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.core.agent import ProductAnalysisAgent

async def test_agent():
    """测试商品分析 Agent"""
    # 创建 Agent 实例
    agent = ProductAnalysisAgent()
    
    # 测试商品ID
    item_id = "123456789"  # 使用模拟数据中的商品ID
    
    try:
        # 运行分析
        result = await agent.run(item_id)
        
        # 打印分析结果
        print("\n=== 商品信息 ===")
        item_info = result.get('item_info', {}) # 安全获取 item_info，默认为空字典
        print(f"商品名称: {item_info.get('title', 'N/A')}")
        print(f"价格: {item_info.get('price', 'N/A')}元")
        print(f"品牌: {item_info.get('brand', 'N/A')}")
        print(f"销量: {item_info.get('total_sold', 'N/A')}")
        
        print("\n=== 商品分析 ===")
        print(result['analysis'].get('product', '无分析结果'))
        
        print("\n=== 评论分析 ===")
        print(result['analysis'].get('comments', '无评论分析'))
        
        print("\n=== 相似商品对比 ===")
        print(result['analysis'].get('comparison', '无对比结果'))
        
        if result['error']:
            print(f"\n错误信息: {result['error']}")
            
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")

if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_agent()) 
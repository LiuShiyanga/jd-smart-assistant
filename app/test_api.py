import asyncio
from app.core.taobao_api import TaobaoApi

async def test_api():
    api = TaobaoApi()
    
    # 测试商品详情获取
    print("测试商品详情获取...")
    item_info = await api.item_get("652874751412")  # 使用示例中的商品ID
    print("商品详情:", item_info)
    
    # 测试评论获取
    print("\n测试评论获取...")
    reviews = await api.item_review(
        item_id="600530677643",
        page=1,
        sort="",
        is_sku=False
    )
    print("商品评论:", reviews)
    
    # 测试商品搜索
    print("\n测试商品搜索...")
    search_results = await api.item_search(
        keyword="女装",
        price_range=(0, 0),
        page=1,
        sort="",
        cat="0",
        discount_only="",
        seller_info="no",
        nick="",
        ppath="",
        imgid="",
        filter=""
    )
    print("搜索结果:", search_results)

if __name__ == "__main__":
    asyncio.run(test_api()) 
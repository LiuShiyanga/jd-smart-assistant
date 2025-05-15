import asyncio
from app.core.mock_data import MockTaobaoApi

async def test_item_get():
    """测试获取商品详情"""
    api = MockTaobaoApi()
    item_info = await api.item_get("123456789")
    
    assert item_info["num_iid"] == "123456789"
    assert item_info["title"] == "iPhone 15 Pro Max 256GB 原色钛金属"
    assert item_info["price"] == 9999.00
    assert len(item_info["props"]) == 8
    assert item_info["shop_info"]["shop_name"] == "Apple官方旗舰店"
    print("商品详情测试通过！")

async def test_item_review():
    """测试获取商品评论"""
    api = MockTaobaoApi()
    comments = await api.item_review("123456789")
    
    assert len(comments) == 3
    assert comments[0]["rate_content"] == "手机非常好用，外观设计很漂亮，拍照效果很棒，电池续航也很给力。"
    assert comments[0]["display_user_nick"] == "张***"
    print("商品评论测试通过！")

async def test_item_search():
    """测试商品搜索"""
    api = MockTaobaoApi()
    similar_items = await api.item_search(keyword="iPhone")
    
    assert len(similar_items) == 2
    assert similar_items[0]["title"] == "iPhone 15 Pro 256GB 原色钛金属"
    assert similar_items[0]["price"] == 8999.00
    assert similar_items[1]["title"] == "iPhone 15 Plus 256GB 蓝色"
    assert similar_items[1]["price"] == 7999.00
    print("商品搜索测试通过！")

async def run_all_tests():
    """运行所有测试"""
    try:
        await test_item_get()
        await test_item_review()
        await test_item_search()
        print("\n所有测试通过！")
    except AssertionError as e:
        print(f"\n测试失败：{str(e)}")
    except Exception as e:
        print(f"\n测试出错：{str(e)}")

if __name__ == "__main__":
    asyncio.run(run_all_tests()) 
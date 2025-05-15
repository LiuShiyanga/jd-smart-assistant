"""
模拟手机商品数据
"""
from typing import Optional

MOCK_PHONE_DATA = {
    "item_info": {
        "num_iid": "123456789",
        "title": "iPhone 15 Pro Max 256GB 原色钛金属",
        "desc_short": "A17 Pro芯片，4800万像素主摄，钛金属边框",
        "brand": "Apple",
        "price": 9999.00,
        "total_price": 9999.00,
        "orginal_price": 10999.00,
        "nick": "Apple官方旗舰店",
        "num": 1000,
        "min_num": 1,
        "detail_url": "https://item.taobao.com/item.htm?id=123456789",
        "pic_url": "https://img.alicdn.com/imgextra/i4/123456789/O1CN01xxx_1.jpg",
        "cid": 1512,
        "props": [
            {"name": "品牌", "value": "Apple"},
            {"name": "型号", "value": "iPhone 15 Pro Max"},
            {"name": "颜色", "value": "原色钛金属"},
            {"name": "存储容量", "value": "256GB"},
            {"name": "屏幕尺寸", "value": "6.7英寸"},
            {"name": "处理器", "value": "A17 Pro"},
            {"name": "电池容量", "value": "4422mAh"},
            {"name": "摄像头", "value": "4800万像素主摄"}
        ],
        "total_sold": 5000,
        "shop_info": {
            "shop_name": "Apple官方旗舰店",
            "shop_url": "https://shop.taobao.com/shop/view_shop.htm?shop_id=123456789",
            "shop_id": "123456789"
        }
    },
    "comments": [
        {
            "rate_content": "手机非常好用，外观设计很漂亮，拍照效果很棒，电池续航也很给力。",
            "rate_date": "2024-02-26 10:30:00",
            "display_user_nick": "张***",
            "auction_sku": "颜色:原色钛金属;存储容量:256GB"
        },
        {
            "rate_content": "物流很快，包装完好，手机做工精细，系统流畅，很满意的一次购物。",
            "rate_date": "2024-02-25 15:20:00",
            "display_user_nick": "李***",
            "auction_sku": "颜色:原色钛金属;存储容量:256GB"
        },
        {
            "rate_content": "手机很轻，手感很好，拍照效果确实不错，就是价格有点贵。",
            "rate_date": "2024-02-24 09:15:00",
            "display_user_nick": "王***",
            "auction_sku": "颜色:原色钛金属;存储容量:256GB"
        }
    ],
    "similar_items": [
        {
            "title": "iPhone 15 Pro 256GB 原色钛金属",
            "price": 8999.00,
            "pic_url": "https://img.alicdn.com/imgextra/i4/123456789/O1CN01xxx_2.jpg",
            "detail_url": "https://item.taobao.com/item.htm?id=123456790",
            "sales": 3000
        },
        {
            "title": "iPhone 15 Plus 256GB 蓝色",
            "price": 7999.00,
            "pic_url": "https://img.alicdn.com/imgextra/i4/123456789/O1CN01xxx_3.jpg",
            "detail_url": "https://item.taobao.com/item.htm?id=123456791",
            "sales": 2000
        }
    ]
}

class MockTaobaoApi:
    """模拟淘宝API"""
    
    async def item_get(self, item_id: str) -> dict:
        """获取商品详情"""
        return MOCK_PHONE_DATA["item_info"]
    
    async def item_review(self, item_id: str, page: int = 1, sort: str = "", is_sku: bool = False) -> list:
        """获取商品评论"""
        return MOCK_PHONE_DATA["comments"]
    
    async def item_search(self, 
                         keyword: Optional[str] = None,
                         price_range: Optional[tuple] = None,
                         page: int = 1,
                         sort: str = "",
                         cat: str = "0",
                         discount_only: str = "",
                         seller_info: str = "no",
                         nick: str = "",
                         ppath: str = "",
                         imgid: str = "",
                         filter: str = "") -> list:
        """搜索商品"""
        return MOCK_PHONE_DATA["similar_items"] 
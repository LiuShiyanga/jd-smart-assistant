from typing import Dict, List, Optional
import httpx
import time
import hashlib
import json
from app.config import settings

class TaobaoApi:
    def __init__(self):
        self.base_url = "https://api-gw.onebound.cn/taobao"
        self.app_key = settings.WANBANG_APP_KEY
        self.app_secret = settings.WANBANG_APP_SECRET
        self.headers = {
            "Accept-Encoding": "gzip",
            "Connection": "close"
        }

    async def item_get(self, item_id: str) -> Dict:
        """获取商品详情"""
        params = {
            "key": self.app_key,
            "secret": self.app_secret,
            "num_iid": item_id,
            "cache": "yes",
            "result_type": "json",
            "lang": "cn"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/item_get/",
                    params=params,
                    headers=self.headers
                )
                data = response.json()
                
                if "item" in data:
                    item_data = data["item"]
                    return {
                        "num_iid": item_data.get("num_iid", ""),
                        "title": item_data.get("title", ""),
                        "desc_short": item_data.get("desc_short", ""),
                        "brand": item_data.get("brand", ""),
                        "price": float(item_data.get("price", 0)),
                        "total_price": float(item_data.get("total_price", 0)),
                        "suggestive_price": float(item_data.get("suggestive_price", 0)),
                        "orginal_price": float(item_data.get("orginal_price", 0)),
                        "nick": item_data.get("nick", ""),
                        "num": int(item_data.get("num", 0)),
                        "min_num": int(item_data.get("min_num", 0)),
                        "detail_url": item_data.get("detail_url", ""),
                        "pic_url": item_data.get("pic_url", ""),
                        "cid": int(item_data.get("cid", 0)),
                        "props": item_data.get("props", []),
                        "props_name": item_data.get("props_name", ""),
                        "total_sold": int(item_data.get("total_sold", 0)),
                        "skus": item_data.get("skus", []),
                        "seller_info": item_data.get("seller_info", {}),
                        "shop_info": {
                            "shop_name": item_data.get("nick", ""),
                            "shop_url": item_data.get("seller_info", {}).get("zhuy", ""),
                            "shop_id": item_data.get("shop_id", "")
                        }
                    }
                else:
                    print(f"API返回错误: {data.get('error', '未知错误')}")
                    return {}
        except Exception as e:
            print(f"API调用错误: {str(e)}")
            return {}

    async def item_review(self, item_id: str, page: int = 1, sort: str = "", is_sku: bool = False) -> List[Dict]:
        """获取商品评论"""
        params = {
            "key": self.app_key,
            "secret": self.app_secret,
            "num_iid": item_id,
            "page": page,
            "sort": sort,
            "is_sku": "true" if is_sku else "false",
            "cache": "yes",
            "result_type": "json",
            "lang": "cn"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/item_review/",
                    params=params,
                    headers=self.headers
                )
                data = response.json()
                
                if "items" in data and "item" in data["items"]:
                    return data["items"]["item"]
                else:
                    print(f"API返回错误: {data.get('error', '未知错误')}")
                    return []
        except Exception as e:
            print(f"API调用错误: {str(e)}")
            return []

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
                         filter: str = "") -> List[Dict]:
        """搜索商品"""
        params = {
            "key": self.app_key,
            "secret": self.app_secret,
            "q": keyword or "",
            "page": page,
            "cat": cat,
            "discount_only": discount_only,
            "sort": sort,
            "seller_info": seller_info,
            "nick": nick,
            "ppath": ppath,
            "imgid": imgid,
            "filter": filter,
            "cache": "yes",
            "result_type": "json",
            "lang": "cn"
        }
        
        # 添加价格范围
        if price_range:
            params["start_price"] = price_range[0]
            params["end_price"] = price_range[1]
        else:
            params["start_price"] = 0
            params["end_price"] = 0
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/item_search/",
                    params=params,
                    headers=self.headers
                )
                data = response.json()
                
                if "items" in data and "item" in data["items"]:
                    return data["items"]["item"]
                else:
                    print(f"API返回错误: {data.get('error', '未知错误')}")
                    return []
        except Exception as e:
            print(f"API调用错误: {str(e)}")
            return [] 
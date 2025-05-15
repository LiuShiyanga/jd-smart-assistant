"""
基于 langgraph 的智能导购 Agent
"""
from typing import TypedDict, Annotated, Sequence, Dict, Any, List, Union, Optional, cast
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
import importlib
from app.config import RUN_MODE, API_CONFIG, LLM_CONFIG
import json
import operator

# 定义 reducer 函数
def dict_merge(d1, d2):
    """合并两个字典"""
    return {**d1, **d2}

def last_value(a, b):
    """使用最后一个值"""
    return b

# 定义状态类型
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "对话历史", operator.add]
    current_step: Annotated[str, "当前步骤", last_value]
    item_info: Annotated[Dict[str, Any], "商品信息", dict_merge]
    comments: Annotated[list, "评论信息", operator.add]
    similar_items: Annotated[list, "相似商品", operator.add]
    analysis: Annotated[Dict[str, str], "分析结果", dict_merge]
    error: Annotated[str, "错误信息", last_value]
    next_action: Annotated[str, "下一步动作", last_value]
    context: Annotated[Dict[str, Any], "上下文信息", dict_merge]
    step_count: Annotated[Optional[int], "步骤计数", last_value]
    should_end: Annotated[bool, "是否结束", last_value]

class ProductAnalysisAgent:
    """商品分析 Agent"""
    
    def __init__(self):
        # 初始化 LLM
        self.llm = ChatOpenAI(
            model_name=LLM_CONFIG['model_name'],
            temperature=LLM_CONFIG['temperature'],
            max_tokens=LLM_CONFIG['max_tokens'],
            api_key=LLM_CONFIG['api_key'],
            base_url=LLM_CONFIG['api_base']
        )
        
        # 动态导入 API 类
        api_module = importlib.import_module(API_CONFIG[RUN_MODE]['api_module'])
        api_class = getattr(api_module, API_CONFIG[RUN_MODE]['api_class'])
        self.api = api_class()
        
        # 系统提示词
        self.system_prompt = """你是一个专业的购物助手，你的任务是：
        1. 分析商品信息，给出购买建议
        2. 分析用户评论，总结优缺点
        3. 对比相似商品，找出最佳选择
        4. 根据用户需求，提供个性化建议
        
        请记住：
        - 保持客观公正
        - 关注商品质量和性价比
        - 考虑用户的实际需求
        - 提供具体的购买理由
        """
        
        # 构建工作流
        self.workflow = self._build_workflow()
    
    def _build_workflow(self):
        """构建工作流图"""
        workflow = StateGraph(AgentState)
        
        # 定义节点函数
        async def decide_next_action(state: AgentState) -> Dict[str, Any]:
            """决定下一步动作"""
            current_step_count = state.get("step_count", 0) + 1
            try:
                # 检查是否应该结束 (例如由前一个动作节点设定)
                if state.get("should_end", False):
                    return {"should_end": True, "step_count": current_step_count}
                
                # 检查步骤计数是否超过限制
                if current_step_count >= 5: # Agent 逻辑的步数限制
                    return {"should_end": True, "step_count": current_step_count, "current_step": "max_steps_reached"}

                last_completed_step = state["current_step"]

                if last_completed_step == "start":
                    return {"next_action": "analyze_product", "step_count": current_step_count}
                elif last_completed_step == "analyze_product":
                    if not state.get("item_info"): # 商品信息获取失败或为空
                        # 可以选择重试 analyze_product，或者报错结束，或者让LLM决定
                        # 这里简单处理为让LLM决定，或者直接结束
                        return {
                            "error": "Failed to retrieve item_info in analyze_product.",
                            "should_end": True, # 或者交由LLM决定是否重试
                            "step_count": current_step_count
                        }
                    return {"next_action": "analyze_comments", "step_count": current_step_count}
                elif last_completed_step == "analyze_comments":
                    if not state.get("comments") and state.get("item_info"): # 评论获取失败或为空，但商品信息是有的
                         # 同上，可以决定重试或结束
                         return {
                            "error": "Failed to retrieve comments in analyze_comments.",
                            "should_end": True, # 或者交由LLM决定是否重试
                            "step_count": current_step_count
                        }
                    # 如果 item_info 为空，则不应该继续到 find_similar_items
                    if not state.get("item_info"):
                        return {"should_end": True, "error": "Cannot find similar items without item_info.", "step_count": current_step_count}
                    return {"next_action": "find_similar_items", "step_count": current_step_count}
                elif last_completed_step == "find_similar_items":
                    # 此时所有核心分析已完成（或尝试完成）
                    return {"should_end": True, "step_count": current_step_count}
                elif last_completed_step == "error": # 如果上一步骤是错误状态
                    return {"should_end": True, "error": state.get("error", "Error processed."), "step_count": current_step_count}
                else:
                    # 未知或非预期的 last_completed_step，通常不应该到这里，除非状态被外部改变
                    # 或者是有意设计的更复杂的流程，此时依赖LLM决策
                    prompt = f'''
                    You are a helpful AI assistant guiding a product analysis workflow.
                    Based on the current state, decide the next logical action.
                    
                    Current state:
                    - Last completed step: {last_completed_step}
                    - Item info: {'Available' if state.get('item_info') else 'Missing'}
                    - Comments: {'Available' if state.get('comments') else 'Missing'}
                    - Similar items: {'Available' if state.get('similar_items') else 'Missing'}
                    - Error: {state.get('error', 'None')}
                    - Step count: {current_step_count}
                    
                    Available actions: analyze_product, analyze_comments, find_similar_items, end.
                    Choose one action.
                    '''
                    messages = [
                        SystemMessage(content=self.system_prompt), # system_prompt for overall assistant persona
                        HumanMessage(content=prompt)
                    ]
                    response = await self.llm.ainvoke(messages)
                    action = response.content.strip().lower()
                    
                    if action == "end":
                        return {"should_end": True, "step_count": current_step_count}
                    elif action in ["analyze_product", "analyze_comments", "find_similar_items"]:
                        return {"next_action": action, "step_count": current_step_count}
                    else:
                        # LLM返回了无效动作
                        return {
                            "error": f"LLM returned invalid action: {action}",
                            "should_end": True,
                            "step_count": current_step_count
                        }
            except Exception as e:
                return {
                    "error": f"Error in decide_next_action: {str(e)}",
                    "should_end": True,
                    "step_count": current_step_count # current_step_count 已经计算
                }

        async def analyze_product(state: AgentState) -> AgentState:
            """分析商品详情"""
            try:
                # 从最后一条消息获取商品ID
                item_id = state["messages"][-1].content
                item_info = await self.api.item_get(item_id)
                
                # 使用LLM分析商品信息
                messages = [
                    SystemMessage(content=self.system_prompt),
                    HumanMessage(content=f"""
                    请分析以下商品信息，并给出购买建议：
                    商品名称：{item_info.get('title', '')}
                    价格：{item_info.get('price', 0)}元
                    品牌：{item_info.get('brand', '')}
                    销量：{item_info.get('total_sold', 0)}
                    店铺：{item_info.get('shop_info', {}).get('shop_name', '')}
                    """)
                ]
                
                response = await self.llm.ainvoke(messages)
                
                return {
                    "item_info": item_info,
                    "analysis": {"product": response.content},
                    "error": "",
                    "current_step": "analyze_product",
                    "messages": [AIMessage(content=response.content)]
                }
            except Exception as e:
                return {
                    "error": str(e),
                    "current_step": "error"
                }
        
        async def analyze_comments(state: AgentState) -> AgentState:
            """分析评论"""
            try:
                # 确保 item_info 和 num_iid 存在
                if not state.get("item_info") or not state["item_info"].get("num_iid"):
                    return {
                        "error": "Cannot analyze comments without item_id (num_iid from item_info).",
                        "current_step": "error", # 标记当前步骤为错误
                        "messages": [AIMessage(content="Error: Missing item_id for comment analysis.")]
                    }

                # 只有在没有评论时才获取和分析
                if not state.get("comments"): # 使用 get 避免 KeyError
                    item_id = state["item_info"]["num_iid"]
                    comments_data = await self.api.item_review(item_id) # Renamed variable to avoid conflict
                    
                    # 使用LLM分析评论
                    messages_llm = [ # Renamed variable
                        SystemMessage(content=self.system_prompt),
                        HumanMessage(content=f'''
                        请分析以下商品评论，总结用户反馈：
                        {json.dumps(comments_data[:5], ensure_ascii=False, indent=2)}
                        ''')
                    ]
                    
                    response = await self.llm.ainvoke(messages_llm)
                    
                    return {
                        "comments": comments_data,
                        "analysis": {**state.get("analysis",{}), "comments": response.content}, # Merge with existing analysis
                        "error": "",
                        "current_step": "analyze_comments",
                        "messages": state.get("messages", []) + [AIMessage(content=response.content)]
                    }
                else: # 评论已存在
                    return {
                        "current_step": "analyze_comments", # 确认当前步骤完成
                        "messages": state.get("messages", []) + [AIMessage(content="Comments already analyzed.")]
                         # No change to comments or analysis if already present
                    }
            except Exception as e:
                return {
                    "error": str(e),
                    "current_step": "error",
                    "messages": state.get("messages", []) + [AIMessage(content=f"Error in analyze_comments: {str(e)}")]
                }
        
        async def find_similar_items(state: AgentState) -> AgentState:
            """查找相似商品"""
            try:
                # 确保 item_info 存在
                if not state.get("item_info"):
                    return {
                        "error": "Cannot find similar items without item_info.",
                        "current_step": "error",
                        "messages": [AIMessage(content="Error: Missing item_info for finding similar items.")]
                    }

                # 只有在没有相似商品时才获取和分析
                if not state.get("similar_items"): # 使用 get 避免 KeyError
                    item_info_data = state["item_info"] # Renamed variable
                    price = item_info_data.get("price", 0)
                    
                    # 确保 title 存在
                    title = item_info_data.get("title")
                    if not title:
                         return {
                            "error": "Cannot find similar items without product title in item_info.",
                            "current_step": "error",
                            "messages": [AIMessage(content="Error: Missing product title for finding similar items.")]
                        }

                    similar_items_data = await self.api.item_search( # Renamed variable
                        keyword=title,
                        price_range=(price * 0.9, price * 1.1) if price else None # Handle price might be 0 or None
                    )
                    
                    # 使用LLM分析相似商品
                    messages_llm = [ # Renamed variable
                        SystemMessage(content=self.system_prompt),
                        HumanMessage(content=f'''
                        请比较以下商品，给出购买建议：
                        原商品：{title} - {price}元
                        相似商品：
                        {json.dumps(similar_items_data[:2], ensure_ascii=False, indent=2)}
                        ''')
                    ]
                    
                    response = await self.llm.ainvoke(messages_llm)
                    
                    return {
                        "similar_items": similar_items_data[:2],
                        "analysis": {**state.get("analysis",{}), "comparison": response.content}, # Merge
                        "error": "",
                        "current_step": "find_similar_items",
                        "messages": state.get("messages", []) + [AIMessage(content=response.content)]
                    }
                else: # 相似商品已存在
                     return {
                        "current_step": "find_similar_items",
                        "messages": state.get("messages", []) + [AIMessage(content="Similar items already analyzed.")]
                    }
            except Exception as e:
                return {
                    "error": str(e),
                    "current_step": "error",
                    "messages": state.get("messages", []) + [AIMessage(content=f"Error in find_similar_items: {str(e)}")]
                }
        
        # 添加节点
        workflow.add_node("decide_next_action", decide_next_action)
        workflow.add_node("analyze_product", analyze_product)
        workflow.add_node("analyze_comments", analyze_comments)
        workflow.add_node("find_similar_items", find_similar_items)
        
        # 定义路由逻辑
        def route_logic(state: AgentState) -> str:
            if state.get("should_end", False):
                return END
            
            next_action = state.get("next_action")
            if next_action in ["analyze_product", "analyze_comments", "find_similar_items"]:
                return next_action
            else:
                # 如果 next_action 无效或未设置，并且不应该结束，则这是一个意外情况。
                # decide_next_action 应该在这种情况下设置错误并标记 should_end=True。
                # 作为安全措施，我们在此处路由到 END。
                return END

        # 设置条件边
        workflow.add_conditional_edges(
            "decide_next_action",
            route_logic,
            {
                "analyze_product": "analyze_product",
                "analyze_comments": "analyze_comments",
                "find_similar_items": "find_similar_items",
                END: END  # 将 END (特殊标记) 映射到图的终止状态
            }
        )
        
        # 连接动作节点回到决策节点
        workflow.add_edge("analyze_product", "decide_next_action")
        workflow.add_edge("analyze_comments", "decide_next_action")
        workflow.add_edge("find_similar_items", "decide_next_action")
        
        # 设置入口
        workflow.set_entry_point("decide_next_action")
        
        return workflow.compile()
    
    async def run(self, item_id: str) -> dict:
        """运行 Agent"""
        # 初始化状态
        initial_state = {
            "messages": [HumanMessage(content=item_id)],
            "current_step": "start",
            "item_info": {},
            "comments": [],
            "similar_items": [],
            "analysis": {},
            "error": "",
            "next_action": "",
            "context": {},
            "step_count": 0,
            "should_end": False
        }
        
        # 运行工作流
        config = {"recursion_limit": 10}  # 设置递归限制
        final_state = await self.workflow.ainvoke(initial_state, config=config)
        return final_state 
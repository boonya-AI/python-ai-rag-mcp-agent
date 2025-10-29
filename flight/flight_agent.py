from openai import OpenAI
import json
import re

from flight.all_in_one import TravelPolicyRAG


class FlightBookingAgent:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.rag = TravelPolicyRAG()
        self.available_tools = {
            "search_flights": "搜索航班信息",
            "book_flight": "预订指定航班",
            "get_weather": "获取目的地天气",
            "query_policy": "查询公司差旅政策"
        }

    def _extract_tool_call(self, response: str) -> dict:
        """从AI响应中提取工具调用信息"""
        tool_pattern = r'【(\w+)】:\s*(.+)'
        match = re.search(tool_pattern, response)
        if match:
            return {"tool": match.group(1), "params": match.group(2)}
        return None

    def _parse_tool_params(self, tool_name: str, params_str: str) -> dict:
        """解析工具参数"""
        if tool_name == "search_flights":
            # 解析 "北京, 2024-01-15, 5000" 这样的参数
            parts = [p.strip() for p in params_str.split(",")]
            return {
                "destination": parts[0],
                "date": parts[1] if len(parts) > 1 else None,
                "max_price": int(parts[2]) if len(parts) > 2 else None
            }
        elif tool_name == "book_flight":
            parts = [p.strip() for p in params_str.split(",")]
            return {
                "flight_no": parts[0],
                "passenger_name": parts[1] if len(parts) > 1 else "张三",
                "passenger_id": parts[2] if len(parts) > 2 else "110101199001011234"
            }
        elif tool_name == "get_weather":
            parts = [p.strip() for p in params_str.split(",")]
            return {
                "destination": parts[0],
                "date": parts[1] if len(parts) > 1 else None
            }
        return {"query": params_str}

    def process_request(self, user_request: str) -> str:
        """处理用户请求"""
        print(f"用户请求: {user_request}")

        # 步骤1: 规划决策
        planning_prompt = f"""
        你是一个机票预订助手。用户请求: {user_request}

        可用工具:
        - query_policy: 查询公司差旅政策
        - search_flights: 搜索航班 (参数: 目的地,日期,最高价格)
        - book_flight: 预订航班 (参数: 航班号,乘客姓名,身份证号)  
        - get_weather: 获取天气信息 (参数: 目的地,日期)

        请分析需要按什么顺序调用哪些工具，用【工具名】: 参数 的格式回答。
        示例: 【query_policy】: 北京差旅标准
        """

        planning_response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": planning_prompt}],
            temperature=0
        )

        plan = planning_response.choices[0].message.content
        print(f"执行计划: {plan}")

        # 步骤2: 执行工具调用
        final_result = []
        lines = plan.split('\n')

        for line in lines:
            tool_call = self._extract_tool_call(line)
            if tool_call:
                tool_name = tool_call["tool"]
                params = self._parse_tool_params(tool_name, tool_call["params"])

                print(f"执行工具: {tool_name} 参数: {params}")

                # 执行相应的工具
                if tool_name == "query_policy":
                    result = self.rag.query_policy(params.get("query", ""))
                elif tool_name in ["search_flights", "book_flight", "get_weather"]:
                    # 这里应该调用MCP客户端来执行工具
                    result = self._call_mcp_tool(tool_name, params)
                else:
                    result = f"未知工具: {tool_name}"

                final_result.append(f"{tool_name}结果: {result}")
                print(f"工具结果: {result}")

        # 步骤3: 生成最终回复
        if final_result:
            summary_prompt = f"""
            用户原始请求: {user_request}

            执行结果:
            {chr(10).join(final_result)}

            请根据以上信息给用户一个完整、友好的回复。
            """

            summary_response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": summary_prompt}],
                temperature=0.7
            )

            return summary_response.choices[0].message.content
        else:
            return "未能处理您的请求"

    def _call_mcp_tool(self, tool_name: str, params: dict) -> str:
        """模拟调用MCP工具"""
        # 在实际实现中，这里会通过MCP客户端调用远程工具
        if tool_name == "search_flights":
            return f"模拟搜索: 到{params['destination']}的航班 (实际会调用MCP)"
        elif tool_name == "book_flight":
            return f"模拟预订: 航班{params['flight_no']} (实际会调用MCP)"
        elif tool_name == "get_weather":
            return f"模拟天气: {params['destination']}天气良好"
        return "工具调用失败"
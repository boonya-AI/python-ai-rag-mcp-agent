import re
import json
from datetime import datetime, timedelta

from flight.ollama.travel_policy_rag import TravelPolicyRAG
from flight.ollama.qunar_flight_api import QunarFlightAPI


class OllamaFlightAgent:
    def __init__(self, model_name: str = "qwen2:7b"):
        self.model_name = model_name
        self.rag = TravelPolicyRAG()
        self.flight_api = QunarFlightAPI()

        # 可用的工具列表
        self.tools = {
            "search_flights": self.search_flights,
            "book_flight": self.book_flight,
            "query_policy": self.query_policy,
            "get_weather": self.get_weather
        }

    def call_ollama(self, messages: list) -> str:
        """调用Ollama模型"""
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=messages
            )
            return response['message']['content']
        except Exception as e:
            return f"调用模型出错: {e}"

    def search_flights(self, params: dict) -> str:
        """搜索航班工具"""
        dep_city = params.get('departure', '北京')  # 默认从北京出发
        arr_city = params.get('destination')
        date = params.get('date')

        if not arr_city:
            return "需要指定目的地城市"

        if not date:
            # 默认3天后
            date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")

        result = self.flight_api.search_flights(dep_city, arr_city, date)

        if 'error' in result:
            return f"搜索失败: {result['error']}"

        flights = result['data']['flights']
        response = [f"找到 {len(flights)} 个从{dep_city}到{arr_city}的航班 ({date}):"]

        for flight in flights:
            response.append(
                f"- {flight['flightNumber']} {flight['airline']} "
                f"{flight['departureTime']}-{flight['arrivalTime']} "
                f"￥{flight['price']} 准点率:{flight['punctualityRate']}"
            )

        return "\n".join(response)

    def book_flight(self, params: dict) -> str:
        """预订航班工具"""
        flight_number = params.get('flight_number')
        passenger_name = params.get('passenger_name', '张三')
        passenger_id = params.get('passenger_id', '110101199001011234')

        if not flight_number:
            return "需要指定航班号"

        passenger_info = {
            'name': passenger_name,
            'idCard': passenger_id,
            'phone': '13800138000',
            'email': 'zhangsan@company.com'
        }

        result = self.flight_api.create_booking(flight_number, passenger_info)

        if result.get('success'):
            return (f"预订成功!\n"
                    f"预订号: {result['bookingId']}\n"
                    f"航班: {result['flightNumber']}\n"
                    f"乘客: {result['passengerName']}\n"
                    f"金额: ￥{result['amount']}\n"
                    f"状态: {result['status']}\n"
                    f"时间: {result['bookingTime']}")
        else:
            return f"预订失败: {result.get('error', '未知错误')}"

    def query_policy(self, params: dict) -> str:
        """查询政策工具"""
        query = params.get('query', '')
        return self.rag.query_policy(query)

    def get_weather(self, params: dict) -> str:
        """获取天气工具（模拟）"""
        city = params.get('destination', '北京')
        # 模拟天气数据
        weather_data = {
            "北京": "晴朗 15-25°C 北风2级 适宜出行",
            "上海": "多云 18-28°C 东南风3级 适宜出行",
            "广州": "阵雨 22-30°C 南风2级 建议带伞",
            "深圳": "多云 24-32°C 南风3级 适宜出行"
        }
        return weather_data.get(city, "天气信息暂不可用")

    def _parse_tool_call(self, text: str) -> dict:
        """解析工具调用"""
        # 匹配格式: 【工具名】参数
        pattern = r'【(\w+)】\s*(.*)'
        match = re.search(pattern, text)
        if match:
            return {
                'tool': match.group(1),
                'params_str': match.group(2).strip()
            }
        return None

    def _parse_params(self, tool_name: str, params_str: str) -> dict:
        """解析参数字符串"""
        if tool_name == "search_flights":
            # 格式: 北京,上海,2024-01-20
            parts = [p.strip() for p in params_str.split(',')]
            params = {}
            if len(parts) > 0:
                params['destination'] = parts[0]
            if len(parts) > 1:
                params['date'] = parts[1]
            return params

        elif tool_name == "book_flight":
            # 格式: CA1234,张三,110101199001011234
            parts = [p.strip() for p in params_str.split(',')]
            params = {}
            if len(parts) > 0:
                params['flight_number'] = parts[0]
            if len(parts) > 1:
                params['passenger_name'] = parts[1]
            if len(parts) > 2:
                params['passenger_id'] = parts[2]
            return params

        elif tool_name == "get_weather":
            return {'destination': params_str.strip()}

        else:  # query_policy和其他
            return {'query': params_str}

    def process_request(self, user_request: str) -> str:
        """处理用户请求"""
        print(f"用户请求: {user_request}")

        # 第一步：规划工具调用
        planning_prompt = f"""
        你是一个专业的机票预订助手，可以帮用户查询差旅政策、搜索航班、预订机票和查询天气。

        用户请求: {user_request}

        可用工具:
        - query_policy: 查询公司差旅政策，参数示例: 【query_policy】北京差旅标准
        - search_flights: 搜索航班，参数格式: 【search_flights】目的地,日期(可选) 示例: 【search_flights】上海,2024-01-20
        - book_flight: 预订航班，参数格式: 【book_flight】航班号,乘客姓名(可选),身份证号(可选) 示例: 【book_flight】CA1234,张三
        - get_weather: 获取天气，参数: 【get_weather】目的地

        请分析用户请求，规划需要调用的工具序列。用以下格式回答，每行一个工具调用:
        【工具名】参数

        注意: 如果用户没有指定日期，使用3天后的日期。
        """

        planning_messages = [
            {"role": "system", "content": "你是一个专业的旅行助手，需要准确分析用户需求并调用合适的工具。"},
            {"role": "user", "content": planning_prompt}
        ]

        plan = self.call_ollama(planning_messages)
        print(f"执行计划:\n{plan}")

        # 第二步：执行工具调用
        results = []
        lines = plan.strip().split('\n')

        for line in lines:
            tool_call = self._parse_tool_call(line)
            if tool_call:
                tool_name = tool_call['tool']
                params_str = tool_call['params_str']

                if tool_name in self.tools:
                    params = self._parse_params(tool_name, params_str)
                    print(f"执行工具: {tool_name}, 参数: {params}")

                    try:
                        result = self.tools[tool_name](params)
                        results.append(f"{tool_name}结果: {result}")
                        print(f"工具结果: {result}")
                    except Exception as e:
                        error_msg = f"工具执行出错: {str(e)}"
                        results.append(error_msg)
                        print(error_msg)
                else:
                    error_msg = f"未知工具: {tool_name}"
                    results.append(error_msg)
                    print(error_msg)

        # 第三步：生成最终回复
        if results:
            summary_prompt = f"""
            用户原始请求: {user_request}

            工具执行结果:
            {chr(10).join(results)}

            请根据以上执行结果，给用户一个完整、友好、专业的回复。
            包括所有相关信息，并给出明确的下一步建议。
            """

            summary_messages = [
                {"role": "system", "content": "你是一个专业的旅行助手，需要根据工具执行结果给出准确、友好的回复。"},
                {"role": "user", "content": summary_prompt}
            ]

            final_response = self.call_ollama(summary_messages)
            return final_response
        else:
            return "抱歉，我无法处理您的请求。请提供更具体的信息。"
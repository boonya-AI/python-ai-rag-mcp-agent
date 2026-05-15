import json
import asyncio
from mcp import MCPServer, types

# mcp 至少要用python3.10
class FlightMCPServer:
    def __init__(self):
        self.server = MCPServer("flight-tools")

        # 模拟航班数据
        self.flight_data = {
            "北京": [
                {"flight_no": "CA1234", "airline": "中国国航", "departure": "09:00",
                 "price": 4800, "seats": 5, "class": "economy"},
                {"flight_no": "MU5678", "airline": "东方航空", "departure": "14:30",
                 "price": 5200, "seats": 3, "class": "economy"}
            ],
            "上海": [
                {"flight_no": "CZ9012", "airline": "南方航空", "departure": "10:15",
                 "price": 4500, "seats": 8, "class": "economy"}
            ]
        }

        self._register_tools()

    def _register_tools(self):
        @self.server.tool()
        async def search_flights(destination: str, date: str, max_price: int = None) -> str:
            """搜索航班信息

            Args:
                destination: 目的地城市
                date: 出行日期 (YYYY-MM-DD)
                max_price: 最高价格限制
            """
            if destination not in self.flight_data:
                return f"未找到到{destination}的航班"

            flights = self.flight_data[destination]
            if max_price:
                flights = [f for f in flights if f['price'] <= max_price]

            if not flights:
                return "没有符合条件的航班"

            result = [f"找到 {len(flights)} 个到{destination}的航班:"]
            for flight in flights:
                result.append(
                    f"- {flight['flight_no']} {flight['airline']} "
                    f"{flight['departure']} ￥{flight['price']} "
                    f"余票:{flight['seats']}"
                )

            return "\n".join(result)

        @self.server.tool()
        async def book_flight(flight_no: str, passenger_name: str, passenger_id: str) -> str:
            """预订航班

            Args:
                flight_no: 航班号
                passenger_name: 乘客姓名
                passenger_id: 身份证号
            """
            # 在实际系统中这里会调用航空公司API
            for city_flights in self.flight_data.values():
                for flight in city_flights:
                    if flight['flight_no'] == flight_no:
                        if flight['seats'] > 0:
                            flight['seats'] -= 1
                            booking_ref = f"BK{flight_no}{passenger_id[-4:]}"
                            return (f"预订成功! 航班: {flight_no}\n"
                                    f"乘客: {passenger_name}\n"
                                    f"预订号: {booking_ref}\n"
                                    f"状态: 已确认")
                        else:
                            return "抱歉，该航班已无余票"

            return "未找到指定航班"

        @self.server.tool()
        async def get_weather(destination: str, date: str) -> str:
            """获取目的地天气信息"""
            # 模拟天气数据
            weather_data = {
                "北京": "晴朗，15-25°C，适宜出行",
                "上海": "多云，18-28°C，适宜出行",
                "广州": "阵雨，22-30°C，建议带伞"
            }
            return weather_data.get(destination, "天气信息暂不可用")

    async def run(self):
        await self.server.run()
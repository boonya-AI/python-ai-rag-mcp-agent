import requests
import json
from datetime import datetime, timedelta


class QunarFlightAPI:
    def __init__(self):
        # 去哪儿网机票搜索API基础URL（模拟真实API）
        self.search_url = "https://flight.qunar.com/touch/api/domestic/wbdflightlist"
        self.booking_url = "https://flight.qunar.com/touch/api/order/create"

    def search_flights(self, dep_city: str, arr_city: str, date: str):
        """搜索航班信息（模拟去哪儿网API）"""
        try:
            # 模拟API参数
            params = {
                'departureCity': dep_city,
                'arrivalCity': arr_city,
                'departureDate': date,
                'ex_track': 'auto_4e0b83a7'
            }

            # 在实际应用中，这里会调用真实的API
            # response = requests.get(self.search_url, params=params)
            # return response.json()

            # 模拟返回数据（基于真实去哪儿网数据结构）
            return self._mock_flight_data(dep_city, arr_city, date)

        except Exception as e:
            print(f"搜索航班出错: {e}")
            return {"error": str(e)}

    def _mock_flight_data(self, dep_city: str, arr_city: str, date: str):
        """模拟去哪儿网航班数据"""
        # 基础航班信息
        base_flights = [
            {
                'flightNumber': 'CA1234',
                'airline': '中国国航',
                'departureTime': '08:00',
                'arrivalTime': '10:30',
                'price': 4800,
                'discount': 0.85,
                'craftType': 'A320',
                'punctualityRate': '95%'
            },
            {
                'flightNumber': 'MU5678',
                'airline': '东方航空',
                'departureTime': '14:30',
                'arrivalTime': '17:00',
                'price': 5200,
                'discount': 0.92,
                'craftType': 'B737',
                'punctualityRate': '92%'
            },
            {
                'flightNumber': 'CZ9012',
                'airline': '南方航空',
                'departureTime': '19:15',
                'arrivalTime': '21:45',
                'price': 4500,
                'discount': 0.78,
                'craftType': 'A321',
                'punctualityRate': '98%'
            }
        ]

        # 根据城市和日期生成具体数据
        flights = []
        for i, base in enumerate(base_flights):
            flight = base.copy()
            flight['price'] = int(flight['price'] * (0.9 + 0.2 * (i / len(base_flights))))
            flights.append(flight)

        return {
            'data': {
                'flights': flights,
                'depCity': dep_city,
                'arrCity': arr_city,
                'date': date,
                'timestamp': datetime.now().isoformat()
            }
        }

    def create_booking(self, flight_number: str, passenger_info: dict):
        """创建机票预订（模拟）"""
        try:
            # 模拟预订请求
            booking_data = {
                'flightNumber': flight_number,
                'passenger': passenger_info,
                'contact': passenger_info.get('contact', {}),
                'timestamp': datetime.now().isoformat()
            }

            # 在实际应用中，这里会调用真实的预订API
            # response = requests.post(self.booking_url, json=booking_data)
            # return response.json()

            # 模拟成功响应
            return {
                'success': True,
                'bookingId': f'QN{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'flightNumber': flight_number,
                'passengerName': passenger_info['name'],
                'status': 'CONFIRMED',
                'amount': 4800,
                'bookingTime': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}
# 主程序
from flight.openai import FlightBookingAgent


def main():
    # 初始化Agent (需要设置你的OpenAI API Key)
    agent = FlightBookingAgent(api_key="your-openai-api-key")

    # 示例用户请求
    user_requests = [
        "帮我预订下周三去北京的经济舱机票，预算不超过5000元",
        "查询一下公司去上海的差旅政策，然后看看有没有明天下午的航班",
        "我要去广州出差，先看看政策标准，再查查天气和航班"
    ]

    for request in user_requests:
        print("\n" + "=" * 50)
        print(f"处理请求: {request}")
        print("=" * 50)

        result = agent.process_request(request)
        print(f"\n最终回复:\n{result}")


if __name__ == "__main__":
    main()
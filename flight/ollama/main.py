from flight.ollama.ollama_flight_agent import OllamaFlightAgent


def call():
    print("call main function")


def main():
    call()

    print("初始化机票预订智能体...")

    # 初始化智能体（使用Ollama）
    agent = OllamaFlightAgent(model_name="qwen2:7b")  # 也可以使用 llama2 或其他的模型

    # 测试请求
    test_requests = [
        "帮我预订去上海的机票",
        "查询公司去北京的差旅政策，然后搜索明天下午的航班",
        "我要去广州出差，先看看政策，再查查天气和航班信息",
        "预订航班CA1234，乘客李四"
    ]

    print("\n" + "=" * 60)
    print("机票预订智能体演示 (基于Ollama + 去哪儿网API)")
    print("=" * 60)

    for i, request in enumerate(test_requests, 1):
        print(f"\n{'=' * 40}")
        print(f"测试 {i}: {request}")
        print(f"{'=' * 40}")

        response = agent.process_request(request)
        print(f"\n智能体回复:\n{response}")

        if i < len(test_requests):
            input("\n按回车键继续下一个测试...")


if __name__ == "__main__":
    main()
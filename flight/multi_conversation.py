from flight.flight_agent import FlightBookingAgent

# 多对话历史
class ConversationalFlightAgent(FlightBookingAgent):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.conversation_history = []

    def chat(self, user_message: str) -> str:
        self.conversation_history.append({"role": "user", "content": user_message})

        # 基于对话历史进行决策
        response = self.process_request_with_history(user_message)

        self.conversation_history.append({"role": "assistant", "content": response})
        return response
# requirements.txt
# openai
# chromadb
# python-dotenv

import openai
import chromadb
import json
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class TravelPolicyRAG:
    def __init__(self):
        self.client = chromadb.Client()
        self.collection = self.client.create_collection("travel_policy")
        openai.api_key = os.getenv("OPENAI_API_KEY")

        self._initialize_knowledge_base()

    def _get_embedding(self, text: str) -> list:
        """使用OpenAI API获取文本嵌入"""
        try:
            response = openai.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"获取嵌入时出错: {e}")
            return [0.1] * 1536  # text-embedding-3-small的维度

    def _initialize_knowledge_base(self):
        # 创建示例政策数据
        policy = {
            "travel_policy": {
                "flight_standards": {
                    "beijing": {"economy": 5500, "business": 12000},
                    "shanghai": {"economy": 5000, "business": 11000},
                    "guangzhou": {"economy": 4500, "business": 10000}
                },
                "approval_required": {
                    "domestic": 10000,
                    "international": 20000
                },
                "preferred_airlines": ["中国国航", "东方航空", "南方航空"],
                "advance_booking": "国内航班需提前3天预订"
            }
        }

        documents = []
        metadatas = []
        ids = []

        def flatten_dict(d, prefix=""):
            items = []
            for k, v in d.items():
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, f"{prefix}{k}."))
                else:
                    items.append((f"{prefix}{k}", str(v)))
            return items

        flat_items = flatten_dict(policy)
        for i, (key, value) in enumerate(flat_items):
            doc_text = f"{key}: {value}"
            documents.append(doc_text)
            metadatas.append({"type": "policy", "key": key})
            ids.append(f"policy_{i}")

        # 批量获取嵌入
        embeddings = []
        for doc in documents:
            embedding = self._get_embedding(doc)
            embeddings.append(embedding)

        # 添加到向量数据库
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print("知识库初始化完成!")

    def query_policy(self, question: str) -> str:
        """查询差旅政策"""
        query_embedding = self._get_embedding(question)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=3
        )

        if results['documents']:
            return "\n".join(results['documents'][0])
        return "未找到相关政策信息"


# 测试
if __name__ == "__main__":
    # 确保设置了 OPENAI_API_KEY 环境变量
    rag = TravelPolicyRAG()

    test_questions = [
        "去北京的差旅标准是多少？",
        "经济舱的报销标准",
        "需要提前多久预订机票？"
    ]

    for question in test_questions:
        print(f"问题: {question}")
        answer = rag.query_policy(question)
        print(f"回答: {answer}\n")
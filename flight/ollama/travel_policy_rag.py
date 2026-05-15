import ollama
import chromadb
import json
import requests


class TravelPolicyRAG:
    def __init__(self):
        self.client = chromadb.Client()
        self.collection = self.client.create_collection("travel_policy")

        # 初始化知识库
        self._initialize_knowledge_base()

    def _get_embedding(self, text: str) -> list:
        """使用Ollama获取文本嵌入"""
        try:
            # 使用Ollama的嵌入模型
            response = ollama.embeddings(model='nomic-embed-text', prompt=text)
            return response['embedding']
        except Exception as e:
            print(f"获取嵌入时出错: {e}")
            # 返回一个简单的fallback嵌入
            return [0.1] * 768

    def _initialize_knowledge_base(self):
        # 创建公司差旅政策
        policy = {
            "travel_policy": {
                "flight_standards": {
                    "北京": {"economy": 5500, "business": 12000},
                    "上海": {"economy": 5000, "business": 11000},
                    "广州": {"economy": 4500, "business": 10000},
                    "深圳": {"economy": 4800, "business": 10500}
                },
                "approval_required": {
                    "domestic": 10000,
                    "international": 20000
                },
                "preferred_airlines": ["中国国航", "东方航空", "南方航空"],
                "advance_booking": "国内航班需提前3天预订",
                "class_preference": "经理级以下员工预订经济舱"
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
        print("差旅政策知识库初始化完成!")

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
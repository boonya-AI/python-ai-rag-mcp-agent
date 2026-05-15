import chromadb
from sentence_transformers import SentenceTransformer
import json


class TravelPolicyRAG:
    def __init__(self):
        self.client = chromadb.Client()
        self.collection = self.client.create_collection("travel_policy")
        self.embedder = SentenceTransformer('BAAI/bge-small-zh')

        # 初始化知识库
        self._initialize_knowledge_base()

    def _initialize_knowledge_base(self):
        with open('company_policy.json', 'r', encoding='utf-8') as f:
            policy = json.load(f)

        documents = []
        metadatas = []
        ids = []

        # 扁平化政策数据
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
            documents.append(f"{key}: {value}")
            metadatas.append({"type": "policy", "key": key})
            ids.append(f"policy_{i}")

        # 添加嵌入到向量数据库
        embeddings = self.embedder.encode(documents).tolist()
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def query_policy(self, question: str) -> str:
        """查询差旅政策"""
        query_embedding = self.embedder.encode([question]).tolist()[0]

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=3
        )

        if results['documents']:
            return "\n".join(results['documents'][0])
        return "未找到相关政策信息"
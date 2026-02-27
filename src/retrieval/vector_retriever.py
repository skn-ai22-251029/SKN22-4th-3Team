from langsmith import traceable
from src.core.config import ZipsaConfig
from src.utils.mongodb import MongoDBManager
from src.embeddings.factory import EmbeddingFactory

class VectorRetriever:
    def __init__(self, collection_name=None):
        self.policy = ZipsaConfig.get_policy("v3")
        self.db = MongoDBManager.get_v3_db()
        self.collection_name = collection_name or self.policy.collection_name
        self.collection = self.db[self.collection_name]
        self.embedder = EmbeddingFactory.get_embedder()

    @traceable(name="Vector Search")
    async def search(self, query: str, specialist: str = None, limit: int = 3, filters: dict = None):
        """Atlas 벡터 검색 로직을 처리합니다."""
        print(f"🔍 [VECTOR RETRIEVER]: '{query}' 검색 중 (전문가: {specialist}, 필터: {filters})...")
        
        try:
            query_vector = await self.embedder.embed_query(query)
            
            # 메타데이터 필터 구성
            combined_filter = {}
            if specialist:
                combined_filter["specialists"] = specialist
            if filters:
                combined_filter.update(filters)
                
            vector_search_stage = {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embedding",
                    "queryVector": query_vector,
                    "numCandidates": 100,
                    "limit": limit
                }
            }
            if combined_filter:
                vector_search_stage["$vectorSearch"]["filter"] = combined_filter

            results = await self.collection.aggregate([
                vector_search_stage,
                { "$set": { "score_type": "vector" } }
            ]).to_list(None)
            
            print(f"✅ [VECTOR RETRIEVER]: {len(results)}건의 결과를 찾았습니다.")
            return results

        except Exception as e:
            print(f"벡터 검색 오류: {e}")
            return []

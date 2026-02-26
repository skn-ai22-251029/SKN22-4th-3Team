from langsmith import traceable
from src.core.config import ZipsaConfig
from src.utils.mongodb import MongoDBManager
from src.embeddings.factory import EmbeddingFactory
from src.utils.text import tokenize_korean

class HybridRetriever:
    def __init__(self, version="v2", collection_name=None):
        self.policy = ZipsaConfig.get_policy(version)
        if version == "v1":
            self.db = MongoDBManager.get_v1_db()
        elif version == "v3":
            self.db = MongoDBManager.get_v3_db()
        else:
            self.db = MongoDBManager.get_v2_db()
        
        # 정책에 있는 컬렉션을 기본값으로 사용 (명시적으로 주어지지 않은 경우)
        self.collection_name = collection_name or self.policy.collection_name
        self.collection = self.db[self.collection_name]
        self.embedder = EmbeddingFactory.get_embedder()

    @traceable(name="Hybrid Search")
    async def search(self, query: str, specialist: str = None, limit: int = 3, filters: dict = None):
        """
        RRF (Reciprocal Rank Fusion)를 사용하여 하이브리드 검색을 수행합니다.
        """
        print(f"🔍 [RETRIEVER]: '{query}' 검색 중 (전문가: {specialist}, 필터: {filters})...")
        
        # 1. 입력 전처리
        if specialist == "General":
            specialist = None
            
        # 2. 개별 검색 실행 (벡터 및 키워드)
        vector_results = await self._run_vector_search(query, specialist, filters, limit)
        keyword_results = await self._run_keyword_search(query, specialist, filters, limit)

        # 3. RRF를 사용한 결합 및 랭킹
        merged = self._rank_and_merge(vector_results, keyword_results, limit)
        
        print(f"✅ [RETRIEVER]: {len(merged)}건의 결과를 찾았습니다.")
        return merged

    async def _run_vector_search(self, query: str, specialist: str, filters: dict, limit: int):
        """Atlas 벡터 검색 로직을 처리합니다."""
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
                "limit": limit * 2
            }
        }
        if combined_filter:
            vector_search_stage["$vectorSearch"]["filter"] = combined_filter

        try:
            return await self.collection.aggregate([
                vector_search_stage,
                { "$set": { "score_type": "vector" } }
            ]).to_list(None)
        except Exception as e:
            print(f"벡터 검색 오류: {e}")
            return []

    async def _run_keyword_search(self, query: str, specialist: str, filters: dict, limit: int):
        """메타데이터 필터링을 포함한 Atlas 검색 (BM25)을 처리합니다."""
        try:
            tokenized_query = tokenize_korean(query)
            
            if specialist or filters:
                must_clauses = [{"text": {"query": tokenized_query, "path": "tokenized_text"}}]
                filter_clauses = []
                
                if specialist:
                    filter_clauses.append({"text": {"query": specialist, "path": "specialists"}})
                
                if filters:
                    for k, v in filters.items():
                        if isinstance(v, dict):
                            if "$lte" in v: filter_clauses.append({"range": {"path": k, "lte": v["$lte"]}})
                            elif "$gte" in v: filter_clauses.append({"range": {"path": k, "gte": v["$gte"]}})
                            elif "$eq" in v: filter_clauses.append({"equals": {"path": k, "value": v["$eq"]}})
                        else:
                            filter_clauses.append({"equals": {"path": k, "value": v}})

                search_query = {
                    "index": "keyword_index",
                    "compound": {
                        "must": must_clauses,
                        "filter": filter_clauses if filter_clauses else [{"wildcard": {"path": "*", "query": "*"}}]
                    }
                }
            else:
                search_query = {
                    "index": "keyword_index",
                    "text": {"query": tokenized_query, "path": "tokenized_text"}
                }

            return await self.collection.aggregate([
                { "$search": search_query },
                { "$limit": limit * 2 },
                { "$set": { "score_type": "keyword" } }
            ]).to_list(None)
        except Exception as e:
            print(f"키워드 검색 실패: {e}")
            return []

    def _rank_and_merge(self, vector_results, keyword_results, limit):
        """RRF (Reciprocal Rank Fusion)를 적용하고 결과를 병합합니다."""
        scores = {}
        for rank, doc in enumerate(vector_results):
            doc_id = str(doc.get("_id"))
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (rank + 60)

        for rank, doc in enumerate(keyword_results):
            doc_id = str(doc.get("_id"))
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (rank + 60)
        
        all_docs = vector_results + keyword_results
        if not all_docs:
            return []

        all_docs_sorted = sorted(all_docs, key=lambda x: scores.get(str(x.get("_id")), 0), reverse=True)
        
        merged = []
        seen = set()
        for doc in all_docs_sorted:
            doc_id = str(doc.get("_id"))
            if doc_id not in seen:
                doc["final_score"] = scores[doc_id]
                merged.append(doc)
                seen.add(doc_id)
        
        return merged[:limit]

# 사용 예시
# retriever = HybridRetriever(collection_name="breeds")
# results = await retriever.search("활동적인 고양이 추천해줘")

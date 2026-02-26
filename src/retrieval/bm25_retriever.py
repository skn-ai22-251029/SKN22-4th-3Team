from langsmith import traceable
from src.core.config import ZipsaConfig
from src.utils.mongodb import MongoDBManager
from src.utils.text import tokenize_korean

class BM25Retriever:
    def __init__(self, version="v2", collection_name=None):
        self.policy = ZipsaConfig.get_policy(version)
        if version == "v1":
            self.db = MongoDBManager.get_v1_db()
        elif version == "v3":
            self.db = MongoDBManager.get_v3_db()
        else:
            self.db = MongoDBManager.get_v2_db()
        
        self.collection_name = collection_name or self.policy.collection_name
        self.collection = self.db[self.collection_name]

    @traceable(name="BM25 Search")
    async def search(self, query: str, specialist: str = None, limit: int = 3, filters: dict = None):
        """메타데이터 필터링을 포함한 Atlas 검색 (BM25)을 처리합니다."""
        print(f"🔍 [BM25 RETRIEVER]: '{query}' 검색 중 (전문가: {specialist}, 필터: {filters})...")
        
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

            results = await self.collection.aggregate([
                { "$search": search_query },
                { "$limit": limit },
                { "$set": { "score_type": "keyword" } }
            ]).to_list(None)
            
            print(f"✅ [BM25 RETRIEVER]: {len(results)}건의 결과를 찾았습니다.")
            return results

        except Exception as e:
            print(f"키워드 검색 실패: {e}")
            return []

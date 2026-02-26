import os
import pickle
import asyncio
from tqdm import tqdm
from src.utils.mongodb import MongoDBManager
from src.core.config import ZipsaConfig
from src.pipelines.base import BaseLoader

class V3Loader(BaseLoader):
    def __init__(self):
        self.policy = ZipsaConfig.get_policy("v3")
        # 올바른 DB를 사용하는지 확인
        self.db = MongoDBManager.get_v3_db() # 'cat_library'로 업데이트된 policy.db_name 사용
        self.collection = self.db[self.policy.collection_name]

    async def run(self, input_path: str):
        print(f"🚀 V3 데이터 로드 시작: {input_path}에서 읽는 중...")
        
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"입력 파일을 찾을 수 없습니다: {input_path}")
            
        with open(input_path, "rb") as f:
            items = pickle.load(f)
            
        print(f"📊 {len(items)}개의 문서를 {self.policy.db_name}.{self.policy.collection_name}에 로드 중...")
        
        # 인덱스 생성 필요시 매니저를 통하거나 존재 여부 확인 가능
        # 현재는 업서트로 직접 로드 수행
        
        for item in tqdm(items, desc="MongoDB로 로드 중"):
            # UID 기준으로 업서트 실행
            await self.collection.update_one(
                {"uid": item["uid"]},
                {"$set": item},
                upsert=True
            )
            
        print("✨ V3 로드 완료!")

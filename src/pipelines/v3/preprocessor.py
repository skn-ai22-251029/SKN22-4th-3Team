import os
import re
import json
from typing import List, Dict, Any
from tqdm import tqdm
from src.utils.text import tokenize_korean
from src.core.config import ZipsaConfig
from src.pipelines.base import BasePreprocessor

class V3Preprocessor(BasePreprocessor):
    def __init__(self):
        self.policy = ZipsaConfig.get_policy("v3")
        self.classifier = None # 초기화 시 API 키 요구를 피하기 위해 지연 로드 사용
        self.output_path = "data/v3/processed.json"
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', ' ', text)
        # 불필요한 공백 제거
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    async def _process_batch(self, batch: List[Dict[str, Any]], start_index: int) -> List[Dict[str, Any]]:
        if self.classifier is None:
            from src.pipelines.v3.classifier import V3Classifier
            self.classifier = V3Classifier()

        # 1. LLM 분류 실행
        metadata_results = await self.classifier.classify_batch(batch)
        
        processed_batch = []
        for i, (raw_item, meta) in enumerate(zip(batch, metadata_results)):
            uid = f"v3_{start_index + i:05d}"
            
            # 텍스트 클리닝
            clean_content = self.clean_text(raw_item.get("text", ""))
            
            # 형태소 분석 (제목 + 요약 + 본문 결합 후 수행)
            full_text_for_tokens = f"{meta['title_refined']} {meta['metadata']['summary']} {clean_content}"
            tokenized = tokenize_korean(full_text_for_tokens)
            
            doc = {
                "uid": uid,
                "title_refined": meta["title_refined"],
                "text": clean_content,
                "summary": meta["metadata"]["summary"],
                "keywords": meta["metadata"]["keywords"],
                "intent_tags": meta["metadata"]["intent_tags"],
                "categories": meta["categories"],
                "specialists": meta["specialists"],
                "tokenized_text": tokenized,
                "source": "bemypet_catlab",
                "original_url": raw_item.get("url", "")
            }
            processed_batch.append(doc)
        return processed_batch

    async def run(self, limit: int = None) -> str:
        print("🚀 V3 순수 전처리 시작 (Raw -> LLM)...")
        
        raw_path = "data/raw/bemypet_catlab.json"
        if not os.path.exists(raw_path):
            raise FileNotFoundError(f"원본 데이터를 찾을 수 없습니다: {raw_path}")

        with open(raw_path, "r", encoding="utf-8") as f:
            raw_items = json.load(f)

        if limit:
            raw_items = raw_items[:limit]

        processed_items = []
        batch_size = 5 # LLM 비용 및 속도 제한 관리
        
        print(f"📊 {len(raw_items)}개의 문서를 처리 중 (배치 크기: {batch_size})...")

        for i in tqdm(range(0, len(raw_items), batch_size), desc="V3 Preprocessing"):
            batch = raw_items[i : i + batch_size]
            processed_batch = await self._process_batch(batch, i)
            processed_items.extend(processed_batch)

        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(processed_items, f, ensure_ascii=False, indent=2)
            
        print(f"✨ {len(processed_items)}개의 항목을 {self.output_path}에 저장했습니다.")
        return self.output_path

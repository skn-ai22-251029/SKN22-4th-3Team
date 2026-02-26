import os
import json
import ssl
from kiwipiepy import Kiwi

# Kiwi 모델 다운로드를 위한 SSL 컨텍스트 수정 (기업/Mac 네트워크 환경 대응)
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# 싱글톤 인스턴스
_kiwi = None
_stopwords = set()
_synonyms = {}

# 핵심 리소스 경로 찾기 헬퍼
def _get_core_resource_path(filename: str) -> str:
    """실행 컨텍스트에 상관없이 src/core/tokenizer/에서 리소스를 찾습니다."""
    # 현재 파일(src/utils/text.py) 기준 상대 경로 시도
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prospective_path = os.path.join(current_dir, "../core/tokenizer", filename)
    if os.path.exists(prospective_path):
        return prospective_path
    
    # 작업 공간 절대 경로로 폴백
    return os.path.join("/Users/leemdo/Workspaces/SKN22-3rd-3Team/src/core/tokenizer", filename)

def get_kiwi():
    global _kiwi
    if _kiwi is None:
        _kiwi = Kiwi()
        # 사용자 사전 로드
        path = _get_core_resource_path("domain_dictionary.txt")
        if os.path.exists(path):
            print(f"📚 사용자 사전 로드 중: {path}")
            _kiwi.load_user_dictionary(path)
        else:
            print(f"⚠️ 경고: 사용자 사전을 찾을 수 없습니다: {path}")
    return _kiwi

def load_resources():
    """불용어, 유의어 등 외부 리소스를 로드합니다 (로드되지 않은 경우만)."""
    global _stopwords, _synonyms
    
    if not _stopwords:
        path = _get_core_resource_path("stopwords.txt")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                _stopwords = set(line.strip() for line in f if line.strip())
            print(f"🛑 {len(_stopwords)}개의 불용어를 {path}에서 로드했습니다.")
        else:
            print(f"⚠️ 경고: 불용어 파일을 찾을 수 없습니다: {path}")
    
    if not _synonyms:
        path = _get_core_resource_path("synonyms.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                grouped_data = json.load(f)
                
            # 계층 구조를 플랫하게 변환
            for standard_name, aliases in grouped_data.items():
                if isinstance(aliases, list):
                    for alias in aliases:
                        _synonyms[alias] = standard_name
                elif isinstance(aliases, str):
                    _synonyms[standard_name] = aliases
                        
            print(f"🔄 {len(_synonyms)}개의 유의어 매핑을 {path}에서 로드했습니다.")
        else:
            print(f"⚠️ 경고: 유의어 파일을 찾을 수 없습니다: {path}")

# 초기 로드 (선택 사항, 또는 tokenize에서 지연 로드)
# load_resources()

def tokenize_korean(text: str) -> str:
    """
    Kiwi(도메인 사전 포함)를 사용해 한국어 텍스트를 토큰화합니다.
    명사(NN*), 동사(VV), 형용사(VA), 어근(XR)을 추출합니다.
    불용어를 제거하고 유의어를 적용합니다.
    """
    if not text:
        return ""
        
    kiwi = get_kiwi()
    load_resources() # 리소스 로드 보장
    
    tokens = kiwi.tokenize(text)
    
    selected_tokens = []
    for t in tokens:
        # 태그 필터링: 명사, 동사, 형용사, 어근
        if t.tag.startswith(('N', 'V', 'XR')):
            # 불용어 필터링
            if t.form not in _stopwords:
                # 유의어 교체
                token_form = t.form
                if token_form in _synonyms:
                    token_form = _synonyms[token_form]
                    
                selected_tokens.append(token_form)
    
    return " ".join(selected_tokens)

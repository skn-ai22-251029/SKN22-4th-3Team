import requests
from typing import Optional, Dict, Any

class WikipediaAPI:
    """
    위키피디아 API 사용을 위한 간단한 래퍼입니다.
    """
    def __init__(self, language: str = 'en'):
        self.api_url = f"https://{language}.wikipedia.org/w/api.php"
        self.session = requests.Session()
        # 위키피디아는 User-Agent를 요구합니다.
        self.session.headers.update({
            "User-Agent": "CatBreedCrawler/1.0 (test@example.com)" 
        })

    def get_page_info(self, title: str) -> Optional[Dict[str, Any]]:
        """
        페이지 제목, 요약 정보(extract), URL, 마지막 업데이트 시간 등을 포함한 페이지 정보를 가져옵니다.
        
        Args:
            title: 검색할 페이지 제목
            
        Returns:
            페이지를 찾은 경우 'title', 'context', 'url', 'updated_at'을 포함한 딕셔너리, 그렇지 않으면 None 반환
        """
        params = {
            "action": "query",
            "format": "json",
            "prop": "extracts|info",
            "inprop": "url|displaytitle",
            "exintro": True,
            "explaintext": True,
            "redirects": 1,
            "titles": title
        }

        try:
            response = self.session.get(self.api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            pages = data.get("query", {}).get("pages", {})
            if not pages:
                return None
            
            # API는 페이지 ID를 키로 하는 페이지들을 반환합니다. -1은 누락을 의미합니다.
            for page_id, page_data in pages.items():
                if page_id == "-1":
                    return None
                
                return {
                    "title": page_data.get("title"),
                    "context": page_data.get("extract"),
                    "url": page_data.get("fullurl"),
                    "updated_at": page_data.get("touched")
                }
                
        except requests.RequestException as e:
            print(f"{title} 데이터 검색 중 오류 발생: {e}")
            return None
            
        return None

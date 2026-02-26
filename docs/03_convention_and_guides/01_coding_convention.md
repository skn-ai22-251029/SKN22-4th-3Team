# 01. Coding Convention

이 문서는 프로젝트의 코드 일관성과 품질을 유지하기 위한 Python 코딩 가이드를 정의합니다.

## 1. Python Code Style
기본적으로 **[PEP 8](https://peps.python.org/pep-0008/)** 스타일 가이드를 준수합니다.

### 1.1 들여쓰기 (Indentation)
- 공백(Space) 2칸을 사용합니다.
- 탭(Tab) 사용은 금지합니다.

### 1.2 최대 줄 길이 (Line Length)
- 한 줄은 최대 **88자** (Black 기본값) 또는 120자 이내로 작성합니다.
- 가독성을 위해 적절한 줄 바꿈을 권장합니다.

### 1.3 Import
- Import 순서는 다음과 같이 그룹화하여 공백으로 구분합니다:
    1. 표준 라이브러리 (e.g., `os`, `sys`)
    2. 서드파티 라이브러리 (e.g., `pandas`, `langchain`)
    3. 로컬 애플리케이션/라이브러리 (e.g., `src.core`)
- 와일드카드 import (`from module import *`)는 지양합니다.

```python
# Good
import os
import sys

import pandas as pd
from langchain.chat_models import ChatOpenAI

from src.core.config import settings
```

## 2. Naming Convention
명확하고 의도를 알 수 있는 이름을 사용합니다.

- **변수명 (Variable)**: `snake_case`
    - `user_name`, `cat_breed`
- **함수명 (Function)**: `snake_case`
    - `calculate_age()`, `fetch_data()`
- **클래스명 (Class)**: `PascalCase`
    - `UserProfile`, `ChatAgent`
- **상수명 (Constant)**: `UPPER_CASE`
    - `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT`
- **파일명 (File)**: `snake_case`
    - `user_profile.py`, `utils.py`

## 3. Docstrings
모든 공개 모듈, 함수, 클래스, 메서드에는 Docstring을 작성해야 합니다.
**Google Style**을 권장합니다.

```python
def fetch_user_data(user_id: str) -> dict:
    """사용자의 ID를 기반으로 사용자 데이터를 조회합니다.

    Args:
        user_id (str): 조회할 사용자의 고유 ID.

    Returns:
        dict: 사용자 데이터를 포함하는 딕셔너리. 데이터가 없으면 빈 딕셔너리 반환.

    Raises:
        ValueError: user_id가 유효하지 않은 형식일 경우.
    """
    ...
```



## 4. Type Hinting
Python 3.5+의 타입 힌트를 적극적으로 사용합니다.

```python
# Good
def greet(name: str, age: int) -> str:
    return f"Hello {name}, you are {age} years old."
```

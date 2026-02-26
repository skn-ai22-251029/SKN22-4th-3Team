# 04. Environment & Secrets

프로젝트 실행에 필요한 환경 변수와 보안 민감 정보(Secrets)를 관리하는 방법입니다.

## 1. `.env` 파일
이 프로젝트는 `.env.example` 파일을 제공합니다.
설정값은 로컬의 `.env` 파일에 저장하며, 이 파일은 **절대로 Git에 커밋하지 않습니다**.

### 1.1 설정 방법
1. `.env.example` 파일을 복사하여 `.env` 파일을 생성합니다.
   ```bash
   cp .env.example .env
   ```
2. `.env` 파일을 열어 실제 값을 입력합니다.

### 1.2 주요 환경 변수
```ini
# OpenAI API Key
OPENAI_API_KEY=sk-...

# LangSmith (Tracing, Optional)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls-...

# Database (MongoDB)
MONGODB_URI=mongodb+srv://...
DB_NAME=zipsa_db
```

## 2. 보안 원칙 (Security)
- **API Key 노출 금지**: 코드 내에 하드코딩하지 않습니다. 반드시 환경 변수로 관리하세요.
- **GitHub 업로드 주의**: 실수로 `.env` 파일을 커밋했다면, 즉시 해당 Key를 폐기(Revoke)하고 재발급 받아야 합니다.
- **`.gitignore` 확인**: `.env`, `venv/`, `__pycache__/` 등이 `.gitignore`에 포함되어 있는지 항상 확인합니다.

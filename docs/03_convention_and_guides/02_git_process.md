# 02. Git Process

이 문서는 효율적인 협업을 위한 Git 브랜치 전략과 커밋 컨벤션을 정의합니다.

## 1. Branching Strategy
우리는 **Feature Branch Workflow**를 따릅니다.
`main` 브랜치는 항상 배포 가능한 상태를 유지해야 하며, 모든 작업은 별도의 브랜치에서 진행된 후 Pull Request(PR)를 통해 병합됩니다.

### 1.1 브랜치 종류
- **main**: 제품으로 배포되는 기준 브랜치입니다. 직접 커밋(Push)은 금지되며 PR로만 병합 가능합니다.
- **feature/**: 새로운 기능 개발을 위한 브랜치입니다.
- **fix/**: 버그 수정을 위한 브랜치입니다.
- **docs/**: 문서 작업을 위한 브랜치입니다.
- **refactor/**: 코드 리팩토링을 위한 브랜치입니다.

### 1.2 작업 흐름 (Workflow)
1. `main` 브랜치에서 최신 코드를 pull 합니다: `git pull origin main`
2. 작업 브랜치를 생성합니다: `git checkout -b feature/login-page`
3. 작업을 진행하고 커밋합니다.
4. 원격 저장소에 브랜치를 push 합니다: `git push origin feature/login-page`
5. GitHub에서 `main` 브랜치로 **Pull Request**를 생성합니다.
6. 리뷰어의 승인을 받은 후 Merge 합니다.

## 2. Commit Message Convention
**[Conventional Commits](https://www.conventionalcommits.org/)** 규칙을 따릅니다.
커밋 메시지는 `<type>: <description>` 형식을 기본으로 합니다.

### 2.1 Type 종류
- **feat**: 새로운 기능 추가
- **fix**: 버그 수정
- **docs**: 문서 수정
- **style**: 코드 포맷팅, 세미콜론 누락 등 (코드 변경 없음)
- **refactor**: 코드 리팩토링 (기능 변경 없음)
- **test**: 테스트 코드 추가/수정
- **chore**: 빌드 업무 수정, 패키지 매니저 수정 등

### 2.2 작성 예시
```text
feat: 사용자 로그인 API 구현
fix: 채팅 응답이 느린 문제 해결 (Timeour 30s -> 60s)
docs: README.md에 설치 가이드 추가
refactor: User 클래스 상속 구조 개선
```

### 2.3 규칙
- 제목은 50자 이내로 간결하게 작성합니다.
- 본문이 필요한 경우 한 줄 띄우고 상세 내용을 작성합니다.
- 한글 작성을 원칙으로 하되, 팀 내 합의에 따라 영문도 병기 가능합니다.

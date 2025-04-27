# GitHub 릴리스 생성 가이드

이 문서는 GitHub에서 릴리스를 생성하는 방법을 안내합니다.

## 릴리스 태그 생성 방법

### 1. GitHub 저장소 페이지로 이동

- 브라우저에서 GitHub 저장소 페이지로 이동합니다.
- 예: `https://github.com/yourusername/html-to-ghost`

### 2. Releases 섹션으로 이동

- 저장소 페이지에서 오른쪽 사이드바의 "Releases" 링크를 클릭합니다.
- 또는 URL에 `/releases`를 추가하여 직접 이동할 수 있습니다.
- 예: `https://github.com/yourusername/html-to-ghost/releases`

### 3. "Create a new release" 버튼 클릭

- Releases 페이지에서 "Create a new release" 또는 "Draft a new release" 버튼을 클릭합니다.

### 4. 릴리스 정보 입력

- **Choose a tag**: `v1.0.0`을 입력합니다. 이 태그가 존재하지 않는 경우 "Create new tag: v1.0.0" 옵션이 표시됩니다.
- **Target**: 일반적으로 `main` 또는 `master` 브랜치를 선택합니다.
- **Release title**: "v1.0.0 - 초기 릴리스"와 같은 제목을 입력합니다.
- **Description**: CHANGELOG.md의 내용을 복사하여 붙여넣습니다.

### 5. 릴리스 파일 첨부 (선택 사항)

- 필요한 경우 바이너리 파일이나 소스 코드 아카이브를 첨부할 수 있습니다.
- "Attach binaries by dropping them here or selecting them" 영역을 클릭하여 파일을 선택합니다.

### 6. 릴리스 생성

- 모든 정보를 입력한 후 "Publish release" 버튼을 클릭합니다.
- 나중에 수정하려면 "Save draft" 버튼을 클릭하여 초안으로 저장할 수 있습니다.

## 릴리스 노트 예시

```markdown
## [1.0.0] - 2025-04-27

### 추가

- HTML 파일을 Ghost 블로그 JSON 형식으로 변환하는 기능
- 이미지 파일 처리 및 압축 기능
- 태그 정보 추출 및 관계 설정 기능
- JSON 데이터 정제 기능
- 연도별 처리 기능
- 샘플 파일 생성 기능

### 개선

- 기존 `convert_to_ghost_by_year.py`와 `clean_json.py`의 기능을 통합
- Ghost 블로그 JSON 형식에 맞게 태그 누락 문제 해결
- 명령행 인터페이스 개선

### 기술적 세부 사항

- Ghost 블로그 4.0.0 버전의 JSON 형식 지원
- BeautifulSoup4를 사용한 HTML 파싱
- Pillow를 사용한 이미지 압축
- 다양한 경로에서 이미지 파일 찾기 알고리즘 구현
- 태그 추출 로직 개선 (backup_post_tags 클래스, 시리즈 제목, 본문 해시태그)
```

## 릴리스 후 작업

1. 릴리스가 성공적으로 생성되었는지 확인합니다.
2. 릴리스 페이지에서 릴리스 URL을 복사하여 필요한 곳에 공유합니다.
3. 다음 개발 주기를 위해 CHANGELOG.md 파일에 새로운 "Unreleased" 섹션을 추가할 수 있습니다.

## 참고 자료

- [GitHub 릴리스 관리 공식 문서](https://docs.github.com/ko/repositories/releasing-projects-on-github/managing-releases-in-a-repository)
- [Semantic Versioning](https://semver.org/lang/ko/)
- [Keep a Changelog](https://keepachangelog.com/ko/1.0.0/)

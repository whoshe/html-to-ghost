# Changelog

모든 주요 변경 사항이 이 파일에 기록됩니다.

형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.0.0/)를 기반으로 하며,
이 프로젝트는 [Semantic Versioning](https://semver.org/lang/ko/)을 준수합니다.

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

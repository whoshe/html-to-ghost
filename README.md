# HTML to Ghost Blog JSON Converter

네이버 포스트 HTML 백업 파일을 Ghost 블로그 플랫폼의 JSON 형식으로 변환하는 도구입니다.

## 프로젝트 소개

이 프로젝트는 네이버 포스트에서 백업한 HTML 파일을 Ghost 블로그 플랫폼에서 사용할 수 있는 JSON 형식으로 변환합니다. 이 도구를 사용하면 네이버 포스트 콘텐츠를 Ghost 블로그로 쉽게 마이그레이션할 수 있습니다.

### 주요 기능

- HTML 파일에서 제목, 날짜, 태그, 본문 내용 추출
- 이미지 파일 처리 및 압축
- Ghost 블로그 JSON 형식으로 변환
- 태그 정보 처리 및 관계 설정
- JSON 데이터 정제

## 소스 코드 구성

- `html_to_ghost.py`: HTML 파일을 Ghost 블로그 JSON 형식으로 변환하는 통합 스크립트
- `convert_to_ghost_by_year.py`: 기존 변환 스크립트 (참고용)
- `clean_json.py`: 기존 JSON 정제 스크립트 (참고용)

## 설치 방법

### 요구 사항

- Python 3.6 이상
- 필요한 패키지: BeautifulSoup4, Pillow

### 설치

1. 저장소 클론 또는 다운로드:

```bash
git clone https://github.com/yourusername/html-to-ghost.git
cd html-to-ghost
```

2. 필요한 패키지 설치:

```bash
pip install beautifulsoup4 pillow
```

## 사용 방법

### 기본 사용법

```bash
python3 html_to_ghost.py
```

이 명령은 현재 디렉토리에서 `POST_ARTICLE_` 패턴을 가진 모든 폴더를 찾아 HTML 파일을 처리합니다.

### 명령어 옵션

```
usage: html_to_ghost.py [-h] [--input INPUT] [--output OUTPUT] [--year YEAR] [--clean-only] [--sample SAMPLE]

HTML 파일을 Ghost 블로그 JSON 형식으로 변환

optional arguments:
  -h, --help            도움말 표시
  --input INPUT, -i INPUT
                        입력 디렉토리 (지정하지 않으면 모든 POST_ARTICLE_XXX 폴더 처리)
  --output OUTPUT, -o OUTPUT
                        출력 디렉토리 (기본값: ghost_export_final)
  --year YEAR, -y YEAR  특정 연도만 처리 (예: 2016)
  --clean-only, -c      기존 JSON 파일만 정제
  --sample SAMPLE, -s SAMPLE
                        샘플 파일 생성 (HTML 파일 경로 지정)
```

### 사용 예제

1. 특정 디렉토리의 HTML 파일 처리:

```bash
python3 html_to_ghost.py --input POST_ARTICLE_001
```

2. 특정 연도의 포스트만 처리:

```bash
python3 html_to_ghost.py --year 2016
```

3. 출력 디렉토리 지정:

```bash
python3 html_to_ghost.py --output my_ghost_export
```

4. 기존 JSON 파일 정제:

```bash
python3 html_to_ghost.py --clean-only
```

5. 샘플 파일 생성:

```bash
python3 html_to_ghost.py --sample POST_ARTICLE_001/20160202_3509403_수다쟁이오리와무뚝뚝한곰곰아놀자.html
```

## 변환 결과 예시

### 샘플 HTML 파일

`POST_ARTICLE_001/20160202_3509403_수다쟁이오리와무뚝뚝한곰곰아놀자.html` 파일을 변환한 결과입니다.

#### 원본 HTML 파일 구조

- 제목: "수다쟁이 오리와 무뚝뚝한 곰 '곰아 놀자!'"
- 날짜: "2016.02.02. 16:24"
- 태그: #동네서점β, #동네서점, #여자, #페미니즘, #책추천, #그림책, #그림책추천, #프레드릭, #오나의책방
- 본문: HTML 형식의 블로그 포스트 내용
- 이미지: 7개의 이미지 파일

#### 변환된 JSON 구조

```json
{
  "db": [
    {
      "meta": {
        "exported_on": 1745714947206,
        "version": "4.0.0"
      },
      "data": {
        "posts": [
          {
            "id": "UUID",
            "title": "수다쟁이 오리와 무뚝뚝한 곰 '곰아 놀자!'",
            "slug": "수다쟁이-오리와-무뚝뚝한-곰-곰아-놀자",
            "mobiledoc": null,
            "html": "HTML 콘텐츠",
            "feature_image": "/content/images/2016/UUID.jpg",
            "featured": false,
            "status": "published",
            "published_at": "2016-02-02T16:24:00Z",
            "created_at": "2016-02-02T16:24:00Z",
            "updated_at": "2016-02-02T16:24:00Z"
          }
        ],
        "tags": [
          {
            "id": 1,
            "name": "동네서점β",
            "slug": "동네서점β",
            "description": ""
          },
          {
            "id": 2,
            "name": "동네서점",
            "slug": "동네서점",
            "description": ""
          }
          // 추가 태그들...
        ],
        "posts_tags": [
          {
            "post_id": "UUID",
            "tag_id": 1
          },
          {
            "post_id": "UUID",
            "tag_id": 2
          }
          // 추가 포스트-태그 관계...
        ]
      }
    }
  ]
}
```

### 실제 운영 중인 Ghost 블로그 예시

이 도구를 사용하여 변환된 실제 Ghost 블로그 포스트 예시:

- [수다쟁이 오리와 무뚝뚝한 곰 '곰아 놀자!'](https://blog.bookshopmap.com/sudajaengi-oriwa-muddugddughan-gom-goma-nolja)

## 주의사항 및 제한사항

1. **이미지 처리**: 이미지 파일은 다양한 경로에서 찾기를 시도합니다. 이미지를 찾을 수 없는 경우 해당 이미지는 건너뜁니다.

2. **HTML 구조**: 네이버 포스트의 HTML 구조가 변경된 경우 추출 로직이 제대로 작동하지 않을 수 있습니다.

3. **태그 처리**: 태그는 HTML 파일의 `backup_post_tags` 클래스, 시리즈 제목, 본문 내용에서 해시태그를 추출합니다.

4. **이미지 압축**: 이미지 파일이 1MB를 초과하는 경우 자동으로 압축합니다. 압축 품질은 최대 90%에서 시작하여 필요에 따라 낮아집니다.

5. **Ghost 버전 호환성**: 이 도구는 Ghost 4.0.0 버전의 JSON 형식을 기준으로 작성되었습니다. 다른 버전의 Ghost에서는 호환성 문제가 발생할 수 있습니다.

## 문제 해결

### 일반적인 문제

1. **이미지를 찾을 수 없음**

   - 이미지 파일이 예상 경로에 있는지 확인하세요.
   - 이미지 파일명이 예상 패턴과 일치하는지 확인하세요.

2. **태그가 추출되지 않음**

   - HTML 파일에 태그 정보가 포함되어 있는지 확인하세요.
   - 태그 추출 로직을 수정하여 다른 방식으로 태그를 추출해 보세요.

3. **변환된 JSON 파일이 Ghost에서 가져오기 실패**
   - JSON 파일 형식이 Ghost 버전과 호환되는지 확인하세요.
   - JSON 파일의 구조가 올바른지 확인하세요.

### 디버깅 팁

- `--sample` 옵션을 사용하여 단일 HTML 파일에 대한 변환 결과를 확인하세요.
- 로그 메시지를 확인하여 변환 과정에서 발생하는 문제를 파악하세요.
- 필요한 경우 코드를 수정하여 특정 HTML 구조에 맞게 추출 로직을 조정하세요.

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 기여

버그 신고, 기능 요청, 코드 기여는 언제나 환영합니다. GitHub 이슈 또는 풀 리퀘스트를 통해 참여해 주세요.

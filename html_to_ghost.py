#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
import uuid
import time
import shutil
import argparse
from datetime import datetime
from bs4 import BeautifulSoup
from PIL import Image

def parse_date(date_str):
    """네이버 포스트 날짜 문자열을 파싱하여 ISO 형식으로 변환"""
    # 예: "2016.02.02. 16:24"
    match = re.search(r'(\d{4})\.(\d{2})\.(\d{2})\. (\d{2}):(\d{2})', date_str)
    if match:
        year, month, day, hour, minute = map(int, match.groups())
        dt = datetime(year, month, day, hour, minute)
        return dt.isoformat() + 'Z'
    return datetime.now().isoformat() + 'Z'

def create_slug(text):
    """텍스트를 URL 슬러그로 변환"""
    # 원본 텍스트 보존 (디버깅용)
    original = text
    
    # 한글, 영문, 숫자, 공백만 남기고 나머지 제거
    slug = re.sub(r'[^\w\s가-힣]', '', text)
    
    # 공백을 하이픈으로 변환
    slug = re.sub(r'\s+', '-', slug.strip())
    
    # 디버깅 출력
    print(f"원본: '{original}' -> 슬러그: '{slug}'")
    
    return slug.lower()

def compress_image(image_path, output_path, max_size_mb=1):
    """이미지 압축 (1MB 이상인 경우)"""
    try:
        # 이미지 파일이 존재하는지 확인
        if not os.path.exists(image_path):
            print(f"Warning: Image file not found: {image_path}")
            return False
        
        # 현재 파일 크기 확인
        current_size = os.path.getsize(image_path) / (1024 * 1024)  # MB 단위
        
        if current_size <= max_size_mb:
            # 이미 1MB 이하면 그대로 복사
            shutil.copy2(image_path, output_path)
            return True
        
        # 이미지 열기
        img = Image.open(image_path)
        
        # 압축 시도
        quality = 90
        while quality > 30:  # 최소 품질 제한
            img.save(output_path, quality=quality, optimize=True)
            if os.path.getsize(output_path) / (1024 * 1024) <= max_size_mb:
                return True
            quality -= 10
        
        # 품질을 낮춰도 1MB를 초과하는 경우 크기 조정
        width, height = img.size
        ratio = 0.9  # 10% 축소
        
        while ratio > 0.5:  # 최소 50%까지 축소
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            resized_img = img.resize((new_width, new_height), Image.LANCZOS)
            resized_img.save(output_path, quality=quality, optimize=True)
            
            if os.path.getsize(output_path) / (1024 * 1024) <= max_size_mb:
                return True
            
            ratio -= 0.1
        
        # 최대한 압축했지만 여전히 1MB 초과하는 경우
        print(f"Warning: Could not compress image below 1MB: {image_path}")
        shutil.copy2(image_path, output_path)
        return True
    
    except Exception as e:
        print(f"Error compressing image {image_path}: {e}")
        return False

def extract_tags_from_html(html_content):
    """HTML 내용에서 태그 추출"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 태그 추출 방법 1: backup_post_tags 클래스에서 추출
    tags_div = soup.find('div', class_='backup_post_tags')
    if tags_div:
        tag_spans = tags_div.find_all('span', class_='backup_post_tag')
        tags = [span.text.strip().replace('#', '') for span in tag_spans]
        return tags
    
    # 태그 추출 방법 2: 시리즈 제목에서 추출
    series_title = soup.find('div', class_='backup_post_series_title')
    if series_title and series_title.text:
        return [series_title.text.strip().replace('#', '')]
    
    # 태그 추출 방법 3: 본문 내용에서 해시태그 추출
    content_divs = soup.find_all('div', class_='se2_in_page')
    if content_divs:
        hashtag_pattern = r'#([^\s#]+)'
        all_text = ' '.join([div.get_text() for div in content_divs])
        hashtags = re.findall(hashtag_pattern, all_text)
        if hashtags:
            return hashtags
    
    return []

def process_html_file(html_file, output_dir):
    """HTML 파일 처리"""
    try:
        # 파일명에서 정보 추출
        filename = os.path.basename(html_file)
        match = re.match(r'(\d+)_(\d+)_(.+)\.html', filename)
        if not match:
            print(f"Warning: Could not parse filename: {filename}")
            return None
        
        date_str, post_id, title_slug = match.groups()
        print(f"파일명 파싱: {date_str}, {post_id}, {title_slug}")
        
        # HTML 파일 읽기
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print(f"HTML 파일 크기: {len(html_content)} 바이트")
        
        # HTML 파싱
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 제목 추출 (여러 방법 시도)
        title = title_slug  # 기본값으로 파일명에서 추출한 제목 사용
        
        # 방법 1: h3 태그에서 찾기
        title_tag = soup.find('h3')
        if title_tag:
            title = title_tag.text
        else:
            # 방법 2: se_sectionTitle 클래스의 h5 태그에서 찾기
            title_h5 = soup.find('h5', class_='se_textarea')
            if title_h5:
                # HTML 주석 처리 (<!-- SE3-TEXT { -->내용<!-- } SE3-TEXT -->)
                title_text = title_h5.text
                if '<!-- SE3-TEXT { -->' in title_text and '<!-- } SE3-TEXT -->' in title_text:
                    title = title_text.split('<!-- SE3-TEXT { -->')[1].split('<!-- } SE3-TEXT -->')[0]
                else:
                    title = title_text
            else:
                # 방법 3: se_card_titleView 클래스의 div 안에서 찾기
                title_div = soup.find('div', class_='se_card_titleView')
                if title_div:
                    title_h5 = title_div.find('h5')
                    if title_h5:
                        title = title_h5.text
        
        print(f"제목: {title}")
        
        # 날짜 추출 (여러 방법 시도)
        date_text = ''
        
        # 방법 1: border-bottom: solid 스타일을 가진 div에서 찾기
        date_div = soup.find('div', style=lambda s: s and 'border-bottom: solid' in s)
        if date_div:
            date_text = date_div.text
        else:
            # 방법 2: se_publishDate 클래스를 가진 span에서 찾기
            date_span = soup.find('span', class_='se_publishDate')
            if date_span:
                date_text = date_span.text
            else:
                # 방법 3: 파일명에서 날짜 추출 (20160202 -> 2016.02.02)
                if date_str and len(date_str) >= 8:
                    year = date_str[:4]
                    month = date_str[4:6]
                    day = date_str[6:8]
                    date_text = f"{year}.{month}.{day}. 00:00"
        
        print(f"날짜: {date_text}")
        
        # 태그 추출
        tags = extract_tags_from_html(html_content)
        print(f"추출된 태그: {tags}")
        
        # 본문 내용 추출 (여러 클래스 시도)
        content_divs = []
        
        # 방법 1: se2_in_page 클래스의 div 찾기 (기존 방식)
        se2_divs = soup.find_all('div', class_='se2_in_page')
        if se2_divs:
            content_divs = se2_divs
            print(f"se2_in_page div 수: {len(content_divs)}")
        
        # 방법 2: se_textView 클래스의 div 찾기
        if not content_divs:
            se_textview_divs = soup.find_all('div', class_='se_textView')
            if se_textview_divs:
                content_divs = se_textview_divs
                print(f"se_textView div 수: {len(content_divs)}")
        
        # 방법 3: se_component_wrap 클래스의 div 찾기 (이미지 포함 가능성 높음)
        if not content_divs:
            se_component_divs = soup.find_all('div', class_='se_component_wrap')
            if se_component_divs:
                content_divs = se_component_divs
                print(f"se_component_wrap div 수: {len(content_divs)}")
        
        # 방법 4: se_card 클래스의 div 찾기 (이미지 카드 포함)
        if not content_divs:
            se_card_divs = soup.find_all('div', class_='se_card')
            if se_card_divs:
                content_divs = se_card_divs
                print(f"se_card div 수: {len(content_divs)}")
        
        # 방법 5: se_textarea 클래스의 p 태그 직접 찾기
        if not content_divs:
            p_tags = soup.find_all('p', class_='se_textarea')
            if p_tags:
                print(f"se_textarea p 태그 수: {len(p_tags)}")
                # p 태그를 div로 감싸서 content_divs에 추가
                content_div = soup.new_tag('div')
                for p in p_tags:
                    content_div.append(p)
                content_divs = [content_div]
        
        # 방법 6: 본문 영역으로 추정되는 div 찾기 (마지막 수단)
        if not content_divs:
            # 본문 영역으로 추정되는 div 찾기 (예: 큰 div 중에서 이미지나 텍스트가 많은 div)
            main_content_div = None
            max_content_length = 0
            
            for div in soup.find_all('div'):
                # div 내의 텍스트 및 이미지 태그 수 확인
                text_length = len(div.get_text())
                img_count = len(div.find_all('img'))
                content_length = text_length + img_count * 100  # 이미지에 가중치 부여
                
                if content_length > max_content_length:
                    max_content_length = content_length
                    main_content_div = div
            
            if main_content_div:
                content_divs = [main_content_div]
                print(f"본문 영역으로 추정되는 div 찾음 (텍스트 길이: {len(main_content_div.get_text())}, 이미지 수: {len(main_content_div.find_all('img'))})")
        
        print(f"최종 선택된 본문 div 수: {len(content_divs)}")
        
        # 이미지 태그 처리
        first_image = None
        first_image_path = None
        images = []
        
        # 1. 본문 div에서 이미지 태그 찾기
        content_img_tags = []
        for div in content_divs:
            content_img_tags.extend(div.find_all('img'))
        
        # 2. 본문 div에서 이미지를 찾지 못한 경우, 전체 HTML에서 이미지 태그 찾기
        if not content_img_tags:
            print("본문 div에서 이미지를 찾지 못했습니다. 전체 HTML에서 이미지 태그를 찾습니다.")
            content_img_tags = soup.find_all('img')
        
        print(f"처리할 이미지 태그 수: {len(content_img_tags)}")
        
        # 이미지 태그 처리
        for img in content_img_tags:
            if 'src' in img.attrs:
                    # 원본 이미지 경로
                    src = img['src']
                    print(f"이미지 src: {src}")
                    
                    # 이미지 파일명 추출
                    if src.startswith('image/'):
                        img_filename = os.path.basename(src)
                        print(f"이미지 파일명(image/ 시작): {img_filename}")
                    else:
                        # 이미지 ID 추출 시도
                        img_id_match = re.search(r'data-image-id="(\d+)_(\d+)"', str(img))
                        if img_id_match:
                            section_id, img_id = img_id_match.groups()
                            img_filename = f"{date_str}_{post_id}_{section_id}_{img_id}.jpg"
                            print(f"이미지 파일명(ID 추출): {img_filename}")
                        else:
                            # 고유한 이미지 파일명 생성
                            img_filename = f"{date_str}_{post_id}_{uuid.uuid4().hex}.jpg"
                            print(f"이미지 파일명(UUID 생성): {img_filename}")
                    
                    # 원본 이미지 경로 시도 (여러 가능한 경로)
                    possible_paths = [
                        # 1. HTML 파일과 같은 디렉토리의 image 폴더
                        os.path.join(os.path.dirname(html_file), 'image', f"{date_str}_{post_id}", img_filename),
                        # 2. 현재 작업 디렉토리의 image 폴더
                        os.path.join('image', f"{date_str}_{post_id}", img_filename),
                        # 3. 원본 src 경로 그대로 시도
                        src if os.path.isabs(src) else os.path.join(os.path.dirname(html_file), src),
                        # 4. POST_ARTICLE_001/image 폴더
                        os.path.join('POST_ARTICLE_001', 'image', f"{date_str}_{post_id}", img_filename),
                        # 5. 이미지 ID 기반 경로
                        os.path.join(os.path.dirname(html_file), 'image', f"{date_str}_{post_id}", f"{section_id}_{img_id}.jpg") if 'section_id' in locals() else None,
                        os.path.join('image', f"{date_str}_{post_id}", f"{section_id}_{img_id}.jpg") if 'section_id' in locals() else None,
                        # 6. 파일명만 사용
                        os.path.join(os.path.dirname(html_file), 'image', f"{date_str}_{post_id}", os.path.basename(src)),
                        os.path.join('image', f"{date_str}_{post_id}", os.path.basename(src)),
                        # 7. 사용자가 제공한 형식 (image/20160414_3999621/20160414_3999621_1.JPEG)
                        os.path.join('image', f"{date_str}_{post_id}", f"{date_str}_{post_id}_1.JPEG"),
                        os.path.join('image', f"{date_str}_{post_id}", f"{date_str}_{post_id}_1.jpeg"),
                        os.path.join('image', f"{date_str}_{post_id}", f"{date_str}_{post_id}_1.jpg"),
                        os.path.join('image', f"{date_str}_{post_id}", f"{date_str}_{post_id}_1.JPG"),
                        os.path.join('image', f"{date_str}_{post_id}", f"{date_str}_{post_id}_1.png"),
                        os.path.join('image', f"{date_str}_{post_id}", f"{date_str}_{post_id}_1.PNG"),
                        # 8. 상위 디렉토리의 image 폴더
                        os.path.join(os.path.dirname(os.path.dirname(html_file)), 'image', f"{date_str}_{post_id}", img_filename),
                        os.path.join(os.path.dirname(os.path.dirname(html_file)), 'image', f"{date_str}_{post_id}", f"{date_str}_{post_id}_1.jpg"),
                        # 9. 추가 이미지 번호 시도 (1~5)
                        os.path.join('image', f"{date_str}_{post_id}", f"{date_str}_{post_id}_2.jpg"),
                        os.path.join('image', f"{date_str}_{post_id}", f"{date_str}_{post_id}_3.jpg"),
                        os.path.join('image', f"{date_str}_{post_id}", f"{date_str}_{post_id}_4.jpg"),
                        os.path.join('image', f"{date_str}_{post_id}", f"{date_str}_{post_id}_5.jpg"),
                        # 10. 다른 확장자 시도
                        os.path.join('image', f"{date_str}_{post_id}", f"{date_str}_{post_id}.jpg"),
                        os.path.join('image', f"{date_str}_{post_id}", f"{date_str}_{post_id}.png"),
                        os.path.join('image', f"{date_str}_{post_id}", f"{date_str}_{post_id}.gif"),
                        # 11. 상위 디렉토리에서 이미지 폴더 직접 시도
                        os.path.join('image', f"{date_str}_{post_id}", img_filename),
                    ]
                    
                    # 가능한 경로 중 존재하는 첫 번째 경로 사용
                    original_img_path = None
                    for path in possible_paths:
                        if path and os.path.exists(path):
                            original_img_path = path
                            print(f"이미지 파일 발견: {path}")
                            break
                    
                    if not original_img_path:
                        print(f"이미지 파일을 찾을 수 없음: {img_filename}")
                        print("시도한 경로:")
                        for path in possible_paths:
                            if path:
                                print(f"  - {path}")
                    
                    # 연도 추출 (date_str에서 첫 4자리)
                    year = date_str[:4]
                    
                    # Ghost 블로그용 이미지 경로 (연도별 폴더 추가)
                    ghost_img_filename = f"{date_str}_{post_id}_{uuid.uuid4().hex}.jpg"
                    year_images_dir = os.path.join(output_dir, 'images', year)
                    
                    # 연도별 이미지 디렉토리 생성
                    os.makedirs(year_images_dir, exist_ok=True)
                    
                    ghost_img_path = os.path.join(year_images_dir, ghost_img_filename)
                    
                    # 이미지 압축 및 복사
                    if original_img_path and os.path.exists(original_img_path):
                        compress_image(original_img_path, ghost_img_path)
                        
                        # 이미지 경로 수정 (연도 정보 추가)
                        img['src'] = f"/content/images/{year}/{ghost_img_filename}"
                        
                        # 이미지 정보 저장
                        images.append({
                            'original_path': original_img_path,
                            'ghost_path': ghost_img_path,
                            'ghost_url': f"/content/images/{year}/{ghost_img_filename}"
                        })
                        
                        # 첫 번째 이미지 저장
                        if first_image is None:
                            first_image = img
                            first_image_path = f"/content/images/{year}/{ghost_img_filename}"
                    else:
                        print(f"Warning: Image file not found: {original_img_path}")
        
        # 본문 HTML 생성 - 이미지 경로 변환에 집중
        # 이미지 태그가 본문에 포함되어 있는지 확인
        has_images_in_content = any('<img' in str(div) for div in content_divs)
        
        # 본문 HTML 생성
        content_html = ''.join(str(div) for div in content_divs)
        
        # 이미지가 본문에 없지만 이미지가 발견된 경우, 이미지를 본문에 추가
        if not has_images_in_content and images:
            print("본문 HTML에 이미지 태그가 없지만 이미지가 발견되었습니다. 이미지를 본문에 추가합니다.")
            
            # 이미지 HTML 생성
            image_html = "<div class='ghost-image-container'>\n"
            for img_info in images:
                image_html += f'<div><img src="{img_info["ghost_url"]}" alt="{title}" class="ghost-image"></div>\n'
            image_html += "</div>\n"
            
            # 기존 본문 HTML에 이미지 HTML 추가
            content_html += image_html
            
            print(f"이미지 {len(images)}개를 본문에 추가했습니다.")
        
        # Ghost 블로그 포스트 데이터 생성
        post_data = {
            'title': title,
            'date': date_text,
            'tags': tags,  # 추출된 태그 목록
            'content': content_html,
            'feature_image': first_image_path,
            'images': images,
            'slug': create_slug(title),
            'id': str(uuid.uuid4()),
            'published_at': parse_date(date_text)
        }
        
        return post_data
    
    except Exception as e:
        print(f"Error processing HTML file {html_file}: {e}")
        return None

def clean_text(text):
    """
    텍스트에서 줄바꿈(\n)과 백슬래시(\) 제거 및 중복 공백 제거
    """
    if not isinstance(text, str):
        return text
    
    # 줄바꿈과 백슬래시 제거
    text = text.replace('\\n', '').replace('\\', '')
    
    # 두 번 이상 연속으로 반복되는 공백 제거 (단일 공백으로 대체)
    text = re.sub(r'\s{2,}', ' ', text)
    
    return text

def clean_html(html):
    """
    HTML 본문에서 줄바꿈(\n)과 백슬래시(\) 제거 및 중복 공백 제거
    HTML 태그 내부 구조는 유지
    """
    if not isinstance(html, str):
        return html
    
    # 실제 줄바꿈 문자 제거
    html = re.sub(r'\n', '', html)
    
    # 두 번 이상 연속으로 반복되는 공백 제거 (단일 공백으로 대체)
    html = re.sub(r'\s{2,}', ' ', html)
    
    return html

def clean_json_data(data):
    """JSON 데이터 정제"""
    if 'db' in data and len(data['db']) > 0 and 'data' in data['db'][0]:
        db_data = data['db'][0]['data']
        
        # posts 배열이 있는지 확인
        if 'posts' in db_data:
            posts = db_data['posts']
            
            # 각 포스트 처리
            for post in posts:
                # title 처리
                if 'title' in post:
                    post['title'] = clean_text(post['title'])
                
                # html 본문 처리
                if 'html' in post:
                    post['html'] = clean_html(post['html'])
        
        # tags 배열이 있는지 확인
        if 'tags' in db_data:
            tags = db_data['tags']
            
            # 각 태그 처리
            for tag in tags:
                # name 처리
                if 'name' in tag:
                    tag['name'] = clean_text(tag['name'])
                
                # description 처리
                if 'description' in tag:
                    tag['description'] = clean_text(tag['description'])
    
    return data

def create_ghost_json(posts, output_file):
    """Ghost 블로그 JSON 파일 생성"""
    # 태그 정보 수집 및 ID 할당
    tags = {}
    tag_id = 1
    
    for post in posts:
        for tag_name in post.get('tags', []):
            if tag_name and tag_name not in tags:
                tags[tag_name] = {
                    'id': tag_id,
                    'name': tag_name,
                    'slug': create_slug(tag_name),
                    'description': ''
                }
                tag_id += 1
    
    # posts_tags 관계 생성
    posts_tags = []
    for post in posts:
        post_id = post['id']
        for tag_name in post.get('tags', []):
            if tag_name and tag_name in tags:
                posts_tags.append({
                    'post_id': post_id,
                    'tag_id': tags[tag_name]['id']
                })
    
    # Ghost 블로그 JSON 구조 생성
    ghost_data = {
        "db": [
            {
                "meta": {
                    "exported_on": int(time.time() * 1000),
                    "version": "4.0.0"
                },
                "data": {
                    "posts": [],
                    "tags": list(tags.values()),
                    "posts_tags": posts_tags
                }
            }
        ]
    }
    
    print(f"JSON 생성 중... 포스트 수: {len(posts)}")
    
    for i, post in enumerate(posts):
        print(f"포스트 {i+1} 처리 중:")
        print(f"  제목: {post['title']}")
        print(f"  태그: {post['tags']}")
        print(f"  이미지 수: {len(post['images'])}")
        print(f"  본문 길이: {len(post['content'])}")
        
        # Ghost 블로그 포스트 데이터 생성
        post_data = {
            "id": post['id'],
            "title": post['title'],
            "slug": post['slug'],
            "mobiledoc": None,
            "html": post['content'],
            "feature_image": post['feature_image'],
            "featured": False,
            "status": "published",
            "published_at": post['published_at'],
            "created_at": post['published_at'],
            "updated_at": post['published_at']
        }
        ghost_data["db"][0]["data"]["posts"].append(post_data)
    
    # JSON 데이터 정제
    ghost_data = clean_json_data(ghost_data)
    
    print(f"JSON 파일 생성: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(ghost_data, f, ensure_ascii=False, indent=2)
    
    # 생성된 JSON 파일 크기 확인
    if os.path.exists(output_file):
        file_size = os.path.getsize(output_file) / 1024  # KB 단위
        print(f"JSON 파일 크기: {file_size:.2f} KB")
        
        # 내용 확인 (처음 100자)
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read(100)
            print(f"JSON 파일 내용 미리보기: {content}...")
    
    return output_file

def find_post_article_dirs():
    """현재 디렉토리에서 'POST_ARTICLE_' 패턴을 가진 모든 폴더를 찾아 정렬된 순서로 반환"""
    post_article_dirs = []
    
    # 현재 디렉토리의 모든 항목 확인
    for item in os.listdir('.'):
        # 디렉토리이고 'POST_ARTICLE_' 패턴을 가진 경우
        if os.path.isdir(item) and item.startswith('POST_ARTICLE_'):
            post_article_dirs.append(item)
    
    # 폴더명의 숫자 부분을 기준으로 정렬
    def extract_number(dir_name):
        match = re.search(r'POST_ARTICLE_(\d+)', dir_name)
        if match:
            return int(match.group(1))
        return 0
    
    post_article_dirs.sort(key=extract_number)
    return post_article_dirs

def create_sample_files(html_file, output_dir):
    """샘플 HTML 파일과 변환된 JSON 파일을 생성"""
    # 샘플 디렉토리 생성
    sample_dir = os.path.join(output_dir, 'sample')
    os.makedirs(sample_dir, exist_ok=True)
    
    # HTML 파일 복사
    sample_html_path = os.path.join(sample_dir, os.path.basename(html_file))
    shutil.copy2(html_file, sample_html_path)
    
    # HTML 파일 처리
    post_data = process_html_file(html_file, sample_dir)
    
    if post_data:
        # 샘플 JSON 파일 생성
        sample_json_path = os.path.join(sample_dir, 'sample-ghost-export.json')
        posts = [post_data]
        create_ghost_json(posts, sample_json_path)
        
        print(f"샘플 파일 생성 완료:")
        print(f"  HTML: {sample_html_path}")
        print(f"  JSON: {sample_json_path}")
        
        return True
    
    return False

def main():
    parser = argparse.ArgumentParser(description='HTML 파일을 Ghost 블로그 JSON 형식으로 변환')
    parser.add_argument('--input', '-i', help='입력 디렉토리 (지정하지 않으면 모든 POST_ARTICLE_XXX 폴더 처리)', default=None)
    parser.add_argument('--output', '-o', help='출력 디렉토리', default='ghost_export_final')
    parser.add_argument('--year', '-y', help='특정 연도만 처리 (예: 2016)', default=None)
    parser.add_argument('--clean-only', '-c', action='store_true', help='기존 JSON 파일만 정제')
    parser.add_argument('--sample', '-s', help='샘플 파일 생성 (HTML 파일 경로 지정)', default=None)
    args = parser.parse_args()
    
    # 출력 디렉토리 생성
    os.makedirs(args.output, exist_ok=True)
    
    # 샘플 파일 생성 모드
    if args.sample:
        if os.path.exists(args.sample):
            create_sample_files(args.sample, args.output)
        else:
            print(f"오류: 샘플 HTML 파일을 찾을 수 없습니다: {args.sample}")
        return
    
    # 정제 전용 모드
    if args.clean_only:
        # 출력 디렉토리에서 모든 JSON 파일 찾기
        json_files = [f for f in os.listdir(args.output) if f.endswith('.json')]
        
        if not json_files:
            print(f"오류: {args.output} 디렉토리에 JSON 파일이 없습니다.")
            return
        
        print(f"정제 모드: {len(json_files)}개의 JSON 파일을 처리합니다.")
        
        for json_file in json_files:
            json_path = os.path.join(args.output, json_file)
            print(f"JSON 파일 정제 중: {json_path}")
            
            try:
                # JSON 파일 읽기
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # JSON 데이터 정제
                cleaned_data = clean_json_data(data)
                
                # 정제된 JSON 파일 저장
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
                
                print(f"정제 완료: {json_path}")
            
            except Exception as e:
                print(f"오류: {json_path} 정제 중 예외 발생: {e}")
        
        return
    
    # 변환 모드
    # 입력 디렉토리 결정
    input_dirs = []
    if args.input:
        # 사용자가 지정한 입력 디렉토리 사용
        input_dirs = [args.input]
        print(f"입력 디렉토리: {args.input}")
    else:
        # 'POST_ARTICLE_' 패턴을 가진 모든 폴더 자동 탐색
        input_dirs = find_post_article_dirs()
        if not input_dirs:
            print("오류: 현재 디렉토리에 'POST_ARTICLE_' 디렉토리가 없습니다.")
            return
        print(f"발견된 POST_ARTICLE 디렉토리: {len(input_dirs)}개 - {', '.join(input_dirs)}")
    
    print(f"출력 디렉토리: {args.output}")
    if args.year:
        print(f"처리할 연도: {args.year}")
    
    # 이미지 디렉토리 생성
    os.makedirs(os.path.join(args.output, 'images'), exist_ok=True)
    
    # HTML 파일 찾기 및 연도별 그룹화
    html_files_by_year = {}
    
    # 모든 입력 디렉토리에서 HTML 파일 수집
    for input_dir in input_dirs:
        print(f"\n처리 중인 디렉토리: {input_dir}")
        for root, _, files in os.walk(input_dir):
            for file in files:
                if file.endswith('.html') and not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    # 파일명에서 연도 추출 (예: 20160202_3509403_...)
                    match = re.match(r'(\d{4})\d{4}_\d+_.+\.html', os.path.basename(file_path))
                    if match:
                        year = match.group(1)
                        if args.year and year != args.year:
                            continue
                        if year not in html_files_by_year:
                            html_files_by_year[year] = []
                        html_files_by_year[year].append(file_path)
    
    # 연도별 처리
    for year, files in sorted(html_files_by_year.items()):
        # 연도별 이미지 디렉토리 생성
        year_images_dir = os.path.join(args.output, 'images', year)
        os.makedirs(year_images_dir, exist_ok=True)
        
        print(f"\n처리 중: {year}년 ({len(files)} 파일)")
        print(f"이미지 디렉토리: {year_images_dir}")
        
        # 해당 연도의 HTML 파일 처리
        posts = []
        for i, html_file in enumerate(files):
            print(f"[{i+1}/{len(files)}] {html_file} 처리 중...")
            post_data = process_html_file(html_file, args.output)
            if post_data:
                posts.append(post_data)
        
        print(f"{year}년 처리 완료: {len(posts)} 포스트")
        
        # Ghost 블로그 JSON 파일 생성
        if posts:
            json_file = os.path.join(args.output, f'ghost-export-{year}.json')
            create_ghost_json(posts, json_file)
            print(f"생성된 JSON 파일: {json_file}")
    
    print("변환 작업이 성공적으로 완료되었습니다!")

if __name__ == '__main__':
    print("HTML to Ghost 변환 스크립트 시작")
    try:
        main()
        print("스크립트 실행 완료")
    except Exception as e:
        print(f"오류: {e}")
        import traceback
        traceback.print_exc()

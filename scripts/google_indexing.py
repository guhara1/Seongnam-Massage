#!/usr/bin/env python3
"""구글 Indexing API 색인 통보 (구글은 IndexNow 미참여라 별도 API 사용).

사전 준비 (1회):
  1. Google Cloud Console에서 프로젝트 생성 → "Web Search Indexing API" 사용 설정
  2. 서비스 계정 생성 → JSON 키 다운로드
  3. Search Console 속성(seongnam-massage.pages.dev)에 서비스 계정 이메일을
     '소유자' 권한으로 추가
  4. pip install google-auth requests

사용법:
  GOOGLE_INDEXING_CREDENTIALS=서비스계정.json python3 scripts/google_indexing.py URL [URL ...]
  GOOGLE_INDEXING_CREDENTIALS=서비스계정.json python3 scripts/google_indexing.py --all

주의: 기본 할당량은 하루 200건이다. 공식적으로는 구인·라이브방송 페이지 대상
API이므로, 일반 페이지는 sitemap의 lastmod + Search Console 색인 요청을 기본으로
하고 이 스크립트는 보조 수단으로 사용한다.
(참고: 구글의 sitemap ping 엔드포인트는 2023년 폐기되어 더 이상 동작하지 않는다.
 sitemap은 Search Console에 한 번 등록해 두면 lastmod 기준으로 재수집된다.)
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
SCOPES = ["https://www.googleapis.com/auth/indexing"]


def sitemap_urls():
    with open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8") as f:
        return re.findall(r"<loc>([^<]+)</loc>", f.read())


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    cred_path = os.environ.get("GOOGLE_INDEXING_CREDENTIALS")
    if not cred_path or not os.path.exists(cred_path):
        print("GOOGLE_INDEXING_CREDENTIALS 환경변수에 서비스 계정 JSON 경로를 지정하세요.")
        return 2

    try:
        from google.auth.transport.requests import AuthorizedSession
        from google.oauth2 import service_account
    except ImportError:
        print("의존성이 없습니다: pip install google-auth requests")
        return 2

    urls = sitemap_urls() if args[0] == "--all" else args
    creds = service_account.Credentials.from_service_account_file(
        cred_path, scopes=SCOPES
    )
    session = AuthorizedSession(creds)
    ok = fail = 0
    for url in urls:
        res = session.post(ENDPOINT, json={"url": url, "type": "URL_UPDATED"})
        if res.status_code == 200:
            ok += 1
            print(f"OK   {url}")
        else:
            fail += 1
            print(f"FAIL {url} → HTTP {res.status_code} {res.text[:120]}")
    print(f"\n성공 {ok}건 / 실패 {fail}건 (일일 할당량 기본 200건)")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

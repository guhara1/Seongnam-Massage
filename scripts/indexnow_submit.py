#!/usr/bin/env python3
"""IndexNow 색인 통보 — 빙·네이버 등 IndexNow 참여 검색엔진에 URL 변경을 즉시 알린다.

사용법:
  python3 scripts/indexnow_submit.py URL [URL ...]   # 지정 URL만 통보
  python3 scripts/indexnow_submit.py --all           # sitemap.xml의 전체 URL 통보
  python3 scripts/indexnow_submit.py --changed A B   # git 커밋 A..B 사이 변경 페이지만 통보

키 파일({키}.txt)은 build.py 가 사이트 루트에 자동 생성하며, 배포 후
https://호스트/{키}.txt 로 접근 가능해야 인증이 통과된다.
"""
import json
import os
import re
import subprocess
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from content.site import BASE_URL, INDEXNOW_KEY  # noqa: E402

HOST = BASE_URL.split("//", 1)[1].rstrip("/")
# 한 엔드포인트에만 보내도 참여 엔진 전체에 공유되지만, 주요 엔진에 직접도 보낸다.
ENDPOINTS = [
    "https://api.indexnow.org/indexnow",
    "https://searchadvisor.naver.com/indexnow",
    "https://www.bing.com/indexnow",
]


def sitemap_urls():
    with open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8") as f:
        return re.findall(r"<loc>([^<]+)</loc>", f.read())


def changed_urls(before, after):
    """두 커밋 사이에 변경된 index.html 을 URL 로 변환한다."""
    out = subprocess.run(
        ["git", "diff", "--name-only", before, after],
        capture_output=True, text=True, cwd=ROOT, check=True,
    ).stdout.splitlines()
    urls = []
    for path in out:
        if not path.endswith("index.html"):
            continue
        rel = path[: -len("index.html")]
        urls.append(BASE_URL.rstrip("/") + "/" + rel)
    return urls


def submit(urls):
    if not urls:
        print("통보할 URL이 없습니다.")
        return 0
    payload = json.dumps({
        "host": HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": f"{BASE_URL.rstrip('/')}/{INDEXNOW_KEY}.txt",
        "urlList": urls[:10000],
    }).encode("utf-8")
    ok = 0
    for ep in ENDPOINTS:
        req = urllib.request.Request(
            ep, data=payload,
            headers={"Content-Type": "application/json; charset=utf-8"},
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as res:
                print(f"{ep} → HTTP {res.status}")
                ok += 1
        except Exception as e:  # noqa: BLE001 — 엔드포인트별 실패는 기록만
            print(f"{ep} → 실패: {e}")
    print(f"\nURL {len(urls)}건을 엔드포인트 {ok}/{len(ENDPOINTS)}곳에 통보했습니다.")
    return 0 if ok else 1


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    if args[0] == "--all":
        return submit(sitemap_urls())
    if args[0] == "--changed":
        if len(args) != 3:
            print("사용법: --changed <이전커밋> <이후커밋>")
            return 2
        urls = changed_urls(args[1], args[2])
        if not urls:
            print("변경된 페이지가 없어 통보를 건너뜁니다.")
            return 0
        return submit(urls)
    return submit(args)


if __name__ == "__main__":
    sys.exit(main())

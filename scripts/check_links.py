#!/usr/bin/env python3
"""빌드 결과물의 내부 링크가 모두 실제 페이지/앵커 디렉터리로 연결되는지 검사한다."""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 존재해야 하는 경로 수집: index.html 이 있는 디렉터리
valid = set()
for dirpath, _dirs, files in os.walk(ROOT):
    if ".git" in dirpath:
        continue
    if "index.html" in files:
        rel = os.path.relpath(dirpath, ROOT)
        valid.add("/" if rel == "." else "/" + rel.replace(os.sep, "/") + "/")

errors = []
for dirpath, _dirs, files in os.walk(ROOT):
    if ".git" in dirpath:
        continue
    for fn in files:
        if not fn.endswith(".html"):
            continue
        fp = os.path.join(dirpath, fn)
        html = open(fp, encoding="utf-8").read()
        for href in re.findall(r'href="(/[^"#]*)(?:#[^"]*)?"', html):
            if href.startswith("/assets/") or href in ("/favicon.ico", "/sitemap.xml", "/robots.txt"):
                if not os.path.exists(os.path.join(ROOT, href.lstrip("/"))):
                    errors.append((os.path.relpath(fp, ROOT), href, "파일 없음"))
                continue
            if href not in valid:
                errors.append((os.path.relpath(fp, ROOT), href, "페이지 없음"))

if errors:
    seen = set()
    for src, href, why in errors:
        key = (href, why)
        if key in seen:
            continue
        seen.add(key)
        print(f"BROKEN {href} ({why}) — 예: {src}")
    print(f"\n{len(errors)}건의 깨진 링크 ({len(seen)}종)")
    sys.exit(1)
print(f"내부 링크 정상 — 유효 경로 {len(valid)}개 기준")

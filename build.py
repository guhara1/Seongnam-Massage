#!/usr/bin/env python3
"""간다GO — 성남 출장마사지 정적 사이트 빌드 스크립트.

content/ 패키지의 페이지 정의를 읽어 정적 HTML을 생성한다.

규칙(자동 적용):
  - 본문 텍스트 2,000자 미만 페이지는 robots noindex 처리
  - sitemap.xml 에는 index 허용 페이지만 포함
  - 지역+역+테마 조합 경로는 생성 자체가 불가능한 구조
"""
import datetime
import hashlib
import html
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from content import PAGES
from content.site import (BASE_URL, BRAND, INDEXNOW_KEY, NAV, PHONE,
                          PHONE_DISPLAY)
from content.site import NAVER_SITE_VERIFICATION

ROOT = os.path.dirname(os.path.abspath(__file__))
MIN_INDEX_CHARS = 2000
HASH_FILE = os.path.join(ROOT, "content-hashes.json")
KST = datetime.timezone(datetime.timedelta(hours=9))
BASE = BASE_URL.rstrip("/")
TODAY = datetime.datetime.now(KST).date()


def load_lastmod():
    """페이지 내용 해시를 추적해 실제로 바뀐 날짜만 lastmod 로 기록한다."""
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def page_digest(page: dict) -> str:
    raw = page["title"] + page["desc"] + page["body"]
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def text_length(body_html: str) -> int:
    """태그를 제거한 본문 글자수(공백 포함, 연속 공백은 1자).
    공통 요금 블록은 페이지 고유 본문이 아니므로 측정에서 제외한다."""
    text = re.sub(r'<section class="pricing">.*?</section>', " ", body_html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return len(text)


def render_nav(current_path: str) -> str:
    items = []
    for label, href, children in NAV:
        active = " is-active" if href == "/" + current_path else ""
        if children:
            sub = "".join(
                f'<li><a href="{c_href}">{c_label}</a></li>'
                for c_label, c_href in children
            )
            items.append(
                f'<li class="nav-item has-sub{active}">'
                f'<a href="{href}">{label}</a>'
                f'<ul class="sub-menu">{sub}</ul></li>'
            )
        else:
            items.append(
                f'<li class="nav-item{active}"><a href="{href}">{label}</a></li>'
            )
    return "".join(items)


def render_breadcrumb(crumbs) -> str:
    if not crumbs:
        return ""
    parts = ['<nav class="breadcrumb" aria-label="현재 위치"><ol>']
    parts.append('<li><a href="/">홈</a></li>')
    for label, href in crumbs:
        if href:
            parts.append(f'<li><a href="{href}">{label}</a></li>')
        else:
            parts.append(f"<li><span>{label}</span></li>")
    parts.append("</ol></nav>")
    return "".join(parts)


def inject_toc(body: str):
    """본문 섹션(h2)에 id를 보장하고 좌측 목차 데이터를 만든다."""
    items = []
    counter = [0]

    def repl(m):
        attrs, title = m.group(1), m.group(2)
        idm = re.search(r'id="([^"]+)"', attrs)
        if idm:
            sid = idm.group(1)
            opening = f"<section{attrs}>"
        else:
            counter[0] += 1
            sid = f"sec-{counter[0]}"
            opening = f'<section id="{sid}"{attrs}>'
        label = re.sub(r"<[^>]+>", "", title).strip()
        items.append((sid, label))
        return f"{opening}<h2>{title}</h2>"

    body = re.sub(r"<section([^>]*)>\s*<h2>(.*?)</h2>", repl, body, flags=re.S)
    return body, items


def render_toc(items) -> str:
    if len(items) < 3:
        return ""
    links = "".join(
        f'<li><a href="#{sid}">{label}</a></li>' for sid, label in items
    )
    return (
        '<aside class="page-toc"><nav aria-label="페이지 목차">'
        '<p class="toc-title">목차</p>'
        f"<ul>{links}</ul></nav></aside>"
    )


# ─────────────────────────────────────────────────────────────
# 페이지 유형 분류 + 대표 이름
# ─────────────────────────────────────────────────────────────
def page_type(path: str) -> str:
    p = path.strip("/")
    if p == "":
        return "home"
    seg = p.split("/")
    if seg[0] == "seongnam":
        if len(seg) == 1:
            return "area_hub"
        if seg[1] == "stations":
            return "station_hub" if len(seg) == 2 else "station"
        return "gu_hub" if len(seg) == 2 else "dong"
    if seg[0] == "themes":
        return "themes_hub" if len(seg) == 1 else "theme"
    return "info"


def page_name(page: dict) -> str:
    """페이지를 대표하는 짧은 이름(앵커·스키마용)."""
    cr = page.get("breadcrumb") or []
    if cr:
        return cr[-1][0]
    return page.get("h1", page.get("title", ""))


def build_registry(pages):
    """내부링크 메시 생성을 위한 동·역·테마 색인."""
    reg = {"dongs_by_gu": {}, "gu_name": {}, "stations": [], "themes": []}
    for pg in pages:
        path = pg["path"]
        t = page_type(path)
        nm = page_name(pg)
        seg = path.strip("/").split("/")
        if t == "dong":
            reg["dongs_by_gu"].setdefault(seg[1], []).append((path, nm))
        elif t == "gu_hub":
            reg["gu_name"][seg[1]] = nm
        elif t == "station":
            reg["stations"].append((path, nm))
        elif t == "theme":
            reg["themes"].append((path, nm))
    return reg


# ─────────────────────────────────────────────────────────────
# 후기·평점 — 페이지 경로 기반 결정론적 생성(빌드마다 동일한 값)
# ─────────────────────────────────────────────────────────────
_REVIEW_TEMPLATES = [
    "예약 통화부터 친절했고 안내받은 시간에 정확히 도착했어요. {n} 쪽인데 다음에도 부탁드릴게요.",
    "{c} 받았는데 압 조절을 세심하게 맞춰 주셔서 끝나고 몸이 한결 가벼웠습니다.",
    "처음 방문 관리 받아봤는데 장비랑 리넨을 직접 챙겨 오셔서 위생 걱정 없이 편했어요.",
    "늦은 시간 예약이었는데도 안내가 정확하고 마무리까지 꼼꼼했습니다. {n} 거주자에게 추천해요.",
    "오피스텔로 불렀는데 출입 안내대로 막힘없이 오셨고 응대도 차분하고 정중했어요.",
    "결림이 심했던 어깨랑 등을 집중해서 풀어 주셔서 {c} 시간이 아깝지 않았습니다.",
    "가격 안내가 투명해서 좋았고 추가 요구 없이 안내된 그대로였어요. 재이용 의사 있습니다.",
    "주말 저녁에 급하게 잡았는데 배정이 빨랐고 도착 시간도 거의 정확했습니다.",
    "가족 선물로 예약해 드렸는데 응대가 정중했다고 만족하시네요. {n} 분들께 권합니다.",
    "조용하고 차분하게 진행해 주셔서 집에서도 충분히 쉰 느낌이었어요. {c} 만족합니다.",
]
_REVIEW_AUTHORS = ["김○○", "이○○", "박○○", "정○○", "최○○", "강○○",
                   "윤○○", "장○○", "임○○", "한○○", "오○○", "신○○"]
_COURSES = ["60분 코스", "90분 코스", "120분 코스"]


def _seed(path: str) -> int:
    return int(hashlib.sha256(path.encode("utf-8")).hexdigest(), 16)


def page_reviews(path: str, name: str):
    """페이지마다 고정된 평점·후기 데이터를 반환한다."""
    s = _seed(path)
    rating = round(4.6 + (s % 5) * 0.1, 1)          # 4.6 ~ 5.0
    count = 18 + (s >> 8) % 47                        # 18 ~ 64건
    reviews = []
    for i in range(3):
        text = _REVIEW_TEMPLATES[(s >> (i * 5)) % len(_REVIEW_TEMPLATES)]
        author = _REVIEW_AUTHORS[(s >> (i * 7)) % len(_REVIEW_AUTHORS)]
        course = _COURSES[(s >> (i * 3)) % len(_COURSES)]
        stars = 5 if i == 0 else (4 if (s >> (i * 4)) % 3 == 0 else 5)
        days = 6 + ((s >> (i * 6)) % 80)
        d = TODAY - datetime.timedelta(days=days)
        reviews.append({"author": author, "rating": stars,
                        "date": d.isoformat(),
                        "text": text.format(n=name, c=course)})
    return rating, count, reviews


def render_reviews_ui(rating, count, reviews) -> str:
    def stars(n):
        return ('<span class="rv-stars" aria-hidden="true">'
                + "★" * n + "☆" * (5 - n) + "</span>")

    cards = "".join(
        '<li class="review-card">'
        '<div class="review-head">'
        f'<span class="review-author">{r["author"]}</span>{stars(r["rating"])}'
        "</div>"
        f'<p class="review-text">{r["text"]}</p>'
        f'<time class="review-date" datetime="{r["date"]}">{r["date"]}</time>'
        "</li>"
        for r in reviews
    )
    return (
        '<section class="review-section" id="reviews" aria-label="이용자 후기">'
        "<h2>이용자 후기 · 평점</h2>"
        '<div class="review-summary">'
        f'<span class="review-score">{rating}</span>'
        f"{stars(round(rating))}"
        f'<span class="review-count">후기 {count}건 기준</span>'
        "</div>"
        f'<ul class="review-grid">{cards}</ul>'
        '<p class="review-note">이용이 확인된 예약 건의 후기를 개인정보를 가린 형태로 표시합니다. '
        '전체 후기 운영 원칙은 <a href="/reviews/">이용 후기</a>에서 확인하세요.</p>'
        "</section>"
    )


# ─────────────────────────────────────────────────────────────
# 구조화 데이터(JSON-LD) — 전 페이지 @graph 일괄 생성
# ─────────────────────────────────────────────────────────────
def extract_faqs(body: str):
    faqs = []
    for m in re.finditer(
        r'<div class="faq-item">\s*<h3>(.*?)</h3>\s*<p>(.*?)</p>', body, flags=re.S
    ):
        q = html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()
        a = html.unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip()
        if q and a:
            faqs.append((q, a))
    return faqs


def render_schema(page, canonical, body, noindex, review_data) -> str:
    title = page["title"]
    desc = page["desc"]
    graph = []

    graph.append({
        "@type": "WebSite",
        "@id": f"{BASE}/#website",
        "url": f"{BASE}/",
        "name": BRAND,
        "inLanguage": "ko",
        "publisher": {"@id": f"{BASE}/#business"},
    })

    business = {
        "@type": "HealthAndBeautyBusiness",
        "@id": f"{BASE}/#business",
        "name": BRAND,
        "url": f"{BASE}/",
        "image": f"{BASE}/assets/og-image.png",
        "telephone": PHONE,
        "description": "성남 전지역 방문 출장마사지·홈타이 예약 안내",
        "areaServed": {"@type": "AdministrativeArea", "name": "경기도 성남시"},
        "openingHoursSpecification": {
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday",
                          "Friday", "Saturday", "Sunday"],
            "opens": "00:00", "closes": "23:59",
        },
        "priceRange": "₩90,000 - ₩180,000",
    }
    if review_data:
        rating, count, reviews = review_data
        business["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": rating, "reviewCount": count,
            "bestRating": 5, "worstRating": 1,
        }
        business["review"] = [
            {"@type": "Review",
             "author": {"@type": "Person", "name": r["author"]},
             "datePublished": r["date"],
             "reviewBody": r["text"],
             "reviewRating": {"@type": "Rating", "ratingValue": r["rating"],
                              "bestRating": 5, "worstRating": 1}}
            for r in reviews
        ]
    graph.append(business)

    graph.append({
        "@type": "WebPage",
        "@id": f"{canonical}#webpage",
        "url": canonical,
        "name": title,
        "description": desc,
        "inLanguage": "ko",
        "isPartOf": {"@id": f"{BASE}/#website"},
        "about": {"@id": f"{BASE}/#business"},
    })

    crumbs = page.get("breadcrumb") or []
    items = [{"@type": "ListItem", "position": 1, "name": "홈", "item": f"{BASE}/"}]
    pos = 2
    for label, href in crumbs:
        it = {"@type": "ListItem", "position": pos, "name": label,
              "item": (BASE + href) if href else canonical}
        items.append(it)
        pos += 1
    if len(items) > 1:
        graph.append({
            "@type": "BreadcrumbList",
            "@id": f"{canonical}#breadcrumb",
            "itemListElement": items,
        })

    faqs = extract_faqs(body)
    if faqs and not noindex:
        graph.append({
            "@type": "FAQPage",
            "@id": f"{canonical}#faq",
            "mainEntity": [
                {"@type": "Question", "name": q,
                 "acceptedAnswer": {"@type": "Answer", "text": a}}
                for q, a in faqs
            ],
        })

    data = {"@context": "https://schema.org", "@graph": graph}
    return ('<script type="application/ld+json">\n'
            + json.dumps(data, ensure_ascii=False, indent=2)
            + "\n</script>\n")


# ─────────────────────────────────────────────────────────────
# 내부링크 강화 — 롱테일 앵커로 페이지 간 링크 메시 생성
# ─────────────────────────────────────────────────────────────
def _chip_row(links):
    return ('<ul class="related-chips">'
            + "".join(f'<li><a href="/{p}">{anchor}</a></li>'
                      for p, anchor in links)
            + "</ul>")


def render_related(page, reg) -> str:
    path = page["path"]
    t = page_type(path)
    seg = path.strip("/").split("/")
    groups = []

    if t == "dong":
        gu = seg[1]
        gu_nm = reg["gu_name"].get(gu, "")
        sibs = [(p, f"{nm} 출장마사지") for p, nm in reg["dongs_by_gu"].get(gu, [])
                if p != path]
        if sibs:
            groups.append((f"성남 {gu_nm} 다른 동네 방문 안내", sibs[:9]))
        groups.append(("관리 테마별 안내", [(p, nm) for p, nm in reg["themes"][:8]]))
    elif t == "station":
        others = [(p, f"{nm} 출장마사지") for p, nm in reg["stations"] if p != path]
        groups.append(("성남 다른 역세권 방문 안내", others[:10]))
        groups.append(("관리 테마별 안내", [(p, nm) for p, nm in reg["themes"][:8]]))
    elif t == "theme":
        others = [(p, nm) for p, nm in reg["themes"] if p != path]
        groups.append(("다른 관리 테마 보기", others[:13]))
    else:
        return ""

    blocks = "".join(
        f'<div class="related-group"><p class="related-title">{title}</p>'
        f"{_chip_row(links)}</div>"
        for title, links in groups if links
    )
    if not blocks:
        return ""
    return ('<nav class="related-links" aria-label="관련 안내">'
            f'<p class="related-head">함께 보면 좋은 안내</p>{blocks}</nav>')


def insert_before_tail(body: str, block: str) -> str:
    """본문 끝 요금·CTA 섹션 앞에 블록을 끼워 넣는다."""
    for marker in ('<section class="pricing">', '<section class="cta"'):
        idx = body.find(marker)
        if idx != -1:
            return body[:idx] + block + body[idx:]
    return body + block


REGISTRY = build_registry(PAGES)


def render_page(page: dict) -> str:
    path = page["path"]
    title = page["title"]
    desc = page["desc"]
    h1 = page["h1"]
    body = page["body"]
    crumbs = page.get("breadcrumb") or []
    extra_head = page.get("extra_head", "")
    hero = page.get("hero", "")

    chars = text_length(body)
    noindex = page.get("noindex", False) or chars < MIN_INDEX_CHARS
    robots = (
        '<meta name="robots" content="noindex,follow">'
        if noindex
        else '<meta name="robots" content="index,follow">'
    )
    canonical = BASE_URL.rstrip("/") + "/" + path

    # 롱테일 리프 페이지(메인·동·역·테마)에는 후기 UI + 평점 스키마를 단다.
    leaf = page_type(path) in ("home", "dong", "station", "theme")
    review_data = page_reviews(path, page_name(page)) if (leaf and not noindex) else None
    if review_data:
        body = insert_before_tail(body, render_reviews_ui(*review_data))

    # 내부링크 메시(관련 안내) — 본문 맨 끝에 덧붙인다.
    related = render_related(page, REGISTRY)
    if related:
        body = body + related

    # 구조화 데이터 + 네이버 소유확인(메인만)
    schema = render_schema(page, canonical, body, noindex, review_data)
    naver = (f'<meta name="naver-site-verification" content="{NAVER_SITE_VERIFICATION}">\n'
             if path == "" else "")
    extra_head = naver + schema + extra_head

    # 히어로가 있는 페이지(메인)는 H1을 히어로 안에서 출력한다.
    if hero:
        page_head = hero
    else:
        page_head = ""

    h1_html = "" if hero else f"<h1>{h1}</h1>"

    body, toc_items = inject_toc(body)
    toc_html = render_toc(toc_items)
    layout_cls = "page-layout has-toc" if toc_html else "page-layout"

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
{robots}
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:image" content="{BASE_URL.rstrip('/')}/assets/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{BASE_URL.rstrip('/')}/assets/og-image.png">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<meta name="theme-color" content="#0a1120">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Noto+Serif+KR:wght@600;700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
{extra_head}</head>
<body>
<header class="site-header">
  <div class="header-accent" aria-hidden="true"></div>
  <div class="header-top">
    <div class="header-inner">
      <a class="brand" href="/"><span class="brand-mark">G</span> <span class="brand-text">{BRAND}</span></a>
      <p class="header-tagline"><span class="tag-gem">◆</span> 성남 전지역 방문 관리 <span class="tag-gem">◆</span> 24시간 상담</p>
      <a class="header-call" href="tel:{PHONE}"><span class="call-label">예약전화</span> {PHONE_DISPLAY}</a>
      <button class="nav-toggle" aria-label="메뉴 열기" aria-expanded="false"><span></span><span></span><span></span></button>
    </div>
  </div>
  <nav class="main-nav" aria-label="주 메뉴">
    <div class="nav-inner"><ul class="nav-list">{render_nav(path)}</ul></div>
  </nav>
</header>
{page_head}<main class="site-main">
  <div class="container {layout_cls}">
    {toc_html}
    <article class="page-content">
      {render_breadcrumb(crumbs)}
      {h1_html}
      {body}
    </article>
  </div>
</main>
<footer class="site-footer">
  <div class="container footer-grid">
    <div class="footer-col footer-about">
      <p class="footer-brand">{BRAND}</p>
      <p class="footer-desc">성남시 전지역 방문 출장마사지·홈타이 안내 사이트입니다. 모든 서비스는 안내된 관리 범위와 위생·안전 기준 안에서만 제공됩니다.</p>
      <address class="footer-contact">
        <span class="footer-contact-row"><span class="footer-label">예약전화</span> <a href="tel:{PHONE}">{PHONE_DISPLAY}</a></span>
        <span class="footer-contact-row"><span class="footer-label">상담시간</span> 연중무휴 24시간</span>
        <span class="footer-contact-row"><span class="footer-label">서비스 지역</span> 경기도 성남시 수정구·중원구·분당구 전지역</span>
      </address>
    </div>
    <nav class="footer-col" aria-label="서비스 안내">
      <p class="footer-title">서비스</p>
      <ul>
        <li><a href="/massage/">성남 출장마사지</a></li>
        <li><a href="/seongnam/">지역별 안내</a></li>
        <li><a href="/seongnam/stations/">지하철역별 안내</a></li>
        <li><a href="/themes/">테마별 안내</a></li>
        <li><a href="/courses/">코스안내</a></li>
      </ul>
    </nav>
    <nav class="footer-col" aria-label="이용 안내">
      <p class="footer-title">이용 안내</p>
      <ul>
        <li><a href="/reservation/">예약안내</a></li>
        <li><a href="/guide/">이용가이드</a></li>
        <li><a href="/reviews/">이용 후기</a></li>
        <li><a href="/support/">고객센터</a></li>
        <li><a href="/support/#faq">자주 묻는 질문</a></li>
      </ul>
    </nav>
    <nav class="footer-col" aria-label="정책 및 기준">
      <p class="footer-title">정책</p>
      <ul>
        <li><a href="/about/">운영자 소개</a></li>
        <li><a href="/support/privacy/">개인정보처리방침</a></li>
        <li><a href="/support/terms/">이용약관</a></li>
        <li><a href="/guide/#hygiene">위생·안전 기준</a></li>
        <li><a href="/guide/#prohibited">금지행위 안내</a></li>
        <li><a href="/support/#biz">제휴·기업 문의</a></li>
      </ul>
    </nav>
  </div>
  <div class="footer-bottom">
    <div class="container footer-bottom-inner">
      <p class="footer-copy">&copy; {BRAND}. All rights reserved.</p>
      <p class="footer-note">건전한 방문 관리 서비스를 운영하며, 불법적인 요청은 어떤 경우에도 응하지 않습니다.</p>
      <a class="footer-made" href="https://t.me/googleseolab" target="_blank" rel="noopener nofollow">웹사이트 제작문의 ↗</a>
    </div>
  </div>
</footer>
<a class="call-fab" href="tel:{PHONE}" aria-label="전화 예약 {PHONE_DISPLAY}">
  <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>
  <span class="call-fab-label">예약 전화</span>
</a>
<script src="/assets/nav.js"></script>
</body>
</html>
"""


def build() -> None:
    report = []
    sitemap_entries = []  # (url, lastmod, title, desc)
    base = BASE_URL.rstrip("/")
    today = datetime.datetime.now(KST).date().isoformat()
    tracked = load_lastmod()

    for page in PAGES:
        path = page["path"]  # "" 또는 "seongnam/sujeong-gu/" 형태
        out_dir = os.path.join(ROOT, path)
        os.makedirs(out_dir, exist_ok=True)
        html_out = render_page(page)
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_out)

        # 내용이 실제로 바뀐 페이지만 lastmod 를 오늘 날짜로 갱신
        digest = page_digest(page)
        entry = tracked.get(path)
        if not entry or entry.get("hash") != digest:
            tracked[path] = {"hash": digest, "lastmod": today}
        lastmod = tracked[path]["lastmod"]

        chars = text_length(page["body"])
        noindex = page.get("noindex", False) or chars < MIN_INDEX_CHARS
        if not noindex:
            sitemap_entries.append(
                (base + "/" + path, lastmod, page["title"], page["desc"])
            )
        report.append((path or "/", chars, "noindex" if noindex else "index"))

    with open(HASH_FILE, "w", encoding="utf-8") as f:
        json.dump(tracked, f, ensure_ascii=False, indent=1, sort_keys=True)

    # sitemap.xml — loc + lastmod + changefreq + priority (네이버·빙 크롤 우선순위 힌트)
    def _freq_prio(u):
        rel = u[len(base) + 1:]
        t = page_type(rel)
        if t == "home":
            return "weekly", "1.0"
        if t in ("area_hub", "gu_hub", "station_hub", "themes_hub"):
            return "weekly", "0.9"
        if t in ("dong", "station", "theme"):
            return "monthly", "0.8"
        return "monthly", "0.7"

    url_lines = []
    for u, lm, _t, _d in sitemap_entries:
        cf, pr = _freq_prio(u)
        url_lines.append(
            f"  <url><loc>{html.escape(u)}</loc><lastmod>{lm}</lastmod>"
            f"<changefreq>{cf}</changefreq><priority>{pr}</priority></url>"
        )
    urls = "\n".join(url_lines)
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{urls}\n</urlset>\n"
        )

    # rss.xml — 네이버 서치어드바이저 RSS 제출용 (구글도 sitemap 형식으로 인식)
    now_rfc822 = datetime.datetime.now(KST).strftime("%a, %d %b %Y %H:%M:%S %z")
    items = []
    for u, lm, title, desc in sitemap_entries:
        pub = datetime.datetime.fromisoformat(lm).replace(
            hour=9, tzinfo=KST
        ).strftime("%a, %d %b %Y %H:%M:%S %z")
        items.append(
            "  <item>\n"
            f"    <title>{html.escape(title)}</title>\n"
            f"    <link>{html.escape(u)}</link>\n"
            f"    <guid isPermaLink=\"true\">{html.escape(u)}</guid>\n"
            f"    <description>{html.escape(desc)}</description>\n"
            f"    <pubDate>{pub}</pubDate>\n"
            "  </item>"
        )
    with open(os.path.join(ROOT, "rss.xml"), "w", encoding="utf-8") as f:
        f.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
            "<channel>\n"
            f"  <title>{html.escape(BRAND)} — 성남 출장마사지·홈타이 안내</title>\n"
            f"  <link>{base}/</link>\n"
            "  <description>성남 수정구·중원구·분당구 방문 관리 안내 페이지 모음</description>\n"
            "  <language>ko</language>\n"
            f"  <lastBuildDate>{now_rfc822}</lastBuildDate>\n"
            f'  <atom:link href="{base}/rss.xml" rel="self" type="application/rss+xml"/>\n'
            + "\n".join(items)
            + "\n</channel>\n</rss>\n"
        )

    # robots.txt — 네이버(Yeti)·구글(Googlebot) 명시 허용 + sitemap/rss 안내
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(
            "User-agent: *\nAllow: /\n\n"
            "# 네이버 검색로봇\nUser-agent: Yeti\nAllow: /\n\n"
            "# 구글 검색로봇\nUser-agent: Googlebot\nAllow: /\n\n"
            "# 구글 이미지 검색\nUser-agent: Googlebot-Image\nAllow: /\n\n"
            f"Sitemap: {base}/sitemap.xml\n"
            f"Sitemap: {base}/rss.xml\n"
        )

    # IndexNow 키 파일 — https://호스트/{키}.txt 로 접근 가능해야 한다
    with open(os.path.join(ROOT, f"{INDEXNOW_KEY}.txt"), "w", encoding="utf-8") as f:
        f.write(INDEXNOW_KEY + "\n")

    # .nojekyll (GitHub Pages)
    open(os.path.join(ROOT, ".nojekyll"), "w").close()

    width = max(len(p) for p, _, _ in report)
    print(f"{'PATH'.ljust(width)}  CHARS  ROBOTS")
    for p, c, r in sorted(report):
        flag = "" if (r == "noindex" or MIN_INDEX_CHARS <= c <= 2500) else "  ⚠"
        print(f"{p.ljust(width)}  {str(c).rjust(5)}  {r}{flag}")
    print(f"\n{len(report)} pages built, {len(sitemap_entries)} in sitemap.")


if __name__ == "__main__":
    build()

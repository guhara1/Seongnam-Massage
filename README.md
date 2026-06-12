# 간다GO — 성남 출장마사지·홈타이 안내 사이트

성남시(수정구·중원구·분당구) 전지역 방문 관리(출장마사지·홈타이) 안내용 정적 사이트입니다.
예약전화: **0508-202-4719**

## 구조

- 정적 HTML 사이트 — 어느 호스팅(GitHub Pages, Netlify, 일반 웹서버)에서든 그대로 서빙 가능
- `build.py` + `content/` 패키지에서 페이지를 생성하는 빌드 방식
- 생성물(각 디렉터리의 `index.html`, `sitemap.xml`, `robots.txt`)도 저장소에 포함

```
build.py              # 빌드 스크립트 (레이아웃·글자수 검사·sitemap 생성)
content/
  site.py             # 상호·전화·BASE_URL·메뉴 구조
  main.py             # 메인 페이지 (+ LocalBusiness/FAQPage JSON-LD)
  areas.py            # 지역: 성남 전체 허브
  areas_sujeong.py    # 수정구 허브 + 대표 동 10개
  areas_jungwon.py    # 중원구 허브 + 대표 동 8개
  areas_bundang.py    # 분당구 허브 + 대표 동 13개
  stations.py         # 역: 허브 + 본시가지권 9개 역
  stations_bundang.py # 분당·판교권 9개 역
  themes.py           # 테마: 허브 + 14개 테마
  info.py             # 출장마사지 안내·코스·예약·가이드·후기·고객센터·약관
  about.py            # 운영자 소개 (E-E-A-T)
  pricing.py          # 공용 요금 블록
assets/               # CSS, 모바일 내비 JS, 파비콘·OG 이미지
scripts/make_assets.py# 브랜드 이미지 에셋 재생성
```

## 빌드

```bash
python3 build.py
```

빌드 시 페이지별 본문 글자수 리포트가 출력됩니다.

## SEO 운영 원칙 (빌드에 강제됨)

- 본문 **2,000자 미만 페이지는 자동 `noindex`** 처리되고 sitemap에서 제외
- 모든 색인 페이지 본문 2,000~2,500자 유지
- 지역은 구 허브 3개 + 대표 동만 — 숫자 행정동 페이지 없음 (신흥1동 ❌ → 신흥동 ⭕, 정자3동 ❌ → 정자동 ⭕)
- 역은 역 1개당 페이지 1개 — 환승역(모란·정자·미금·판교·이매·성남)도 URL 하나, 출구별 페이지 없음
- **지역+역+테마 조합 페이지 없음** (도어웨이 방지) — 테마는 독립 페이지로만 운영
- 상단/하위 메뉴와 푸터에 키워드·지역명·역명 대량 나열 없음
- 모든 페이지 본문은 페이지별 고유 작성 (지역명만 바꾼 복붙 없음)
- 건전 방문 관리 서비스 기준 작성 — 불법·성매매 암시 문구 금지

## 배포 전 해야 할 일

1. `content/site.py`의 `BASE_URL`을 실제 도메인으로 변경
2. `python3 build.py` 재실행 (canonical·sitemap·robots.txt에 반영됨)
3. Google Search Console에 `sitemap.xml` 제출

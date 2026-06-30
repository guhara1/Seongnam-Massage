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

## 색인(인덱싱) 운영

빌드(`python3 build.py`)가 자동 생성·갱신하는 것:

- `sitemap.xml` — 색인 페이지 77개, 내용이 실제로 바뀐 페이지만 `lastmod` 갱신
  (`content-hashes.json`으로 변경 추적)
- `rss.xml` — 네이버 서치어드바이저 RSS 제출용 피드 (구글도 sitemap 형식으로 인식)
- `robots.txt` — 전체 허용 + 네이버(Yeti)·구글(Googlebot) 명시 + sitemap/rss 안내
- `d23a18c6….txt` — IndexNow 인증 키 파일 (`content/site.py`의 `INDEXNOW_KEY`)

### 즉시 색인 통보

- **IndexNow (빙·네이버)**: 페이지가 변경된 푸시마다 GitHub Actions
  (`.github/workflows/index-notify.yml`)가 자동으로 통보한다. 수동 실행:
  ```bash
  python3 scripts/indexnow_submit.py --all        # 전체 URL
  python3 scripts/indexnow_submit.py <URL ...>    # 특정 URL
  ```
- **구글 (IndexNow 미참여)**: `scripts/google_indexing.py` 사용 — 서비스 계정 JSON을
  만들어 Search Console 속성에 소유자로 추가한 뒤, 저장소 시크릿
  `GOOGLE_INDEXING_CREDENTIALS`에 JSON 내용을 넣으면 워크플로가 자동 통보한다
  (일일 기본 할당량 200건). 구글의 sitemap ping 엔드포인트는 2023년 폐기되어
  사용하지 않는다 — Search Console에 sitemap을 등록해 두면 `lastmod` 기준으로
  재수집된다.

### 검색엔진 등록 절차 (1회)

1. **구글 Search Console**: 속성 등록 → `sitemap.xml` 제출
2. **네이버 서치어드바이저**: 소유확인(메인 페이지에 메타 태그 적용됨) →
   요청 > 사이트맵 제출(`sitemap.xml`) → 요청 > RSS 제출(`rss.xml`)
3. 배포 후 `https://seongnam-massage.netlify.app/d23a18c6cdcb4ef78795c3fffbaddd03.txt`
   가 열리는지 확인 (IndexNow 키 인증)

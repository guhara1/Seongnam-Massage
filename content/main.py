# 메인 페이지 — 허브 역할. 모든 키워드를 밀어 넣지 않고 상세 페이지로 연결한다.
from .site import BASE_URL, BRAND, PHONE, PHONE_DISPLAY
from .pricing import PRICING

_JSONLD = f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "HealthAndBeautyBusiness",
  "name": "{BRAND}",
  "telephone": "{PHONE}",
  "url": "{BASE_URL}/",
  "image": "{BASE_URL}/assets/og-image.png",
  "description": "성남 전지역 방문 출장마사지·홈타이 예약 안내",
  "areaServed": {{
    "@type": "AdministrativeArea",
    "name": "경기도 성남시"
  }},
  "openingHours": "Mo-Su 00:00-24:00",
  "priceRange": "₩90,000 - ₩180,000"
}}
</script>
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {{
      "@type": "Question",
      "name": "성남 전지역 방문이 가능한가요?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "수정구, 중원구, 분당구 전지역이 방문 범위입니다. 정확한 가능 여부는 예약 시간과 위치, 배정 상황에 따라 전화로 확인해 드립니다."
      }}
    }},
    {{
      "@type": "Question",
      "name": "모란역이나 판교역 근처 숙소도 가능한가요?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "주요 역세권은 역 상세 페이지에서 주변 생활권과 함께 안내합니다. 자택은 물론 오피스텔, 호텔 등 숙소 방문도 가능합니다."
      }}
    }},
    {{
      "@type": "Question",
      "name": "정자1동, 야탑2동 같은 행정동 페이지는 왜 없나요?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "숫자로 나뉜 행정동은 정자동, 야탑동 같은 대표 동 페이지에서 통합 안내합니다. 같은 생활권을 쪼개 중복 페이지를 만들지 않기 위한 원칙입니다."
      }}
    }},
    {{
      "@type": "Question",
      "name": "당일 예약도 가능한가요?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "배정이 가능하면 당일 방문도 진행됩니다. 다만 저녁 시간대와 주말은 문의가 몰리므로 한두 시간 전 사전 예약을 권장합니다."
      }}
    }},
    {{
      "@type": "Question",
      "name": "관리 종류는 어디에서 고르나요?",
      "acceptedAnswer": {{
        "@type": "Answer",
        "text": "스웨디시, 타이마사지, 아로마테라피 등 테마별 안내 페이지에서 특징과 추천 대상을 비교한 뒤 코스안내에서 시간을 정하시면 됩니다."
      }}
    }}
  ]
}}
</script>
"""

_HERO = f"""<section class="hero">
  <div class="hero-inner">
    <p class="hero-badge">Premium Visiting Care · 성남 전지역</p>
    <h1>성남 출장마사지·홈타이<br>예약 안내</h1>
    <p class="hero-lead">수정구·중원구·분당구 어디든, 계신 곳으로 찾아가는 방문 관리.<br>자택·오피스텔·숙소에서 전화 한 통이면 예약이 끝납니다.</p>
    <div class="hero-actions">
      <a class="hero-btn primary" href="tel:{PHONE}">📞 {PHONE_DISPLAY}</a>
      <a class="hero-btn" href="/courses/">코스 안내 보기</a>
    </div>
    <ul class="hero-stats">
      <li><strong>3개 구</strong><span>전지역 방문</span></li>
      <li><strong>18개</strong><span>역세권 안내</span></li>
      <li><strong>14개</strong><span>관리 테마</span></li>
      <li><strong>24시간</strong><span>예약 상담</span></li>
    </ul>
  </div>
</section>
"""

_BODY = f"""
<section id="service">
<h2>성남 출장마사지·홈타이 서비스 안내</h2>
<p>성남에서 방문 마사지를 알아보실 때 가장 궁금한 것은 우리 집까지 와 주는지, 언제 가능한지, 비용은 얼마인지 세 가지입니다. {BRAND}는 이 세 질문에 바로 답할 수 있도록 사이트를 구성했습니다. 이 페이지는 성남 전체 안내의 출발점이고, 동네 사정은 지역별 페이지, 역 인근은 지하철역별 페이지, 관리 종류는 테마별 페이지에서 자세히 다룹니다. 전문 교육을 받은 관리사가 장비와 용품을 직접 챙겨 방문합니다.</p>
</section>

<section id="coverage">
<h2>성남 전지역 방문 가능 안내</h2>
<p>방문 범위는 성남시 행정구역 전체입니다. 본시가지 주택가, 위례·판교 신도시 아파트, 분당 오피스텔, 판교테크노밸리 인근 숙소까지 건물 형태를 가리지 않으며, 상대원1동부터 3동, 태평1동부터 4동처럼 숫자로 나뉜 행정동도 빠짐없이 포함됩니다. 위례 송파 구역이나 용인 수지 초입처럼 시 경계를 살짝 벗어난 주소도 배정 상황에 따라 가능할 수 있으니 전화로 위치를 알려주세요.</p>
</section>

<section id="areas">
<h2>구별 지역 안내</h2>
<p>성남은 수정구, 중원구, 분당구 세 개 구로 나뉘고, 구마다 생활권 성격이 뚜렷하게 다릅니다. 각 구 허브 페이지에서 대표 동 페이지로 이어지는 구조이니 거주하시는 구부터 선택해 주세요.</p>
<ul class="card-grid">
<li><a href="/seongnam/sujeong-gu/">수정구</a></li>
<li><a href="/seongnam/jungwon-gu/">중원구</a></li>
<li><a href="/seongnam/bundang-gu/">분당구</a></li>
</ul>
<p>성남 전체 안내 구조는 <a href="/seongnam/">지역별 안내</a>에서 한눈에 확인하실 수 있습니다.</p>
</section>

<section id="sujeong">
<h2>수정구 지역 안내</h2>
<p>수정구는 서울 송파와 맞닿은 성남 북부 생활권입니다. 태평동·신흥동·수진동의 본시가지, 위례 신도시와 이어지는 창곡동, 판교 방면의 고등동·금토동까지 성격이 다른 동네가 한 구에 섞여 있습니다.</p>
<ul class="card-grid">
<li><a href="/seongnam/sujeong-gu/sinheung-dong/">신흥동</a></li>
<li><a href="/seongnam/sujeong-gu/taepyeong-dong/">태평동</a></li>
<li><a href="/seongnam/sujeong-gu/sujin-dong/">수진동</a></li>
<li><a href="/seongnam/sujeong-gu/dandae-dong/">단대동</a></li>
<li><a href="/seongnam/sujeong-gu/sanseong-dong/">산성동</a></li>
<li><a href="/seongnam/sujeong-gu/yangji-dong/">양지동</a></li>
<li><a href="/seongnam/sujeong-gu/bokjeong-dong/">복정동</a></li>
<li><a href="/seongnam/sujeong-gu/changgok-dong/">창곡동</a></li>
<li><a href="/seongnam/sujeong-gu/godeung-dong/">고등동</a></li>
<li><a href="/seongnam/sujeong-gu/geumto-dong/">금토동</a></li>
</ul>
</section>

<section id="jungwon">
<h2>중원구 지역 안내</h2>
<p>중원구는 모란시장과 성남산업단지를 품은 성남의 원도심입니다. 언덕을 따라 주택가가 펼쳐진 금광동·은행동과 일터가 모인 상대원동, 새 아파트가 들어선 도촌동·여수동이 함께 있습니다.</p>
<ul class="card-grid">
<li><a href="/seongnam/jungwon-gu/seongnam-dong/">성남동</a></li>
<li><a href="/seongnam/jungwon-gu/jungang-dong/">중앙동</a></li>
<li><a href="/seongnam/jungwon-gu/geumgwang-dong/">금광동</a></li>
<li><a href="/seongnam/jungwon-gu/eunhaeng-dong/">은행동</a></li>
<li><a href="/seongnam/jungwon-gu/sangdaewon-dong/">상대원동</a></li>
<li><a href="/seongnam/jungwon-gu/hadaewon-dong/">하대원동</a></li>
<li><a href="/seongnam/jungwon-gu/dochon-dong/">도촌동</a></li>
<li><a href="/seongnam/jungwon-gu/yeosu-dong/">여수동</a></li>
</ul>
</section>

<section id="bundang">
<h2>분당구 지역 안내</h2>
<p>분당구는 분당 신도시와 판교테크노밸리가 자리한 성남 남부의 대규모 생활권입니다. 정자동·서현동 같은 신도시 중심부터 판교동·삼평동의 업무 지구, 구미동·금곡동의 남부 주거지까지 폭넓게 안내합니다.</p>
<ul class="card-grid">
<li><a href="/seongnam/bundang-gu/bundang-dong/">분당동</a></li>
<li><a href="/seongnam/bundang-gu/sunae-dong/">수내동</a></li>
<li><a href="/seongnam/bundang-gu/jeongja-dong/">정자동</a></li>
<li><a href="/seongnam/bundang-gu/seohyeon-dong/">서현동</a></li>
<li><a href="/seongnam/bundang-gu/imae-dong/">이매동</a></li>
<li><a href="/seongnam/bundang-gu/yatap-dong/">야탑동</a></li>
<li><a href="/seongnam/bundang-gu/gumi-dong/">구미동</a></li>
<li><a href="/seongnam/bundang-gu/geumgok-dong/">금곡동</a></li>
<li><a href="/seongnam/bundang-gu/baekhyeon-dong/">백현동</a></li>
<li><a href="/seongnam/bundang-gu/sampyeong-dong/">삼평동</a></li>
<li><a href="/seongnam/bundang-gu/pangyo-dong/">판교동</a></li>
<li><a href="/seongnam/bundang-gu/unjeong-dong/">운중동</a></li>
<li><a href="/seongnam/bundang-gu/daejang-dong/">대장동</a></li>
</ul>
</section>

<section id="stations">
<h2>지하철역 인근 안내</h2>
<p>성남은 8호선, 수인분당선, 신분당선, 경강선, GTX-A 다섯 개 노선이 지나는 도시입니다. 역 페이지는 역 하나당 하나만 운영하며, 모란역이나 판교역 같은 환승역도 URL은 하나입니다.</p>
<ul class="card-grid">
<li><a href="/seongnam/stations/moran-station/">모란역</a></li>
<li><a href="/seongnam/stations/yatap-station/">야탑역</a></li>
<li><a href="/seongnam/stations/seohyeon-station/">서현역</a></li>
<li><a href="/seongnam/stations/sunae-station/">수내역</a></li>
<li><a href="/seongnam/stations/jeongja-station/">정자역</a></li>
<li><a href="/seongnam/stations/migeum-station/">미금역</a></li>
<li><a href="/seongnam/stations/ori-station/">오리역</a></li>
<li><a href="/seongnam/stations/pangyo-station/">판교역</a></li>
<li><a href="/seongnam/stations/seongnam-station/">성남역</a></li>
<li><a href="/seongnam/stations/gachon-univ-station/">가천대역</a></li>
<li><a href="/seongnam/stations/taepyeong-station/">태평역</a></li>
<li><a href="/seongnam/stations/sinheung-station/">신흥역</a></li>
<li><a href="/seongnam/stations/sujin-station/">수진역</a></li>
<li><a href="/seongnam/stations/dandaeogeori-station/">단대오거리역</a></li>
<li><a href="/seongnam/stations/namhansanseong-entrance-station/">남한산성입구역</a></li>
</ul>
<p>전체 역 목록과 노선별 구성은 <a href="/seongnam/stations/">지하철역별 안내</a>에서 확인하세요.</p>
</section>

<section id="themes">
<h2>테마별 관리 안내</h2>
<p>부드러운 이완이 필요하면 스웨디시나 아로마테라피, 시원하게 풀고 싶으면 타이마사지나 스포츠·경락 계열이 어울립니다. 각 테마 페이지에 특징과 추천 대상을 정리해 두었습니다.</p>
<ul class="card-grid">
<li><a href="/themes/swedish/">스웨디시</a></li>
<li><a href="/themes/lomilomi/">로미로미</a></li>
<li><a href="/themes/thai/">타이마사지</a></li>
<li><a href="/themes/chinese/">중국마사지</a></li>
<li><a href="/themes/aroma/">아로마테라피</a></li>
<li><a href="/themes/homecare/">홈케어</a></li>
<li><a href="/themes/hotel-style/">호텔식마사지</a></li>
<li><a href="/themes/foot/">발마사지</a></li>
<li><a href="/themes/sports/">스포츠·경락</a></li>
<li><a href="/themes/skincare/">스킨케어</a></li>
<li><a href="/themes/waxing/">왁싱</a></li>
<li><a href="/themes/couple/">커플 관리</a></li>
<li><a href="/themes/24hours/">24시간</a></li>
<li><a href="/themes/overnight/">수면 가능</a></li>
</ul>
</section>

<section id="course">
<h2>코스 선택 안내</h2>
<p>코스는 60분, 90분, 120분 세 가지가 기본입니다. 처음이라 감이 안 오시면 전신을 고르게 다루는 90분을, 풀고 싶은 부위가 분명하면 60분을, 피로가 오래 쌓였다면 120분을 권합니다. 자세한 구성과 요금은 <a href="/courses/">코스안내</a>에서 비교해 보세요.</p>
</section>

<section id="booking">
<h2>예약 진행 방식</h2>
<p>예약은 전화 한 통으로 끝납니다. 위치와 희망 시간을 말씀해 주시면 가능 여부를 바로 확인하고, 코스와 인원을 정한 뒤 도착 예정 시간을 안내해 드립니다. 회원가입이나 선결제 없이 관리 후 현장에서 결제하시면 됩니다. 상세 절차는 <a href="/reservation/">예약안내</a>에 있습니다.</p>
</section>

<section id="check">
<h2>이용 전 확인사항</h2>
<p>방문 전에 매트 한 장을 펼 자리를 정해 주시고, 도로명 주소와 공동현관 출입 방법을 미리 알려주세요. 시술 부위에 상처나 피부 질환이 있거나 임신 중이시면 예약 단계에서 꼭 말씀해 주셔야 합니다. 그 외 준비사항은 <a href="/guide/">이용가이드</a>에 정리되어 있습니다.</p>
</section>

<section id="safety">
<h2>위생 및 안전 안내</h2>
<p>관리사는 방문마다 소독한 장비와 세탁된 리넨을 사용하며, 시술 전 손 소독을 기본으로 합니다. 관리 강도는 진행 중 언제든 조절을 요청하실 수 있습니다. {BRAND}는 건전한 방문 관리 서비스만 운영하며, 안내된 관리 범위를 벗어나는 요청에는 어떤 경우에도 응하지 않습니다.</p>
</section>

<section id="faq">
<h2>자주 묻는 질문</h2>
<div class="faq-item">
<h3>밤 늦게도 예약이 되나요?</h3>
<p>네, 상담은 24시간 받고 있습니다. 심야 시간대는 배정 상황에 따라 대기가 생길 수 있어 미리 연락 주시면 확실합니다.</p>
</div>
<div class="faq-item">
<h3>호텔이나 모텔로도 와 주나요?</h3>
<p>가능합니다. 객실 방문 시 호텔명과 객실 번호를 알려주시고, 프런트 출입 규정이 있는 곳은 미리 확인해 주시면 진행이 매끄럽습니다.</p>
</div>
<div class="faq-item">
<h3>여성 이용자 혼자도 괜찮은가요?</h3>
<p>네, 혼자 계신 여성 이용자 예약도 많습니다. 원하시면 예약 시 관리사 성별을 요청하실 수 있습니다.</p>
</div>
</section>
""" + PRICING

PAGE = {
    "path": "",
    "title": "성남 출장마사지·홈타이 | 성남 전지역 방문 마사지 예약 안내",
    "desc": "성남 출장마사지·홈타이 안내 페이지입니다. 수정구, 중원구, 분당구와 모란역, 야탑역, 서현역, 판교역 등 성남 주요 지역과 지하철역 인근 예약 정보를 확인해보세요.",
    "h1": "성남 출장마사지·홈타이 예약 안내",
    "body": _BODY + f"""
<section class="cta" id="contact">
<h2>예약문의</h2>
<p>방문 위치와 희망 시간만 알려주세요. 가능 여부 확인부터 도착 안내까지 한 번의 통화로 끝납니다. 연중무휴 24시간 상담 가능합니다.</p>
<a class="cta-phone" href="tel:{PHONE}">{PHONE_DISPLAY}</a>
</section>
""",
    "hero": _HERO,
    "extra_head": _JSONLD,
    "breadcrumb": [],
}

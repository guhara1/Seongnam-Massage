# 전체 페이지 목록 집계
from . import (main, areas, areas_sujeong, areas_jungwon, areas_bundang,
               stations, stations_bundang, themes, info, about)

PAGES = (
    [main.PAGE]
    + areas.PAGES
    + areas_sujeong.PAGES
    + areas_jungwon.PAGES
    + areas_bundang.PAGES
    + stations.PAGES
    + stations_bundang.PAGES
    + themes.PAGES
    + info.PAGES
    + [about.PAGE]
)

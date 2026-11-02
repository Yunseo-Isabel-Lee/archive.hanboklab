# archive.hanboklab

HanbokLab의 한국 복식 아카이브 모음 — https://archive.hanboklab.com

| 경로 | 아카이브 |
|---|---|
| `/hyungbae/` | 조선 흉배 아카이브 (시제품) |

연구 소개, 온톨로지 문서, 데이터 주소(`hanbok:` `hanbokc:` `hanboko:`)는 메인 저장소 [hanboklab](https://github.com/Yunseo-Isabel-Lee/hanboklab)(https://hanboklab.com)에 있다. 유물·개념의 URI는 이 저장소로 옮기지 않고 `https://hanboklab.com/...` 그대로 쓴다.

## 스크립트

| 스크립트 | 하는 일 | 사용 |
|---|---|---|
| scripts/make_archive_data.py | 국중박·메트로폴리탄 출처 시트 → 공개 시제품용 아카이브데이터.csv | `python3 make_archive_data.py <국중박 json> <메트 json> <통합시트 json> <출력 csv>` |
| scripts/make_archive_site.py | 아카이브데이터 + 개념 → 시제품 페이지(hyungbae/) | `python3 make_archive_site.py <데이터 폴더> <개념.csv 폴더> <출력 폴더>` |

`개념.csv`는 메인 저장소의 `scripts/make_concepts.py`로 만든다.

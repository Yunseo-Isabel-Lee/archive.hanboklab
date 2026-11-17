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
| scripts/make_archive_site.py | 흉배58(+근거) + 개념 → 시제품 페이지(hyungbae/)와 ask-guide.md | `python3 make_archive_site.py <데이터 폴더> <개념.csv 폴더> <출력 폴더>` (데이터 폴더에 흉배58.csv·.ttl·흉배58_근거.csv, 개념.csv·.ttl) |

`개념.csv`는 메인 저장소의 `scripts/make_concepts.py`로 만든다.

## 문장으로 묻기

`/hyungbae/#/ask`는 질문을 Cloudflare Worker(`hanbok-ask`, API 키 보관)에 보내 SPARQL을 받고, 브라우저에서 Oxigraph로 `data.ttl`·`concepts.ttl`에 실행한 뒤 결과로 답변을 받는다. Worker는 이 폴더의 `ask-guide.md`와 `concepts.ttl`을 읽어 데이터 모양을 알기 때문에, 데이터를 바꿔 다시 만들면 Worker는 고치지 않아도 된다. Worker가 안 되면 개념 사전 방식으로 대신 찾는다.

"""조선 흉배 아카이브 시제품 페이지 만들기 (정적, GitHub Pages용)
사용: python3 make_archive_site.py <데이터 폴더> <개념.csv 폴더> <출력 폴더>
  데이터 폴더: 흉배58.csv(+ 흉배58_근거.csv) — 없으면 예전 형식 아카이브데이터.csv
  출력: index.html, ask-guide.md(문장으로 묻기 Worker가 읽는 데이터 설명)
"""
import csv, json, os, sys, collections
src, cdir, out = sys.argv[1:4]
os.makedirs(out, exist_ok=True)
rd = lambda p: list(csv.DictReader(open(p, encoding="utf-8-sig")))
data_p = next(os.path.join(src, f) for f in ("흉배58.csv", "아카이브데이터.csv") if os.path.exists(os.path.join(src, f)))
items = rd(data_p)
ev_p = os.path.join(src, "흉배58_근거.csv")
evs = rd(ev_p) if os.path.exists(ev_p) else []
con = rd(os.path.join(cdir, "개념.csv"))
split = lambda s: [x.strip() for x in (s or "").split(";") if x.strip()]
C = {}
for r in con:
    C[r["conceptID"]] = {"id": r["conceptID"], "s": r["scheme"], "ko": r["prefLabel_ko"], "en": r["prefLabel_en"],
                        "alt": split(r["altLabels"]), "b": split(r["broader"]), "rel": split(r["related"]),
                        "note": r["scopeNote"]}
OLD_KEEP = {"nmk": ["국립중앙박물관", "National Museum of Korea"], "met": ["메트로폴리탄 미술관", "The Metropolitan Museum of Art"]}
KEEP = {}
for r in items:
    KEEP.setdefault(r["keeper"], [r.get("keeper_ko") or OLD_KEEP.get(r["keeper"], [r["keeper"]])[0],
                                  r.get("keeper_en") or OLD_KEEP.get(r["keeper"], ["", ""])[1]])
EV_T = {"recordStated": "기관 기재", "ruleDerived": "도출(규칙)", "archiveAssigned": "아카이브 부여",
        "researcherConfirmed": "연구자 확인", "researcherRead": "연구자 판독"}
EVI = collections.defaultdict(list)
for e in evs:
    v = e["값"]
    if v.startswith("hanbokc:"):
        v = C.get(v[8:], {}).get("ko", v[8:])
    elif v.startswith("hanboko:actor-"):
        v = KEEP.get(v[14:], [v])[0]
    elif v.startswith("http"):
        v = "이미지 주소"
    else:
        v = v.rsplit("@", 1)[0] if "@" in v[-8:] else v
    EVI[e["objectID"]].append({"p": e["속성 라벨"], "v": v, "t": e["근거 유형"], "rec": e["근거 레코드"],
                               "col": e["근거 칸"], "ex": e["근거 발췌"] if not e["근거 발췌"].startswith("imageId=") else "",
                               "note": e["비고"]})
I = []
for r in items:
    I.append({"id": r["objectID"], "ko": r["title_ko"], "hani": r["title_hani"], "en": r["title_en"], "no": r["keeperNo"],
              "motif": r["motif"], "period": split(r["period"]), "date": r.get("date", ""), "h": r["height"], "w": r["width"],
              "lic": r["license"], "use": r.get("wearingContext", ""),
              "img": [u.replace(" ", "%20") for u in split(r["images"])], "keeper": r["keeper"], "src": r["recordSource"],
              "rec": r["recordID"], "o_period": r["원문_시대"], "o_size": r["원문_크기"], "o_lic": r["원문_이용조건"], "note": r["비고"],
              "ev": EVI.get(r["objectID"], [])})
DATA = json.dumps({"items": I, "concepts": C, "keepers": KEEP, "evtypes": EV_T}, ensure_ascii=False)

# ── 문장으로 묻기: Worker가 읽어 가는 데이터 설명(데이터가 바뀌면 이 파일도 같이 바뀐다)
lic_n = collections.Counter(r["license"] for r in items)
dates = sorted({r.get("date", "") for r in items if r.get("date")})
GUIDE = f"""# 조선 흉배 아카이브 — 데이터 설명 (문장으로 묻기용, 자동 생성)

## 범위
- 한국 흉배 실물 {len(items)}점, 소장처 {len(KEEP)}곳. 소장처가 시기를 적어 둔 유물만 실었다. 초상화 속 흉배·단령·중국 보자는 없다.
- 값(문양·시기·크기·이용조건)은 소장처 기록에서 뽑아 정리했고, 값마다 근거 주석이 있다.
- 이용조건: {", ".join(f"{C.get(k, {}).get('ko', k)} {n}점" for k, n in lic_n.most_common())}

## PREFIX (쿼리에 모두 적는다)
PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX schema: <http://schema.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX hanbokc: <https://hanboklab.com/concept/>
PREFIX hanboko: <https://hanboklab.com/object/>

## 흉배 유물 ?item (IRI는 hanboko:hb0041 꼴)
?item a crm:E22_Human-Made_Object ;
  crm:P2_has_type hanbokc:hyungbae ;            # 자료 구분. 같은 속성에 주문양 개념도 붙는다(없을 수 있음)
  dcterms:title "쌍학흉배"@ko , "雙鶴胸背"@ko-Hani , "…"@en ;
  dcterms:identifier "공주53361" ;               # 소장처 유물번호(없을 수 있음)
  dcterms:spatial hanbokc:korea ;               # 국적(모두 한국)
  dcterms:temporal hanbokc:c19late ;            # 시기 개념, 가장 구체적인 것에만 연결(여러 개일 수 있음)
  dcterms:date "1864/1892" ;                    # 소장처가 연도를 적은 경우만, EDTF 글자
  schema:height 16.5 ; schema:width 15.5 ;      # 세로·가로 cm, xsd:decimal 숫자(없을 수 있음)
  dcterms:license hanbokc:cc0 ;                 # 이용조건 개념(licenseUnknown = 확인 중)
  crm:P101_had_as_general_use hanbokc:gwanbok ; # 착용 맥락(일부만)
  crm:P50_has_current_keeper hanboko:actor-met ;
  foaf:depiction <이미지 주소> .
dcterms:date 실제 값: {", ".join(dates)}

## 소장처 (rdfs:label 한글@ko)
""" + "\n".join(f"hanboko:actor-{k} = {v[0]}" + (f" / {v[1]}" if v[1] else "") for k, v in KEEP.items()) + """

## 기관 레코드(원문 기록)
?rec a crm:E31_Document ; crm:P70_documents ?item ; dcterms:identifier "e뮤지엄-…" ; dcterms:publisher ?기관 ; dcterms:source <원 페이지> .

## 값마다 붙은 근거 주석
?ev a rdf:Statement ; rdf:subject ?item ; rdf:predicate dcterms:temporal ; rdf:object hanbokc:c19 ;
    dcterms:type hanbokc:recordStated ;   # 근거 유형: recordStated 기관 기재 / ruleDerived 도출(규칙) / archiveAssigned 아카이브 부여 / researcherConfirmed 연구자 확인
    prov:wasDerivedFrom ?rec ; prov:atLocation "국적/시대" ;   # 근거 칸(글자)
    prov:value "한국-대한제국" ;          # 원문 발췌
    skos:editorialNote "…" .              # 비고(있을 때만)

## 개념
개념 목록은 concepts.ttl(아래)에 있다. skos:prefLabel·altLabel(이칭·한자·'~문'·'~무늬'), skos:broader(상위), skos:related(경계가 겹침), skos:inScheme.
- 문양은 상하 관계가 있다(쌍학·단학·운학·백학·선학 → 학 → 날짐승). "학 흉배"는 하위까지: hanbokc:hak ^skos:broader* ?m .
- 시기도 상하 관계(19세기 후반 → 19세기). "조선 말기"처럼 경계가 겹치는 개념은 skos:related로 세기와 이어져 있다.
- 이용조건은 상위로 묶여 있다: 공공누리1·3·CC0 → hanbokc:commercialOk(상업 이용 가능), 공공누리2·4·CC BY-NC → hanbokc:commercialNo.
"""
open(os.path.join(out, "ask-guide.md"), "w", encoding="utf-8").write(GUIDE)

html = r"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>조선 흉배 아카이브 · 시제품</title>
<meta name="description" content="조선 흉배 아카이브 시제품 — 여러 소장처의 한국 흉배를 문양·시기·이용조건으로 찾고, 값마다 근거를 보여 준다.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;1,400&family=Noto+Sans+KR:wght@300;400;500&family=Noto+Serif+KR:wght@200;300;400;500&display=swap" rel="stylesheet">
<style>
:root{--paper:#0a0908;--paper-2:#11100e;--card:#141210;--ink:#ece5d6;--ink-2:#b5ad9f;--muted:#7f786d;--line:rgba(236,229,214,.13);--line-2:rgba(236,229,214,.07);--cream:#f3ead6;--gold:#c49a6c;
--serif:"Noto Serif KR",serif;--sans:"Noto Sans KR",system-ui,sans-serif;--latin:"Cormorant Garamond","Noto Serif KR",serif;--mono:ui-monospace,Menlo,Consolas,monospace}
*{box-sizing:border-box} html{scroll-behavior:smooth}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);font-weight:300;font-size:14.5px;line-height:1.7;word-break:keep-all}
a{color:inherit;text-decoration:none} button{font-family:inherit}
.wrap{max-width:1240px;margin:0 auto;padding:0 clamp(18px,4vw,56px)}
/* 머리 */
.proto{background:#1b1712;color:#cdb48a;font-size:12px;text-align:center;padding:6px 12px;letter-spacing:.04em}
.proto a{border-bottom:1px solid rgba(205,180,138,.4)}
header.site{position:sticky;top:0;z-index:20;background:rgba(10,9,8,.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
header.site .wrap{display:flex;align-items:center;gap:40px;height:72px}
.logo{display:flex;align-items:center;gap:12px}
.seal{width:32px;height:32px;border:1px solid var(--ink);display:grid;place-items:center;font-family:var(--serif);font-size:15px}
.logo b{font-weight:400;font-size:12.5px;letter-spacing:.3em}
nav.main{display:flex;gap:28px;font-size:12px;letter-spacing:.16em;color:var(--ink-2)}
nav.main a{padding-bottom:4px;border-bottom:1px solid transparent} nav.main a.on,nav.main a:hover{color:var(--ink);border-color:var(--ink)}
.hsearch{margin-left:auto;display:flex;align-items:center;gap:8px;border-bottom:1px solid var(--line);padding:4px 0;width:220px}
.hsearch input{background:none;border:0;color:var(--ink);font:inherit;font-size:12.5px;width:100%;outline:none}
/* 공통 */
.page{padding:48px 0 90px;min-height:70vh}
.crumb{font-size:11.5px;color:var(--muted);letter-spacing:.06em;margin-bottom:22px}
.crumb a:hover{color:var(--ink)}
.kick{font-family:var(--latin);font-style:italic;color:var(--gold);font-size:17px}
h1,h2,h3{font-family:var(--serif);font-weight:300;margin:0}
.btn{display:inline-flex;align-items:center;gap:8px;border:1px solid var(--line);padding:9px 16px;font-size:11.5px;letter-spacing:.14em;color:var(--ink);background:transparent;cursor:pointer}
.btn:hover{border-color:var(--ink)}
.btn.cream{background:var(--cream);border-color:var(--cream);color:#16130f;outline:1px solid rgba(243,234,214,.45);outline-offset:3px}
.chip{display:inline-flex;align-items:center;gap:6px;border-bottom:1px solid var(--line);padding:1px 0;font-size:12.5px;color:var(--ink);cursor:pointer;margin-right:12px}
.chip.x::after{content:"×";color:var(--muted)}
.muted{color:var(--muted)} .empty{color:#5d574f}
/* 이미지 */
.media{position:relative;overflow:hidden;background:#15120f;aspect-ratio:4/5}
.media img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transition:transform .8s}
.ph{position:absolute;inset:0;display:grid;place-items:center;background:radial-gradient(ellipse 75% 60% at 50% 42%,#1c1814,#100e0c 75%)}
.ph span{font-family:var(--serif);font-weight:200;font-size:56px;color:rgba(236,229,214,.12)}
/* 첫 화면 */
.hero{display:grid;grid-template-columns:1.1fr .9fr;gap:60px;align-items:center;min-height:min(80vh,720px);padding:40px 0}
.hero h1{font-size:clamp(36px,4.4vw,54px);letter-spacing:.22em;margin:10px 0 22px}
.hero p{color:var(--ink-2);max-width:470px}
.hero .acts{display:flex;gap:16px;margin-top:34px;flex-wrap:wrap}
.hero figure{margin:0;justify-self:center;width:min(360px,100%);cursor:pointer}
.hero figure .media{aspect-ratio:1/1;box-shadow:0 44px 80px rgba(0,0,0,.7)}
.hero figcaption{font-size:11.5px;color:var(--muted);margin-top:18px;text-align:center}
.findline{display:flex;gap:16px;align-items:center;border-bottom:1px solid var(--line);padding-bottom:12px;max-width:640px;margin:40px auto 0}
.findline input{flex:1;background:none;border:0;color:var(--ink);font:inherit;font-size:15px;outline:none}
.sec{padding:100px 0 0}
.sec-h{text-align:center;margin-bottom:46px}
.sec-h h2{font-size:23px;letter-spacing:.3em;text-indent:.3em}
.sec-h p{color:var(--muted);font-size:12.5px;margin:12px 0 0}
.tiles{display:flex;gap:22px;overflow-x:auto;scrollbar-width:none;padding-bottom:6px}
.tile{flex:0 0 250px;position:relative;cursor:pointer}
.tile .media{aspect-ratio:3/4}
.tile .ov{position:absolute;inset:auto 0 0 0;padding:90px 20px 20px;background:linear-gradient(180deg,transparent,rgba(6,5,4,.88))}
.tile b{display:block;font-family:var(--serif);font-weight:300;font-size:22px;letter-spacing:.16em}
.tile small{font-family:var(--latin);font-size:16px;color:#b2aa9b}
.tile:hover img{transform:scale(1.06)}
.info{display:grid;grid-template-columns:1fr 1.4fr;margin-top:110px}
.info .cream{background:var(--cream);color:#1b1814;padding:40px}
.info .cream h4{font-family:var(--serif);font-weight:400;letter-spacing:.2em;margin:0 0 20px;font-size:14px}
.stat{display:flex;align-items:baseline;gap:12px;padding:10px 0;border-top:1px solid rgba(27,24,20,.14)}
.stat b{font-family:var(--latin);font-weight:500;font-size:40px;line-height:1;min-width:84px}
.stat span{font-size:12.5px;color:#5a544b}
.info .dark{background:#15120f;padding:40px 44px}
.info .dark h4{font-family:var(--serif);font-weight:300;letter-spacing:.18em;font-size:17px;margin:0 0 14px}
.info .dark p{color:var(--ink-2);font-size:13px;margin:0 0 12px}
/* 카드 */
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:40px 24px}
.card{cursor:pointer}
.card:hover img{transform:scale(1.07)}
.card .src{font-size:11px;color:var(--muted);margin:14px 0 4px;letter-spacing:.03em}
.card h4{font-family:var(--serif);font-weight:400;font-size:15px;letter-spacing:.04em;margin:0 0 6px;line-height:1.45}
.card .mt{font-size:12px;color:var(--ink-2)}
.lic{display:inline-flex;align-items:center;gap:7px;font-size:12px;color:var(--ink-2);margin-top:6px}
.lic::before{content:"";width:7px;height:7px;border-radius:50%;border:1px solid var(--cream)}
.lic.ok::before{background:var(--cream)}
/* 검색 */
.searchbar{display:flex;gap:14px;align-items:center;margin-bottom:40px}
.searchbar input{flex:1;background:none;border:0;border-bottom:1px solid var(--line);color:var(--ink);font:inherit;font-size:15px;padding:12px 2px;outline:none}
.layout{display:grid;grid-template-columns:230px 1fr;gap:56px}
.facet{border-top:1px solid var(--line);padding:16px 0}
.facet h5{font-family:var(--serif);font-weight:400;font-size:13px;letter-spacing:.2em;margin:0 0 10px}
.opt{display:flex;align-items:center;gap:10px;padding:3px 0;font-size:12.5px;color:var(--ink-2);cursor:pointer}
.opt.sub{padding-left:18px} .opt.sub2{padding-left:36px}
.opt i{width:11px;height:11px;border:1px solid var(--muted);flex:none}
.opt.on{color:var(--ink)} .opt.on i{background:var(--cream);border-color:var(--cream)}
.opt .n{margin-left:auto;font-family:var(--latin);font-size:14px;color:var(--muted)}
.opt.zero{opacity:.35;cursor:default}
.restop{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:30px}
.restop .count{font-family:var(--latin);font-size:38px;line-height:1;margin-right:8px}
.restop select{margin-left:auto;background:var(--card);color:var(--ink-2);border:1px solid var(--line);font:inherit;font-size:12px;padding:6px 8px}
.zero-box{border-top:1px solid var(--line);padding:40px 0}
.zero-box h3{font-size:22px;letter-spacing:.16em;margin-bottom:10px}
/* 개별 */
.item{display:grid;grid-template-columns:1.05fr 1fr;gap:60px}
.viewer .media{aspect-ratio:1/1;background:#070605}
.viewer .media img{object-fit:contain}
.thumbs{display:flex;gap:10px;margin-top:12px}
.thumbs button{width:58px;height:58px;padding:0;border:1px solid var(--line);background:#070605;cursor:pointer;overflow:hidden}
.thumbs button.on{outline:1px solid var(--cream);outline-offset:2px}
.thumbs img{width:100%;height:100%;object-fit:cover}
.usebar{display:flex;align-items:center;gap:14px;flex-wrap:wrap;padding:16px 0;border-bottom:1px solid var(--line);font-size:12.5px;color:var(--ink-2)}
.usebar .credit{flex:1;min-width:220px}
.item h1{font-size:30px;letter-spacing:.12em;line-height:1.35}
.item .hani{font-size:17px;color:var(--muted);letter-spacing:.12em;margin-top:4px}
.item .orig{font-family:var(--latin);font-style:italic;font-size:17px;color:var(--gold);margin:6px 0 22px}
.path{display:flex;align-items:center;gap:10px;flex-wrap:wrap;border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:14px 0;font-size:13px}
.path a{border-bottom:1px solid var(--line)} .path .arr{color:var(--muted)}
dl.meta{display:grid;grid-template-columns:110px 1fr;margin:0}
dl.meta dt,dl.meta dd{padding:12px 0;border-top:1px solid var(--line-2);margin:0}
dl.meta dt{color:var(--muted);font-size:12.5px}
.raw{display:block;color:var(--muted);font-size:12px}
.box{border-top:1px solid var(--line);padding-top:20px;margin-top:26px}
.box h5{font-family:var(--serif);font-weight:400;letter-spacing:.16em;font-size:13px;margin:0 0 10px}
table.orig-t{width:100%;border-collapse:collapse;font-size:12.5px}
table.orig-t th,table.orig-t td{text-align:left;padding:8px 10px 8px 0;border-bottom:1px solid var(--line-2);vertical-align:top}
table.orig-t th{color:var(--muted);font-weight:400;width:26%}
.tools{display:flex;gap:12px;flex-wrap:wrap;margin-top:24px}
/* 문양 */
.concept{display:grid;grid-template-columns:240px 1fr 280px;gap:50px;padding-bottom:50px;margin-bottom:50px;border-bottom:1px solid var(--line)}
.concept .frame{padding:12px;border:1px solid rgba(243,234,214,.3)}
.concept .frame .media{aspect-ratio:3/4}
.concept h1{font-size:40px;letter-spacing:.2em}
.concept h1 span{font-size:19px;color:var(--muted);margin-left:10px;letter-spacing:.1em}
.side{border-top:1px solid var(--line);padding:14px 0}
.side h5{font-family:var(--serif);font-weight:400;font-size:12.5px;letter-spacing:.18em;color:var(--muted);margin:0 0 8px}
.labels span{display:inline-block;border-bottom:1px solid var(--line);margin:0 10px 6px 0;font-size:12.5px}
/* 자연어 */
.ask input{width:100%;background:none;border:0;border-bottom:1px solid var(--line);color:var(--ink);font-family:var(--serif);font-weight:300;font-size:26px;letter-spacing:.04em;padding:8px 0 18px;outline:none}
.examples{display:flex;gap:10px 18px;flex-wrap:wrap;margin:18px 0 0}
.examples span{font-size:12.5px;color:var(--ink-2);border-bottom:1px solid var(--line);cursor:pointer}
.examples span:hover{color:var(--ink)}
.parsed{display:flex;gap:10px 18px;flex-wrap:wrap;align-items:center;margin:28px 0 36px;font-size:13px;color:var(--ink-2)}
.parsed q{color:var(--muted)} .parsed q::before{content:"“"} .parsed q::after{content:"”"}
details.sparql{border:1px solid var(--line);margin-top:56px}
details.sparql summary{padding:14px 18px;cursor:pointer;font-family:var(--serif);letter-spacing:.14em;font-size:13px}
details.sparql pre{margin:0;padding:18px;background:#070605;color:#dfe5ee;font-family:var(--mono);font-size:12px;line-height:1.6;overflow-x:auto;white-space:pre}
.note{font-size:12px;color:var(--muted);margin-top:14px}
.evt{display:inline-block;font-size:10.5px;letter-spacing:.04em;padding:1px 7px;border:1px solid var(--line);color:var(--ink-2);margin-left:8px;vertical-align:1px;white-space:nowrap}
.evt.recordStated{border-color:rgba(243,234,214,.55);color:var(--cream)} .evt.ruleDerived{border-color:rgba(196,154,108,.6);color:var(--gold)}
table.ev-t td.ex{color:var(--ink-2)} table.ev-t td small{display:block;color:var(--muted);font-size:11.5px}
.answer{font-family:var(--serif);font-weight:300;font-size:18px;line-height:1.8;letter-spacing:.02em;margin:30px 0 8px;max-width:820px}
.status{font-size:13px;color:var(--ink-2);margin:28px 0}
.status .dot{display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--gold);margin-right:10px;animation:blink 1s infinite}
@keyframes blink{50%{opacity:.2}}
table.rows{width:100%;border-collapse:collapse;font-size:12px;margin-top:10px} table.rows th,table.rows td{text-align:left;padding:6px 10px 6px 0;border-bottom:1px solid var(--line-2);vertical-align:top}
table.rows th{color:var(--muted);font-weight:400}
/* 꼬리 */
footer.site{border-top:1px solid var(--line);padding:34px 0 40px;font-size:12px;color:var(--muted)}
footer.site .wrap{display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap}
footer.site a{border-bottom:1px solid var(--line)}
@media (max-width:900px){
 .hero,.item,.concept,.info{grid-template-columns:1fr} .layout{grid-template-columns:1fr} nav.main{display:none} .hsearch{display:none}
 .hero{gap:30px} .concept{gap:24px}
}
</style>
</head>
<body>
<div class="proto">시제품 · 비상업 연구·교육용 · 시기가 기록된 한국 흉배 <span id="protoN"></span>점 · 이미지와 기록은 각 소장처의 이용조건을 따릅니다 · <a href="https://hanboklab.com/ontology/">데이터 구조</a> · <a href="https://hanboklab.com/">hanboklab.com</a></div>
<header class="site"><div class="wrap">
  <a class="logo" href="#/"><span class="seal">胸</span><b>조선 흉배 아카이브</b></a>
  <nav class="main" id="nav"><a href="#/motif">문양별 보기</a><a href="#/search">검색</a><a href="#/ask">문장으로 묻기</a><a href="#/about">소개·데이터</a></nav>
  <form class="hsearch" id="hsearch"><input placeholder="쌍학, 雙鶴, 쌍학문 …" aria-label="검색"><span class="muted">⌕</span></form>
</div></header>
<main id="app" class="wrap"></main>
<footer class="site"><div class="wrap">
  <span>조선 흉배 아카이브 · 시제품 · 이윤서 · <a href="https://hanboklab.com/">hanboklab.com</a></span>
  <span>이미지와 소장처 기록은 각 소장처의 이용조건을 따릅니다 · 이 아카이브가 덧붙인 값은 CC BY 4.0</span>
</div></footer>
<script>
const D = __DATA__;
const I = D.items, C = D.concepts, K = D.keepers, EVT = D.evtypes || {};
document.getElementById("protoN").textContent = I.length;
const $ = s => document.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const HANJA = {ssanghak:"雙鶴",danhak:"單鶴",hak:"鶴",baekhak:"白鶴",unhak:"雲鶴",ssangho:"雙虎",danho:"單虎",horangi:"虎",hopyo:"虎豹",girin:"麒麟",naljimseung:"鳥",giljimseung:"獸"};
const LIC_OK = id => (C[id]?.b || []).includes("commercialOk");
const evTag = t => t ? `<span class="evt ${esc(t)}">${esc(EVT[t] || t)}</span>` : "";
const evOf = (it, labels) => it.ev.filter(e => labels.includes(e.p));
// 개념 계층
const kids = {}; Object.values(C).forEach(c => c.b.forEach(b => (kids[b] = kids[b] || []).push(c.id)));
const desc = id => [id, ...(kids[id] || []).flatMap(desc)];
const anc = id => { const c = C[id]; return c ? [id, ...c.b.flatMap(anc)] : []; };
const motifOf = it => it.motif ? anc(it.motif) : [];
const periodOf = it => it.period.flatMap(anc);
const label = id => C[id]?.ko || id;
function media(it, i=0){
  const u = it.img[i]; const ch = HANJA[it.motif] || "胸";
  return `<div class="media">${u?`<img src="${esc(u)}" alt="${esc(it.ko)}" loading="lazy" onerror="this.replaceWith(Object.assign(document.createElement('div'),{className:'ph',innerHTML:'<span>${ch}</span>'}))">`:""}<div class="ph" style="z-index:-1"><span>${ch}</span></div></div>`;
}
function card(it){
  const m = it.motif ? label(it.motif) : '<span class="empty">문양 판독 전</span>';
  const p = it.period.length ? it.period.map(label).join(", ") : '<span class="empty">시기 미상</span>';
  return `<a class="card" href="#/item/${it.id}">${media(it)}<div class="src">${esc(K[it.keeper][0])} · ${esc(it.no)}</div><h4>${esc(it.ko)}</h4><div class="mt">${m} · ${p}</div><span class="lic ${LIC_OK(it.lic)?"ok":""}">${esc(label(it.lic))}${LIC_OK(it.lic)?" · 상업 이용 가능":""}</span></a>`;
}
function setNav(r){ document.querySelectorAll("#nav a").forEach(a => a.classList.toggle("on", r && a.getAttribute("href").startsWith("#/"+r))); }

/* ── 홈 */
function home(){
  setNav("");
  const hero = I.find(x => x.no === "53.60.9") || I[0];
  const tops = ["ssanghak","danhak","hak","baekhak","ssangho","danho","hopyo","girin"].map(id => {
    const n = I.filter(it => motifOf(it).includes(id) && (id!=="hak" || it.motif==="hak")).length; return {id, n};
  }).filter(t => t.n);
  const unread = I.filter(it => !it.motif).length;
  const pick = id => I.find(it => it.motif === id && it.img.length && it.keeper === "met") || I.find(it => it.motif === id && it.img.length);
  $("#app").innerHTML = `
  <section class="hero">
    <div>
      <div class="kick">The Joseon Rank Badge Archive</div>
      <h1>조선 흉배<br>아카이브</h1>
      <p>여러 소장처에 흩어진 관복 흉배를 한자리에 모아, 문양·시기·이용조건으로 이어 찾고 비교합니다. 지금은 ${I.length}점을 담은 시제품입니다.</p>
      <div class="acts"><a class="btn cream" href="#/motif">문양으로 찾기</a><a class="btn" href="#/ask">문장으로 묻기</a></div>
    </div>
    <figure onclick="location.hash='#/item/${hero.id}'">${media(hero)}<figcaption>${esc(hero.ko)}, ${esc(hero.period.map(label).join(", "))} · ${esc(K[hero.keeper][0])} ${esc(hero.no)}</figcaption></figure>
  </section>
  <form class="findline" id="homefind"><input placeholder="문양, 소장처, 유물 이름 — 쌍학, 雙鶴, 쌍학문, 호랑이 …"><button class="btn">검색</button></form>
  <section class="sec">
    <div class="sec-h"><h2>문양으로 찾기</h2><p>상위 문양을 고르면 그 아래 문양까지 함께 나옵니다</p></div>
    <div class="tiles">${tops.map(t => { const it = pick(t.id); return `<a class="tile" href="#/motif/${t.id}">${it?media(it):'<div class="media"><div class="ph"><span>'+(HANJA[t.id]||"胸")+'</span></div></div>'}<div class="ov"><b>${label(t.id)}</b><small>${t.n}점</small></div></a>`; }).join("")}
      <a class="tile" href="#/search?motif=none"><div class="media"><div class="ph"><span>?</span></div></div><div class="ov"><b>판독 전</b><small>${unread}점</small></div></a></div>
  </section>
  <section class="sec">
    <div class="sec-h"><h2>최근 추가된 유물</h2></div>
    <div class="cards">${I.filter(i=>i.img.length).slice(-8).reverse().map(card).join("")}</div>
  </section>
  <div class="info">
    <div class="cream"><h4>이 시제품의 범위</h4>
      <div class="stat"><b>${I.length}</b><span>한국 흉배 실물</span></div>
      <div class="stat"><b>${Object.keys(K).length}</b><span>소장처</span></div>
      <div class="stat"><b>${I.reduce((a,b)=>a+b.img.length,0)}</b><span>이미지</span></div></div>
    <div class="dark"><h4>자료와 이용</h4>
      <p>이미지와 소장처 기록은 각 소장처의 이용조건을 따릅니다. 이 아카이브가 덧붙인 문양·시기 연결과 정리 값은 CC BY 4.0으로 공개합니다.</p>
      <p>전체 수집 자료는 56개 소장처, 흉배 344점입니다. 지금은 소장처가 시기를 적어 둔 ${I.length}점을 싣고, 값마다 어디서 왔는지(근거)를 함께 보여 줍니다. 이용조건을 확인 중인 유물은 「확인 중」으로 표시했습니다.</p>
      <a class="btn" href="#/about">범위와 데이터 →</a></div>
  </div>`;
  $("#homefind").onsubmit = e => { e.preventDefault(); location.hash = "#/search?q=" + encodeURIComponent(e.target.querySelector("input").value); };
}

/* ── 검색 */
const PTOP = Object.values(C).filter(c => c.s === "period" && !c.b.length && I.some(it => periodOf(it).includes(c.id))).map(c => c.id).sort((a,b) => (a[0]==="c"?a:"z"+a).localeCompare(b[0]==="c"?b:"z"+b));
const FACETS = {motif:"문양", period:"시기", lic:"이용조건", keeper:"소장처"};
function matchQ(it, q){
  if (!q) return true;
  q = q.trim().toLowerCase();
  const words = [it.ko, it.hani, it.en, it.no, K[it.keeper][0], K[it.keeper][1]];
  motifOf(it).concat(periodOf(it)).forEach(id => { const c = C[id]; if (c) words.push(c.ko, c.en, ...c.alt); });
  return words.some(w => w && w.toLowerCase().includes(q));
}
function filterItems(f){
  return I.filter(it =>
    matchQ(it, f.q) &&
    (!f.motif || (f.motif === "none" ? !it.motif : motifOf(it).includes(f.motif))) &&
    (!f.period || (f.period === "none" ? !it.period.length : periodOf(it).includes(f.period))) &&
    (!f.lic || it.lic === f.lic || (C[it.lic]?.b || []).includes(f.lic)) &&
    (!f.keeper || it.keeper === f.keeper));
}
function search(params){
  setNav("search");
  const f = Object.fromEntries(params);
  const res = filterItems(f);
  const sort = f.sort || "motif";
  res.sort((a,b) => sort === "size" ? (+b.w||0)-(+a.w||0) : sort === "keeper" ? a.keeper.localeCompare(b.keeper) : (label(a.motif)||"힣").localeCompare(label(b.motif)||"힣") || a.id.localeCompare(b.id));
  const link = (k, v) => { const p = new URLSearchParams(f); if (p.get(k) === v) p.delete(k); else p.set(k, v); return "#/search?" + p.toString(); };
  const cnt = (k, v) => filterItems({...f, [k]: v}).length;
  const opt = (k, v, name, cls="") => { const n = cnt(k, v), on = f[k] === v; return `<a class="opt ${cls} ${on?"on":""} ${n||on?"":"zero"}" href="${n||on?link(k,v):"javascript:void 0"}"><i></i>${name}<span class="n">${n}</span></a>`; };
  const tree = (id, d=0) => opt("motif", id, label(id), d===1?"sub":d>=2?"sub2":"") + (kids[id]||[]).filter(k => I.some(it => motifOf(it).includes(k))).map(k => tree(k, d+1)).join("");
  const chips = Object.entries(f).filter(([k]) => FACETS[k] || k==="q").map(([k,v]) => `<a class="chip x" href="${(()=>{const p=new URLSearchParams(f);p.delete(k);return "#/search?"+p})()}">${k==="q"?"검색어":FACETS[k]}: ${esc(v==="none"?(k==="motif"?"판독 전":"미상"):k==="keeper"?K[v][0]:k==="q"?v:label(v))}</a>`).join("");
  $("#app").innerHTML = `<div class="page">
  <form class="searchbar" id="sbar"><input value="${esc(f.q||"")}" placeholder="문양, 소장처, 유물 이름 — 쌍학, 雙鶴, 쌍학문 …"><button class="btn cream">검색</button><a class="btn" href="#/ask">문장으로 묻기</a></form>
  <div class="layout">
    <aside>
      <div class="facet"><h5>문양</h5>${tree("naljimseung")}${tree("giljimseung")}${opt("motif","none","판독 전")}</div>
      <div class="facet"><h5>시기</h5>${PTOP.map(id => opt("period", id, label(id)) + (kids[id]||[]).filter(k => I.some(it => periodOf(it).includes(k))).map(k => opt("period", k, label(k), "sub")).join("")).join("")}</div>
      <div class="facet"><h5>이용조건</h5>${["commercialOk","commercialNo"].map(g => opt("lic", g, label(g)) + (kids[g]||[]).filter(k => I.some(it => it.lic === k)).map(k => opt("lic", k, label(k), "sub")).join("")).join("")}${opt("lic","licenseUnknown",label("licenseUnknown"))}</div>
      <div class="facet"><h5>소장처</h5>${Object.keys(K).map(k => opt("keeper", k, K[k][0])).join("")}</div>
    </aside>
    <div>
      <div class="restop"><span class="count">${res.length}점</span>${chips}${chips?'<a class="chip" href="#/search">모두 지우기</a>':""}
        <select id="sort"><option value="motif">정렬: 문양</option><option value="size">정렬: 가로 큰 순</option><option value="keeper">정렬: 소장처</option></select></div>
      ${res.length ? `<div class="cards">${res.map(card).join("")}</div>` :
      `<div class="zero-box"><h3>조건에 맞는 흉배가 없습니다</h3><p class="muted">조건을 하나 풀거나, 문양 이름의 다른 표기(이칭)로 찾아보세요. 이 시제품은 시기가 기록된 한국 흉배 ${I.length}점만 담고 있습니다.</p><a class="btn" href="#/search">조건 모두 풀기</a></div>`}
    </div>
  </div></div>`;
  $("#sort").value = sort;
  $("#sort").onchange = e => { const p = new URLSearchParams(f); p.set("sort", e.target.value); location.hash = "#/search?" + p; };
  $("#sbar").onsubmit = e => { e.preventDefault(); const p = new URLSearchParams(f); const v = e.target.querySelector("input").value; v ? p.set("q", v) : p.delete("q"); location.hash = "#/search?" + p; };
}

/* ── 개별 유물 */
function item(id){
  setNav("");
  const it = I.find(x => x.id === id); if (!it) return notfound();
  const path = it.motif ? anc(it.motif).reverse() : [];
  const same = I.filter(x => x.id !== it.id && x.motif && x.motif === it.motif).slice(0, 4);
  const credit = `〈${it.ko}〉, ${K[it.keeper][0]} 소장(${it.no}), ${label(it.lic)}`;
  $("#app").innerHTML = `<div class="page">
  <div class="crumb"><a href="#/search">검색</a>${path.map(p => ` › <a href="#/motif/${p}">${label(p)}</a>`).join("")} › ${esc(it.ko)}</div>
  <div class="item">
    <div class="viewer">
      <div id="big">${media(it)}</div>
      ${it.img.length > 1 ? `<div class="thumbs">${it.img.map((u,i) => `<button data-i="${i}" class="${i?"":"on"}"><img src="${esc(u)}" alt=""></button>`).join("")}</div>` : ""}
      <div class="usebar"><span class="lic ${LIC_OK(it.lic)?"ok":""}">${esc(label(it.lic))}${LIC_OK(it.lic)?" · 상업 이용 가능":""}</span><span class="credit">출처 표기: ${esc(credit)}</span><button class="btn" id="copy">출처 표기 복사</button></div>
    </div>
    <div>
      <h1>${esc(it.ko)}</h1>${it.hani?`<div class="hani">${esc(it.hani)}</div>`:""}
      ${it.en?`<div class="orig">${esc(it.en)}</div>`:'<div style="height:18px"></div>'}
      <div class="path"><span class="muted">문양</span>${path.length ? path.map(p => `<a href="#/motif/${p}">${label(p)}</a>`).join('<span class="arr">→</span>') : '<span class="empty">판독 전 — 연구자가 이미지로 판독할 예정</span>'}</div>
      <dl class="meta">
        <dt>시기</dt><dd>${it.period.length ? it.period.map(p => `<a class="chip" href="#/search?period=${p}">${label(p)}</a>`).join("") : '<span class="empty">시기 미상</span>'}${evTag(evOf(it,["시기"])[0]?.t)}${it.date ? ` <span class="muted">· 연도 ${esc(it.date)}</span>` : ""}<span class="raw">기관 기재: ${esc(it.o_period || "—")}</span></dd>
        <dt>크기</dt><dd>${it.h ? `세로 ${esc(it.h)} cm × 가로 ${esc(it.w)} cm` : '<span class="empty">기재 없음</span>'}${evTag(evOf(it,["세로"])[0]?.t)}<span class="raw">기관 기재: ${esc(it.o_size || "—")}</span></dd>
        <dt>소장처</dt><dd>${esc(K[it.keeper][0])}${it.no ? " · " + esc(it.no) : ""}${it.src ? ` · <a class="chip" href="${esc(it.src)}" target="_blank" rel="noopener">원 페이지 ↗</a>` : ""}</dd>
        <dt>국적</dt><dd>한국${evTag(evOf(it,["국적"])[0]?.t)}</dd>
        ${it.use ? `<dt>착용 맥락</dt><dd>${esc(label(it.use))}${evTag(evOf(it,["착용 맥락"])[0]?.t)}</dd>` : ""}
        <dt>이용조건</dt><dd>${esc(label(it.lic))}${evTag(evOf(it,["이용조건"])[0]?.t)}<span class="raw">기관 기재: ${esc(it.o_lic || "—")} · 이 아카이브가 덧붙인 값은 CC BY 4.0</span></dd>
        ${it.note ? `<dt>비고</dt><dd class="muted">${esc(it.note)}</dd>` : ""}
      </dl>
      ${it.ev.length ? `<div class="box"><h5>값마다 근거</h5>
        <table class="orig-t ev-t"><tr><th>항목</th><th>아카이브 값</th><th>근거</th><th>원문 발췌</th></tr>
        ${it.ev.filter(e => e.p !== "이미지").map(e => `<tr><th>${esc(e.p)}</th><td>${esc(e.v)}</td><td>${evTag(e.t).replace('margin-left:8px','')}${e.col ? `<small>${esc(e.col)}</small>` : ""}</td><td class="ex">${esc(e.ex || "—")}${e.note ? `<small>${esc(e.note)}</small>` : ""}</td></tr>`).join("")}</table>
        <p class="note">기관 레코드 ${esc(it.rec)} · 기관 기재 = 소장처가 적은 값 그대로, 도출(규칙) = 기관 기재값에 정해진 규칙을 적용, 아카이브 부여 = 이 아카이브가 붙인 값.</p></div>` :
      `<div class="box"><h5>기관 기록과 아카이브 정리</h5>
        <table class="orig-t"><tr><th></th><th>기관이 적은 값 (원문 그대로)</th><th>아카이브가 정리한 값</th></tr>
        <tr><th>시기</th><td>${esc(it.o_period||"—")}</td><td>${it.period.map(label).join(", ")||"비움"}</td></tr>
        <tr><th>크기</th><td>${esc(it.o_size||"—")}</td><td>${it.h?`세로 ${it.h} · 가로 ${it.w} cm`:"비움"}</td></tr>
        <tr><th>이용조건</th><td>${esc(it.o_lic||"—")}</td><td>${esc(label(it.lic))}</td></tr></table>
        <p class="note">기관 레코드 ${esc(it.rec)} · 기관 기록은 원문 그대로 두고, 공통 칸으로 정리한 값을 따로 둡니다.</p></div>`}
      <div class="tools"><a class="btn" href="data.ttl" download>데이터 TTL</a><a class="btn" href="https://hanboklab.com/ontology/">데이터 구조</a></div>
    </div>
  </div>
  ${same.length ? `<div class="sec" style="padding-top:70px"><div class="sec-h"><h2>같은 문양의 다른 유물</h2><p>${label(it.motif)}</p></div><div class="cards">${same.map(card).join("")}</div></div>` : ""}
  </div>`;
  document.querySelectorAll(".thumbs button").forEach(b => b.onclick = () => { $("#big").innerHTML = media(it, +b.dataset.i); document.querySelectorAll(".thumbs button").forEach(x => x.classList.toggle("on", x === b)); });
  $("#copy").onclick = e => { navigator.clipboard?.writeText(credit); e.target.textContent = "복사했습니다"; };
}

/* ── 문양 */
function motifIndex(){
  setNav("motif");
  const groups = ["naljimseung","giljimseung"].map(g => `<div class="sec-h" style="margin-top:50px"><h2>${label(g)}</h2></div><div class="tiles" style="flex-wrap:wrap">${desc(g).filter(id => id!==g && I.some(it => motifOf(it).includes(id))).map(id => { const n = I.filter(it => motifOf(it).includes(id)).length; const it = I.find(x => x.motif === id && x.img.length) || I.find(x => motifOf(x).includes(id) && x.img.length); return `<a class="tile" href="#/motif/${id}">${it?media(it):""}<div class="ov"><b>${label(id)}</b><small>${n}점</small></div></a>`; }).join("")}</div>`).join("");
  $("#app").innerHTML = `<div class="page"><div class="crumb"><a href="#/">홈</a> › 문양별 보기</div><div class="kick">Motif</div><h1 style="font-size:36px;letter-spacing:.2em">문양별 보기</h1><p class="muted">흉배의 주문양을 날짐승과 길짐승으로 나누었습니다. 배경 요소(구름·파도·바위·불로초)는 문양으로 연결하지 않습니다.</p>${groups}</div>`;
}
function motif(id){
  setNav("motif");
  const c = C[id]; if (!c || c.s !== "motif") return notfound();
  const list = I.filter(it => motifOf(it).includes(id));
  const it0 = list.find(x => x.img.length);
  const narrower = (kids[id]||[]);
  $("#app").innerHTML = `<div class="page">
  <div class="crumb"><a href="#/">홈</a> › <a href="#/motif">문양별 보기</a>${anc(id).reverse().slice(0,-1).map(p => ` › <a href="#/motif/${p}">${label(p)}</a>`).join("")} › ${label(id)}</div>
  <div class="concept">
    <div class="frame">${it0?media(it0):'<div class="media"><div class="ph"><span>'+(HANJA[id]||"胸")+'</span></div></div>'}</div>
    <div><div class="kick">Motif concept</div><h1>${label(id)}<span>${esc(HANJA[id]||"")}</span></h1>
      <p class="muted" style="margin-top:14px">${esc(c.note||"")}</p>
      <p style="font-size:13px;color:var(--ink-2)">${c.b.length?`상위 <a class="chip" href="#/motif/${c.b[0]}">${label(c.b[0])}</a>`:""}${narrower.length?` 하위 ${narrower.map(k=>`<a class="chip" href="#/motif/${k}">${label(k)}</a>`).join("")}`:""}</p>
      <a class="btn" href="#/search?motif=${id}">검색에서 보기 · 이용조건으로 좁히기</a></div>
    <div><div class="side"><h5>이칭 · 검색어</h5><div class="labels">${c.alt.map(a=>`<span>${esc(a)}</span>`).join("")}</div></div>
      <div class="side"><h5>개념 주소</h5><code style="font-size:11.5px;color:var(--muted)">https://hanboklab.com/concept/${id}</code></div></div>
  </div>
  <div class="restop"><span class="count">${list.length}점</span><span class="muted">하위 문양 포함</span></div>
  <div class="cards">${list.map(card).join("")}</div></div>`;
}

/* ── 문장으로 묻기: 질문 → (Worker·Claude) SPARQL → 브라우저(Oxigraph)에서 실행 → 답변. Worker가 안 되면 개념 사전 방식으로 */
const EX = ["상업적으로 쓸 수 있는 쌍학 흉배 보여줘","19세기 후반 학 흉배","소장처별로 몇 점씩 있어?","가로가 가장 큰 흉배 3점","조선 말기 흉배","1734년 이전 흉배","단국대 흉배의 시기는 어디서 왔어?"];
function parse(q){
  const found = [], f = {};
  const norm = s => s.toLowerCase().replace(/\s+/g, "");
  const Q = norm(q);
  const scan = (scheme, key) => {
    let best = null;
    Object.values(C).filter(c => c.s === scheme).forEach(c => [c.ko, ...c.alt].forEach(w => { const n = norm(w); if (n.length > 1 && Q.includes(n) && (!best || n.length > best.n.length)) best = {c, w, n}; }));
    if (best) { found.push([best.w, scheme, best.c.id]); f[key] = best.c.id; }
  };
  scan("motif", "motif"); scan("period", "period"); scan("license", "lic");
  // 단일 글자 문양(학, 호) 보충
  if (!f.motif) { if (/학/.test(q)) { f.motif = "hak"; found.push(["학","motif","hak"]); } else if (/호랑이|범/.test(q)) { f.motif = "horangi"; found.push(["호랑이","motif","horangi"]); } }
  Object.entries(K).forEach(([k,[ko,en]]) => { const short = ko.replace(" 미술관","").replace("박물관",""); if (Q.includes(norm(ko)) || Q.includes(norm(short)) || (k==="met" && /메트|met/i.test(q)) || (k==="nmk" && /국중박/.test(q))) { f.keeper = k; found.push([ko,"keeper",k]); } });
  const m = q.match(/(가로|세로)\s*(\d+(?:\.\d+)?)\s*(?:cm|센티)?\s*(넘|이상|초과|보다 큰|큰)/);
  if (m) { f.dim = [m[1]==="가로"?"w":"h", +m[2]]; found.push([m[0], "dim", `${m[1]} > ${m[2]}cm`]); }
  return {f, found};
}
function runAsk(q){
  const {f, found} = parse(q);
  let rel = false;
  let res = I.filter(it =>
    (!f.motif || motifOf(it).includes(f.motif)) &&
    (!f.lic || (f.lic==="commercialOk" ? LIC_OK(it.lic) : it.lic===f.lic || (C[it.lic]?.b||[]).includes(f.lic))) &&
    (!f.keeper || it.keeper===f.keeper) &&
    (!f.dim || (+it[f.dim[0]]||0) > f.dim[1]));
  if (f.period) {
    const direct = res.filter(it => periodOf(it).includes(f.period));
    if (direct.length || !C[f.period].rel.length) res = direct;
    else { rel = true; const rs = C[f.period].rel.flatMap(desc); res = res.filter(it => it.period.some(p => rs.includes(p))); }
  }
  const pref = {motif:"crm:P2_has_type", period:"dcterms:temporal", license:"dcterms:license"};
  let sp = `SELECT ?item ?title WHERE {\n  ?item a crm:E22_Human-Made_Object ;\n        dcterms:spatial hanbokc:korea ;\n        dcterms:title ?title .\n`;
  if (f.motif) sp += `  hanbokc:${f.motif} ^skos:broader* ?m .          # “${label(f.motif)}”과 하위 문양\n  ?item crm:P2_has_type ?m .\n`;
  if (f.period) sp += rel ? `  hanbokc:${f.period} skos:related ?r . ?r ^skos:broader* ?p .   # 관련 개념으로 넓힘\n  ?item dcterms:temporal ?p .\n` : `  hanbokc:${f.period} ^skos:broader* ?p .\n  ?item dcterms:temporal ?p .\n`;
  if (f.lic) sp += f.lic==="commercialOk" ? `  ?item dcterms:license/skos:broader hanbokc:commercialOk .   # 상업 이용 가능\n` : `  ?item dcterms:license hanbokc:${f.lic} .\n`;
  if (f.keeper) sp += `  ?item crm:P50_has_current_keeper/rdfs:label "${K[f.keeper][0]}"@ko .\n`;
  if (f.dim) sp += `  ?item schema:${f.dim[0]==="w"?"width":"height"} ?v .\n  FILTER(?v > ${f.dim[1]})\n`;
  sp += `  FILTER(LANG(?title) = "ko")\n}`;
  return {res, found, sp, rel};
}
const ASK_URL = "https://hanbok-ask.lisabelys.workers.dev";
const OX_URL = "https://cdn.jsdelivr.net/npm/oxigraph@0.5.13/web.js";
let STORE = null, lastAsk = null;
async function getStore(){
  if (STORE) return STORE;
  const ox = await import(OX_URL); await ox.default();
  const st = new ox.Store();
  for (const f of ["data.ttl", "concepts.ttl"]) st.load(await (await fetch(f)).text(), {format: "text/turtle"});
  return (STORE = st);
}
async function callAsk(body){
  const r = await fetch(ASK_URL, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body)});
  let j = {}; try { j = await r.json(); } catch(e) {}
  if (!r.ok) throw new Error(j.error || ("중계 서버 오류 " + r.status));
  return j;
}
const OBJ = "https://hanboklab.com/object/", CON = "https://hanboklab.com/concept/";
function termLabel(t){
  if (!t) return "";
  const v = t.value;
  if (t.termType === "NamedNode") {
    if (v.startsWith(CON)) return label(v.slice(CON.length));
    if (v.startsWith(OBJ + "actor-")) return K[v.slice(OBJ.length + 6)]?.[0] || v;
    if (v.startsWith(OBJ)) { const it = I.find(x => x.id === v.slice(OBJ.length)); return it ? it.ko : v.slice(OBJ.length); }
    return v;
  }
  return v;
}
function runSparql(sp){
  const res = STORE.query(sp);
  if (!Array.isArray(res)) throw new Error("SELECT 질의가 아닙니다");
  const vars = res.length ? [...res[0].keys()] : (sp.match(/SELECT\s+(DISTINCT\s+)?([\s\S]*?)\s+WHERE/i)?.[2].match(/\?\w+/g) || []).map(v => v.slice(1));
  return {vars, rows: res};
}
function itemsOf(rows){
  const ids = []; rows.forEach(m => m.forEach(t => { if (t.termType === "NamedNode" && /^https:\/\/hanboklab\.com\/object\/hb\d+$/.test(t.value)) { const id = t.value.slice(OBJ.length); if (!ids.includes(id)) ids.push(id); } }));
  return ids.map(id => I.find(x => x.id === id)).filter(Boolean);
}
async function askLLM(q, step){
  await getStore(); step("질문을 SPARQL로 바꾸는 중");
  let j = await callAsk({mode: "sparql", question: q});
  if (!j.sparql) return {none: j.note || "질문에서 흉배 조건을 찾지 못했습니다."};
  let sp = j.sparql, out = null, tries = [], zeroChecked = false, fixed = 0;
  for (let k = 0; k < 4; k++) {
    try { step("지식그래프에서 찾는 중"); out = runSparql(sp); }
    catch (e) {
      tries.push({sparql: sp, error: String(e.message || e)});
      if (tries.length > 2) throw new Error("SPARQL 실행 오류: " + e.message);
      step("쿼리를 고치는 중"); j = await callAsk({mode: "sparql", question: q, prev_sparql: sp, error: String(e.message || e)});
      if (!j.sparql) return {none: j.note}; sp = j.sparql; fixed++; continue;
    }
    if (!out.rows.length && !zeroChecked) {
      zeroChecked = true; tries.push({sparql: sp, error: "결과 0건"});
      step("0건이라 조건을 다시 검토하는 중");
      j = await callAsk({mode: "sparql", question: q, prev_sparql: sp, error: "실행은 됐지만 결과가 0건이다. 개념 IRI·상하 관계·속성 이름을 다시 확인하고, 해석이 맞으면 같은 쿼리를 그대로 내라."});
      if (j.sparql && j.sparql.trim() !== sp.trim()) { sp = j.sparql; fixed++; continue; }
    }
    break;
  }
  const items = itemsOf(out.rows);
  const rowsL = out.rows.slice(0, 60).map(m => Object.fromEntries(out.vars.map(v => [v, termLabel(m.get(v))])));
  // 답변용: 결과 행에 유물 정보(소장처·문양·시기·크기·이용조건)를 붙여 보낸다
  const info = it => ({"명칭": it.ko, "소장처": K[it.keeper][0], "문양": it.motif ? label(it.motif) : "판독 전", "시기": it.period.map(label).join(", ") || "미상",
    ...(it.date ? {"연도": it.date} : {}), ...(it.h ? {"크기": `세로 ${it.h} × 가로 ${it.w} cm`} : {}), "이용조건": label(it.lic)});
  const rowsA = out.rows.slice(0, 60).map((m, i) => { const o = {...rowsL[i]}; m.forEach(t => { if (t.termType === "NamedNode" && t.value.startsWith(OBJ + "hb")) { const it = I.find(x => x.id === t.value.slice(OBJ.length)); if (it) Object.assign(o, info(it)); } }); return o; });
  step("답변을 쓰는 중");
  let answer = "";
  try { answer = (await callAsk({mode: "answer", question: q, sparql: sp, rows: rowsA, total: out.rows.length, items: I.length})).answer || "(답변 문장이 비어 왔습니다) 아래 결과를 확인하세요."; } catch(e) { answer = "(답변 문장을 만들지 못했습니다: " + (e.message || e) + ") 아래 결과를 확인하세요."; }
  return {sp, out, items, rowsL, answer, tries, fixed};
}
function ask(params){
  setNav("ask");
  const q = params.get("q") || "";
  const head = `<div class="crumb"><a href="#/">홈</a> › 문장으로 묻기</div>
  <form id="askf"><input value="${esc(q)}" placeholder="상업적으로 쓸 수 있는 쌍학 흉배 보여줘"></form>
  <div class="examples">${EX.map(e => `<span data-q="${esc(e)}">${esc(e)}</span>`).join("")}</div>`;
  const wire = () => {
    $("#askf").onsubmit = e => { e.preventDefault(); location.hash = "#/ask?q=" + encodeURIComponent(e.target.querySelector("input").value); };
    document.querySelectorAll(".examples span").forEach(s => s.onclick = () => location.hash = "#/ask?q=" + encodeURIComponent(s.dataset.q));
  };
  const render = body => { $("#app").innerHTML = `<div class="page ask">${head}${body}</div>`; wire(); };
  if (!q) { render(`<p class="note" style="margin-top:30px">문양·시기·소장처·이용조건·크기·근거를 섞어 자유롭게 물어보세요. 질문은 Claude가 SPARQL로 바꾸고, 이 페이지가 공개 데이터(data.ttl·concepts.ttl)에서 직접 실행합니다.</p>`); return; }
  const show = r => {
    if (r.none) { render(`<div class="zero-box"><h3>질문을 이해하지 못했습니다</h3><p class="muted">${esc(r.none)}</p></div>`); return; }
    const cols = r.out.vars;
    render(`${r.answer ? `<div class="answer">${esc(r.answer)}</div>` : ""}
    <div class="restop" style="margin-top:26px">${r.items.length ? `<span class="count">${r.items.length}점</span>` : ""}<span class="muted">결과 ${r.out.rows.length}행</span></div>
    ${r.items.length ? `<div class="cards">${r.items.map(card).join("")}</div>` : ""}
    ${r.out.rows.length && (!r.items.length || cols.length > 2) ? `<details class="sparql" ${r.items.length?"":"open"}><summary>결과 표</summary><div style="padding:6px 18px 18px;overflow-x:auto"><table class="rows"><tr>${cols.map(c => `<th>${esc(c)}</th>`).join("")}</tr>${r.rowsL.map(row => `<tr>${cols.map(c => `<td>${esc(row[c])}</td>`).join("")}</tr>`).join("")}</table></div></details>` : ""}
    ${!r.out.rows.length ? `<div class="zero-box"><h3>조건에 맞는 흉배가 없습니다</h3><p class="muted">이 시제품은 시기가 기록된 흉배 ${I.length}점만 담고 있습니다. 조건을 줄여 다시 물어보세요.</p></div>` : ""}
    <details class="sparql" open><summary>실행한 SPARQL${r.fixed ? ` · 고쳐 쓴 횟수 ${r.fixed}` : ""}</summary><pre>${esc(r.sp)}</pre></details>
    <p class="note">질문 → Claude가 SPARQL 작성 → 이 페이지가 공개 데이터에서 실행 → 결과만 근거로 답변. 답변 문장은 AI가 쓴 것이니 결과 카드와 근거를 함께 확인하세요.</p>`);
  };
  if (lastAsk && lastAsk.q === q && lastAsk.r) { show(lastAsk.r); return; }
  render(`<div class="status" id="st"><span class="dot"></span><span id="stt">준비 중</span></div>`);
  const step = t => { const el = document.getElementById("stt"); if (el) el.textContent = t; };
  askLLM(q, step).then(r => { lastAsk = {q, r}; if ((location.hash.split("q=")[1] || "") === encodeURIComponent(q) || decodeURIComponent(location.hash.split("q=")[1] || "") === q) show(r); })
  .catch(e => {
    const out = runAsk(q);
    render(`<div class="zero-box" style="padding:18px 0"><p class="muted">AI 변환을 쓰지 못해(${esc(e.message || e)}) 개념 사전으로 조건을 찾았습니다.</p></div>
    <div class="parsed"><span>질문에서 찾은 조건</span>${out.found.length ? out.found.map(([w,s,id]) => `<span><q>${esc(w)}</q> → <b style="font-weight:400">${({motif:"문양", period:"시기", license:"이용조건", keeper:"소장처", dim:"크기"})[s]}: ${esc(s==="keeper"?K[id][0]:s==="dim"?id:label(id))}</b></span>`).join("") : '<span class="empty">아는 단어가 없습니다</span>'}</div>
    <div class="restop"><span class="count">${out.res.length}점</span></div>
    ${out.res.length ? `<div class="cards">${out.res.map(card).join("")}</div>` : ""}
    <details class="sparql"><summary>만들어진 SPARQL</summary><pre>${esc(out.sp)}</pre></details>`);
  });
}
/* ── 소개·데이터 */
function about(){
  setNav("about");
  const by = k => I.filter(i => i.keeper === k).length;
  $("#app").innerHTML = `<div class="page" style="max-width:820px">
  <div class="kick">About</div><h1 style="font-size:34px;letter-spacing:.18em;margin-bottom:26px">범위와 데이터</h1>
  <p>조선 흉배 아카이브는 여러 소장처에 흩어진 흉배 실물을 모아 문양·시기·이용조건 같은 공통 개념으로 잇는 아카이브입니다. 이 페이지는 데이터 구조를 시험하는 <b style="font-weight:500">시제품</b>입니다.</p>
  <div class="box"><h5>이 시제품에 담은 것</h5>
    <p class="muted">여러 소장처의 한국 흉배 실물 중 소장처가 시기를 적어 둔 ${I.length}점을 담았습니다(소장처 ${Object.keys(K).length}곳). ${Object.entries(K).map(([k,[ko]]) => `${ko} ${by(k)}점`).join(", ")}. 단령·초상화 속 흉배와 중국 흉배는 넣지 않았습니다.</p>
    <p class="muted">비상업 연구·교육 목적의 시제품입니다. 이미지와 소장처 기록은 각 소장처의 이용조건을 따르며, 이용조건을 아직 확인하지 못한 ${I.filter(i => i.lic === "licenseUnknown").length}점은 「확인 중」으로 표시했습니다. 이미지는 소장처 주소에서 바로 불러옵니다.</p>
    <p class="muted">문양이 이름에 없는 ${I.filter(i=>!i.motif).length}점은 이미지 판독 전입니다.</p></div>
  <div class="box"><h5>근거</h5>
    <p class="muted">유물 화면의 값마다 근거 유형(기관 기재·도출(규칙)·아카이브 부여·연구자 확인)과 근거가 된 기관 기록의 칸·원문 발췌를 붙였습니다. 데이터에서는 값마다 rdf:Statement로 적혀 있어 SPARQL로도 물을 수 있습니다.</p></div>
  <div class="box"><h5>기록 원칙</h5>
    <p class="muted">기관이 적은 값은 원문 그대로 두고, 공통 칸으로 정리한 값을 따로 둡니다. 시기는 숫자로 바꾸지 않고 시기 개념에 연결만 하며, 기관이 '조선'만 적은 경우는 비워 둡니다. 문양은 주문양 하나만 연결합니다.</p></div>
  <div class="box"><h5>데이터 내려받기</h5>
    <div class="tools" style="margin-top:6px"><a class="btn" href="data.ttl" download>유물 데이터 (TTL)</a><a class="btn" href="data.csv" download>유물 데이터 (CSV)</a><a class="btn" href="concepts.ttl" download>통제어휘 (TTL)</a><a class="btn" href="evidence.csv" download>값별 근거 (CSV)</a><a class="btn" href="https://hanboklab.com/ontology/">기술규칙·어휘설명</a></div>
    <p class="note">데이터는 기술규칙(SHACL) 검사를 통과한 것입니다. 이 아카이브가 덧붙인 값은 CC BY 4.0, 이미지와 소장처 기록은 각 소장처의 이용조건을 따릅니다.</p></div>
  <div class="box"><h5>인용</h5><p class="muted">이윤서, 「조선 흉배 아카이브(시제품)」, https://archive.hanboklab.com/hyungbae/ (CC BY 4.0)</p></div>
  </div>`;
}
function notfound(){ $("#app").innerHTML = `<div class="page"><h1 style="font-size:28px">찾는 페이지가 없습니다</h1><p><a class="btn" href="#/">홈으로</a></p></div>`; }

function route(){
  const h = location.hash.slice(2) || "";
  const [path, qs] = h.split("?"); const params = new URLSearchParams(qs || "");
  const [a, b] = path.split("/");
  window.scrollTo(0, 0);
  if (!a) home(); else if (a === "search") search(params); else if (a === "item") item(b);
  else if (a === "motif") b ? motif(b) : motifIndex(); else if (a === "ask") ask(params); else if (a === "about") about(); else notfound();
}
$("#hsearch").onsubmit = e => { e.preventDefault(); location.hash = "#/search?q=" + encodeURIComponent(e.target.querySelector("input").value); };
window.addEventListener("hashchange", route); route();
</script>
</body>
</html>"""
open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(html.replace("__DATA__", DATA))
import shutil
base = os.path.splitext(data_p)[0]
shutil.copy(base + ".ttl", os.path.join(out, "data.ttl"))
shutil.copy(data_p, os.path.join(out, "data.csv"))
if evs: shutil.copy(ev_p, os.path.join(out, "evidence.csv"))
shutil.copy(next(p for p in (os.path.join(src, "개념.ttl"), os.path.join(cdir, "개념.ttl")) if os.path.exists(p)), os.path.join(out, "concepts.ttl"))
print("ok", out, len(I))

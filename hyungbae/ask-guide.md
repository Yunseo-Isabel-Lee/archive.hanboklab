# 조선 흉배 아카이브 — 데이터 설명 (문장으로 묻기용, 자동 생성)

## 범위
- 한국 흉배 실물 58점, 소장처 14곳. 소장처가 시기를 적어 둔 유물만 실었다. 초상화 속 흉배·단령·중국 보자는 없다.
- 값(문양·시기·크기·이용조건)은 소장처 기록에서 뽑아 정리했고, 값마다 근거 주석이 있다.
- 이용조건: 확인 중 31점, CC0 23점, 공공누리 4유형 3점, 공공누리 1유형 1점

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
dcterms:date 실제 값: 1480, 1508/1572, 1600/1700, 1650, 1700, 1720, 1750, 1780, 1800/1880, 1800/1899, 1850/1900, 1860, 1864/1892, 1870, 1900~

## 소장처 (rdfs:label 한글@ko)
hanboko:actor-k01 = 국립공주박물관
hanboko:actor-nfm = 국립민속박물관 / National Folk Museum of Korea
hanboko:actor-craftmuseum = 서울공예박물관 / Seoul Museum of Craft Art
hanboko:actor-brooklyn = 브루클린 미술관 / Brooklyn Museum
hanboko:actor-incheon = 인천광역시립박물관 / Incheon Metropolitan City Museum
hanboko:actor-lacma = 로스앤젤레스 카운티 미술관 / Los Angeles County Museum of Art
hanboko:actor-ojukheon = 오죽헌시립박물관 / Ojukheon Municipal Museum
hanboko:actor-smh = 서울역사박물관 / Seoul Museum of History
hanboko:actor-cma = 클리블랜드 미술관 / The Cleveland Museum of Art
hanboko:actor-vam = 빅토리아 앤드 앨버트 박물관 / Victoria and Albert Museum
hanboko:actor-ggmuseum = 경기도박물관 / Gyeonggi Provincial Museum
hanboko:actor-met = 메트로폴리탄 미술관 / The Metropolitan Museum of Art
hanboko:actor-k39 = 이＊＊＊
hanboko:actor-dku = 단국대학교 석주선기념박물관 / Dankook University Seok Juseon Memorial Museum

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

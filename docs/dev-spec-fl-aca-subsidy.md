# 개발 기획서 — Florida ACA Subsidy Estimator (pSEO + AdSense)

> **For: Claude Code** · 동반 문서: `claude-design-prompt-fl-aca-subsidy.md` (UI 디자인)
> 영어권(미국) 시장, 한국어 기획·영어 산출물. 코드/주석/UI 카피/스키마는 영어.
> **작업명 "SubsidyScope"** = 플레이스홀더.

---

## 0. 한 줄 정의

플로리다 거주자가 자신의 ACA 마켓플레이스 보험료를 **강화 세액공제(enhanced PTC) 유무로 동시 비교**해 추정하는 독립 정보 사이트. 히어로는 듀얼 레짐 보조금 계산기, 본문은 `메트로×가구×소득밴드` 프로그래매틱 페이지, 수익은 AdSense.

---

## 1. 비협상 제약 (NON-NEGOTIABLES) — 위반 시 빌드 중단

1. **Marketplace API(`marketplace.api.healthcare.gov`)로 대량 데이터를 추출·DB 적재하지 않는다.** CMS 약관상 "전체 데이터셋 추출" 금지. v1 본문 소스는 **Exchange PUF(정적 파일)** 뿐. 실시간 API는 v1.5에서 사용자 입력당 호출로만.
2. **보험 추천·가입 알선·리드 판매 금지.** 정보·계산만. (주별 보험 모집인 라이선스 회피.)
3. **계산기는 stateless·client-side.** 소득·건강·PII를 수집/저장/전송하지 않는다.
4. **정부 비제휴 고지 필수.** 정부/healthcare.gov 사칭·암시 금지(.gov 흉내 도메인·브랜딩 금지).
5. **YMYL 룰:** 모든 계산 출력은 "추정치지 견적 아님 + healthcare.gov에서 확정" 프레이밍 + 레짐·날짜 스탬프. 틀린 것보다 **낡은 것**이 실패모드 — freshness 강제.
6. **PUF 약관 준수:** 출처·한계 명시(disclaimer-user agreement).

---

## 2. Phase 0 — 검증 게이트 (BLOCKING · 빌드 착수 전 필수)

> **이 4개 게이트를 통과/문서화하기 전에는 어떤 코드도 작성하지 말 것.** 각 게이트 검증 결과를 리포트로 정리해 사람 승인을 받은 뒤 Phase 1로 진행한다.

**G0-1. 카운티 → rating area 크로스워크 검증**
- CMS Geographic Rating Areas(주별 정의 파일) 확보. FL이 **county-based**임을 확인(예상: county-based). ZIP3 기반 예외 없는지 확인.
- 산출물: `fl_county_fips → rating_area_id` 매핑 테이블 + 출처·연도.
- 합격 기준: FL 전 카운티가 정확히 1개 rating area에 매핑됨.

**G0-2. SLCSP 계산 검증**
- Rate PUF에서 FL · rating area · 연령별 **2번째로 싼 Silver 플랜(SLCSP)** 추출 로직 작성·검증.
- 외부 기준값(예: KFF/CMS 공개 벤치마크)과 최소 3개 rating area에서 대조.
- 합격 기준: 대조 오차 허용범위 내. SLCSP 산출 재현 가능.

**G0-3. 현행 보조금 레짐 확인 + swap 엔진 설계**
- **빌드 시점의 법정 레짐을 1차 출처로 확인**(enhanced 만료 후 pre-2021 복귀 상태인지, 또는 의회가 연장/절충안 통과시켰는지). enhanced PTC는 2025-12-31 만료, 이후 입법 진행 중 → **반드시 현재 상태 재확인**.
- IRS applicable percentage 표 + HHS FPL 가이드라인을 연도+레짐별로 확보.
- 합격 기준: `subsidy_regimes` 설정으로 pre-2021 / enhanced / (통과 시)compromise를 **재빌드 없이 swap** 가능한 구조 확정.

**G0-4. FL 메디케이드 갭 로직**
- FL은 **메디케이드 미확장** → 100% FPL 미만은 커버리지 갭(메디케이드도 보조금도 없음).
- 합격 기준: 계산엔진이 income < 100% FPL을 **에러가 아닌 1급 결과 상태**(갭 안내)로 처리하는 명세 확정.

(추가 확인) v1 대상 **FL 상위 5개 메트로**를 마켓플레이스 등록 기준으로 확정하고 각 메트로의 대표 rating area를 지정. 메트로가 복수 rating area에 걸치면 대표값 선정 근거 문서화.

---

## 3. 기술 스택

- **Frontend/SSG:** Next.js 15 (App Router), TypeScript. Vercel Pro 배포.
- **DB/ORM:** Turso (libSQL) + Drizzle ORM. (정적 PUF 데이터 적재 — Marketplace API 적재 아님.)
- **빌드:** pnpm. GitHub Actions + Vercel Cron(연 1회 PUF 재적재 + 레짐 config 핫스왑 트리거).
- **콘텐츠 생성:** Gemini 2.5 Flash/Flash-Lite (스포크·기사 초안). 사람 리뷰 큐 필수.
- **계산기:** client-side JS(보간), 빌드 시 정적 밴드 페이지 사전계산과 동일 로직 공유.

---

## 4. 데이터 아키텍처 (3-layer)

**Layer 1 (raw, redistributable) — Exchange PUF 적재**
- Rate PUF(연령·흡연·rating area·가족티어 보험료), Plan Attributes PUF(metal, MOOP, 공제, HSA), Benefits & Cost Sharing PUF(CSR variant).
- 대상: FFE/SBE-FP 주(= FL 포함). SBM 주(CA/NY 등) 범위 밖.

**Layer 2 (derived, moat) — 빌드 시 계산**
- rating area·연령별 **SLCSP**, 연령 커브, 메탈티어 최저값, 전년 대비 보험료 변화.

**Layer 3 (interactive) — 계산기**
- 듀얼 레짐 net premium. v1.5에서 Marketplace API로 "실제 플랜" 레이어 추가.

### Drizzle 스키마(초안 — Phase 1에서 확정)
```
rating_areas(rating_area_id PK, state, county_fips[], source_year)
plans(plan_id PK, plan_year, issuer, metal_level, rating_area_id, csr_variant)
plan_rates(plan_id, rating_area_id, age, tobacco, individual_rate, plan_year)
slcsp(rating_area_id, age, plan_year, slcsp_premium)            -- derived
fpl_guidelines(year, household_size, fpl_amount)
subsidy_regimes(regime_id, plan_year, applicable_pct_table JSON,
                fpl_cap, effective_as_of, label, is_current)    -- swappable
content_pages(slug PK, type, params JSON, status, last_reviewed, regime_as_of)
review_queue(slug, draft_ref, reviewer, status, notes)
```

---

## 5. 계산 엔진 (핵심)

레짐 파라미터화. 빌드(정적 밴드)와 클라이언트(정밀 보간)가 **동일 함수**를 쓴다.

```
입력: ages[], household_size, annual_income, rating_area_id, tobacco
1) fpl_pct = annual_income / fpl_guidelines(year, household_size)
2) IF fpl_pct < 100% AND state=FL(미확장): return COVERAGE_GAP 상태  // G0-4
3) benchmark = Σ SLCSP(rating_area, age_i)  // 가족 합산 규칙·age curve 적용
4) for each regime in {current, enhanced}:
     applicable_pct = lookup(regime.applicable_pct_table, fpl_pct)
     IF regime=pre-2021 AND fpl_pct >= 400%: aptc = 0   // 절벽
     ELSE: expected_contribution = annual_income * applicable_pct / 12
           aptc = max(0, benchmark - expected_contribution)
     net_premium = max(0, benchmark - aptc)
5) IF fpl_pct < 250%: surface CSR(silver) 안내
출력: { with_enhanced: {...}, current_law: {...}, difference, slcsp, notes }
```
엣지: ≥400% FPL(현행법 무보조금), 가족 3자녀 초과 미산입 룰, 흡연 할증, age curve. 모두 명시적 처리 또는 "범위 밖" 선언.

---

## 6. 페이지 아키텍처 / 라우팅

- **필러:** `/florida-aca-subsidy-calculator` — 듀얼 레짐 히어로.
- **메트로 허브:** `/aca-subsidy/florida/[metro]`
- **스포크(pSEO 본체):** `/aca-subsidy/florida/[metro]/[household]/[income-band]`
- **뉴스/가이드:** `/aca/[topic]`
- **신뢰:** `/methodology`, `/about` (편집기준·리뷰어).

**v1 스코프 캡 (≈180 스포크):** 5 메트로 × 6 가구 아키타입 × 6 FPL 밴드.
- 가구: single / couple / single+1child / family-of-3 / family-of-4 / older-couple(55–64)
- FPL 밴드: 100 / 150 / 200 / 250 / 300 / 400% (보조금 변곡점)
- 정적 페이지 = 밴드 대표값, 정밀 숫자는 클라이언트 보간. **양산(전 카운티/전 소득) 금지 — v2.**

**Dedup:** 페이지별 결과 figure·YoY 델타·CSR/갭 노트가 파라미터로 유의미하게 달라져야 발행. 코사인 dedup + per-cell 최소 임계.

---

## 7. 콘텐츠 파이프라인

- 스포크 직답 블록·context 단락·FAQ를 Gemini로 초안 → **사람 리뷰 큐(YMYL 필수)** → 발행.
- 직답 블록은 self-contained 1–2문장(두 레짐 figure 포함) — AI 인용 타깃.
- 뉴스 레이어(정책상태·프리미엄쇼크·OEP 일정·메탈티어·CSR·subsidy cliff)가 볼륨 엔진. 출처 인라인 인용(패러프레이즈, 15단어 미만).

---

## 8. SEO / GEO / AEO

- 스키마: FAQPage, HowTo(계산기), Dataset(파생 데이터), Article. 시각 구조가 스키마에 1:1 매핑.
- `llms.txt`, `sitemap.xml`(lastmod 정확), IndexNow 핑.
- 메타: 한국이 아니라 영어 타이틀/디스크립션. 직답 우선.

---

## 9. 신뢰 / EEAT / 컴플라이언스

- 전역 비제휴 배너(header/footer): "Independent. Not affiliated with the U.S. government or HealthCare.gov."
- 출처행(CMS·IRS 링크) + Published/Last updated/Data plan-year·regime-as-of 스탬프.
- **리뷰어 자격 블록**(면허 보험전문가/보건정책 리뷰어 — 정확성 감수만, 개별 조언 금지). → 영입 가정.
- 면책(footer): estimate only, not insurance/tax/legal advice.
- 계산기 stateless 안내: "Your numbers stay in your browser."
- PUF attribution 페이지.

---

## 10. 수익화 (AdSense)

- 광고는 **도구 밖** 정의된 슬롯만(결과 아래 / 기사 중·하단 / 데스크탑 사이드바). 결과·CTA 흉내 금지, "Advertisement" 라벨, CLS 0.
- **순서: 신뢰스택 + 콘텐츠 베이스 완성 → 그 다음 AdSense 신청.** 빈 계산기로 신청 금지.

---

## 11. 발행 전략

- **7일 dry run(noindex)** → 웨이브 램프 → 인덱싱. (Scaled Content Abuse 회피.)
- 연 1회 PUF 재적재(차년도 플랜 게시 시점, ~11월). 레짐 config는 의회 변동 시 **핫스왑**(전면 재빌드 X).

---

## 12. 로드맵

- **v1:** PUF 정적 + 공개 IRS/FPL 표 + 듀얼 레짐 client 계산. FL 5메트로 ≈180 스포크 + 뉴스 레이어 + 신뢰스택. AdSense 신청.
- **v1.5:** Marketplace API로 "실제 플랜·약/의사 커버리지" 레이어(사용자 입력당 호출, 60일 키 로테이션·rate limit 운영).
- **v2:** 전 카운티/세분 소득 확장, 추가 FFE 주(TX/GA/NC), 양산.

---

## 13. v1 Definition of Done

- [ ] Phase 0 G0-1~G0-4 검증 리포트 승인 완료
- [ ] PUF 적재 + SLCSP 파생 테이블 생성, 외부 기준 대조 통과
- [ ] 듀얼 레짐 계산엔진(빌드+클라이언트 동일 로직), 갭/≥400%/CSR 상태 처리
- [ ] 필러 + 메트로 허브 + ≈180 스포크 + 뉴스 시드 + methodology/about 렌더
- [ ] 디자인 프롬프트 시스템 구현(접근성 WCAG AA, 색맹 안전, 모바일 우선)
- [ ] 신뢰 컴포넌트·고지·스키마·llms.txt·sitemap
- [ ] 7일 dry run noindex 가동

---

## 14. 사람 승인 게이트 (자동 판단 금지)

1. Phase 0 검증 리포트 → 승인 후 빌드 착수
2. 현행 보조금 레짐 확정값(틀리면 전 사이트 오류)
3. 스포크 YMYL 콘텐츠 리뷰 큐 통과
4. AdSense 신청 시점(신뢰스택·콘텐츠 베이스 충족 여부)
5. v1.5 Marketplace API 도입 결정

---

## 15. 미결/확인 필요

- 브랜드명·도메인 확정(.gov 흉내 금지, KIPRIS/도메인 가용성 별도 확인 불요 — 영어권).
- FL 상위 5 메트로 최종 선정(G0 등록 데이터 기준).
- 리뷰어 영입 진행(돌봄지기 패턴).

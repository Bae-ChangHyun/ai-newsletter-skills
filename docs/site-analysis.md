# 참고 사이트 분석 및 기능 요구사항 정리

> 분석일: 2026-04-07
> 목적: AI 트렌드 뉴스 큐레이션 플랫폼 구축을 위한 벤치마킹

---

## 목차

1. [개별 사이트 분석](#1-개별-사이트-분석)
   - [1.1 Velopers (velopers.kr)](#11-velopers-veloperskr)
   - [1.2 DevDay (devday.kr)](#12-devday-devdaykr)
   - [1.3 NewCodes (newcodes.net)](#13-newcodes-newcodesnet)
   - [1.4 AI Trends (aitrends.kr)](#14-ai-trends-aitrendskr)
2. [교차 비교 분석](#2-교차-비교-분석)
3. [우리 서비스에 차용할 요소](#3-우리-서비스에-차용할-요소)
4. [기능 요구사항 정리](#4-기능-요구사항-정리)

---

## 1. 개별 사이트 분석

### 1.1 Velopers (velopers.kr)

**서비스 성격**: 한국 기업 기술 블로그 큐레이션 포털

#### UI/UX 패턴

| 항목 | 세부 내용 |
|------|----------|
| **레이아웃** | 수평 네비게이션 바 + 카드 기반 그리드/리스트 레이아웃 |
| **네비게이션** | 홈, 모든 블로그, 모든 태그, 소개, 인기 게시글 |
| **카드 디자인** | 썸네일(선택) + 제목 + 2줄 요약 + 회사 로고/블로그명 + 날짜 + 조회수 + 태그 배열 |
| **페이지네이션** | 숫자 기반 ("< 1 2 3 4 5 >"), 총 528 페이지 |
| **색상 테마** | 흰색 배경, 블루톤 강조색, 기업 로고로 색상 다양성 확보 |
| **다크모드** | 미지원 |
| **반응형** | 모바일 친화적 간결 네비게이션 |

#### 핵심 기능

| 기능 | 구현 여부 | 상세 |
|------|----------|------|
| **뉴스 피드** | O | "오늘 새로운 게시글 N개가 올라왔는데, 아직 N개를 안 보셨어요" 형태 신규 콘텐츠 알림 |
| **카테고리** | O | All, Frontend, Backend, AI, DevOps, Architecture, Else (6개) |
| **검색** | O | 텍스트 검색 + 검색 초기화 버튼 |
| **필터링** | O | 블로그명 + 태그 + 카테고리 조합 필터링. URL 파라미터 기반 (page, category, query, blogs, tags) |
| **태그** | O | 3,000+ 태그, count 기반 중요도 정렬 (자동화 572개, AWS 500개, cloud 406개 등) |
| **인기 지표** | O | 조회수(viewCnt) 표시, 주간 인기 게시글 섹션 |
| **북마크/공유** | X | 미지원 |
| **뉴스레터** | X | 미지원 |
| **댓글** | X | 미지원 (큐레이션 중심) |
| **RSS** | O | RSS 피드 제공 |

#### 사용자 시스템

- 로그인/회원가입 없음 (익명 사용자 중심)
- "원하는 블로그가 없어요" 피드백 기능 (Notion 기반)
- Google Analytics 추적

#### 컨텐츠 구조

- **목록**: `[썸네일] 제목 / 2줄 요약 / [회사로고] 블로그명 + 날짜 + 조회수 / [태그배열]`
- **상세 URL**: `/post/{id}` 형태
- **요약**: AI 또는 수동 작성된 2줄 한국어 요약 (`twoLineSummary`)
- **원본 링크**: 기업 블로그 `baseUrl` 필드로 관리
- **소스 표시**: 기업 로고 아이콘 + 블로그명 텍스트

#### 기술적 특징

- **프레임워크**: SvelteKit (CSR 기반)
- **데이터 구조**: `{ posts, totalPages, techBlogs, allTags, searchParams }`
- **이미지 CDN**: CloudFront, Sanity.io
- **추적**: Google Analytics (G-JHCWNJ506V)

---

### 1.2 DevDay (devday.kr)

**서비스 성격**: 개발자 뉴스 큐레이션 서비스 ("개발자 뉴스를 매일매일")

#### UI/UX 패턴

| 항목 | 세부 내용 |
|------|----------|
| **레이아웃** | 고정 상단 네비게이션 + 카드 기반 피드 (추천순/최신순 전환) |
| **네비게이션** | 홈, 피드 설정, Chrome 익스텐션 프로모션 |
| **카드 디자인** | 소스 로고 + 소스명 + AI 생성 제목 + 대형 썸네일 이미지 |
| **색상 테마** | 기본 다크 모드 (`class="dark"`), 라이트/다크 전환 지원 |
| **다크모드** | O (기본값 다크, `prefers-color-scheme` 미디어쿼리 + 수동 전환) |
| **반응형** | 모바일 우선 디자인, viewport 메타 포함 |

#### 핵심 기능

| 기능 | 구현 여부 | 상세 |
|------|----------|------|
| **뉴스 피드** | O | 추천순/최신순 전환, 대형 썸네일 카드 형태 |
| **피드 설정** | O | 사용자별 피드 소스 커스텀 가능 |
| **카테고리** | O | 기사별 레벨(난이도), 유형(Architecture 등), 태그, Space(Frontend/Backend) 분류 |
| **검색** | O | `/search?level=N&type=X&tag=Y` 파라미터 기반 검색 |
| **태그** | O | 기술 태그 (Next.js, FastAPI, JavaScript, Python 등) |
| **AI 요약** | O | 기사 상세 페이지에 핵심 포인트 4-5개 불릿 요약 + 섹션별 상세 분석 |
| **원문 링크** | O | "원문 읽기" 버튼으로 원본 기업 블로그 연결 |
| **난이도 표시** | O | 중급/고급 등 레벨 배지 |
| **관련 추천** | O | "관련 추천 글" 섹션 (6개) |
| **댓글** | O | 기사별 댓글 기능 ("댓글 0", "첫 번째 댓글을 남겨보세요!") |
| **공간(Space)** | O | Frontend, Backend 등 공간별 분류 |
| **Chrome 익스텐션** | O | 새 탭에서 뉴스 피드 확인 가능한 브라우저 확장 |

#### 사용자 시스템

- 로그인 기능 존재 (OAuth 추정, 상세 미확인)
- 피드 설정으로 개인화된 뉴스 소스 관리
- 댓글 작성을 위한 인증 필요

#### 컨텐츠 구조

- **목록**: `[소스로고] 소스명 / AI 생성 한국어 제목 / 대형 썸네일`
- **상세 URL**: `/article/{slug}` (SEO 친화적 슬러그)
- **상세 페이지 구성**:
  1. AI 요약 (핵심 포인트 불릿)
  2. 섹션별 상세 분석 (아키텍처, 활용법, 장단점 등)
  3. 원문 썸네일 이미지
  4. "원문 읽기" 버튼
  5. 메타 태그 (난이도, 유형, 기술태그, Space)
  6. 관련 추천 글 (6개)
  7. 댓글 영역
- **소스 표시**: 정적 CDN 파비콘 (static.devday.kr/favicons/) + 한국어 소스명

#### 기술적 특징

- **프레임워크**: Next.js App Router (SSR + CSR 하이브리드)
- **보안**: CSP nonce 기반 스크립트 관리
- **분석**: Google Analytics (G-B3YE2LQG82), Microsoft Clarity
- **성능**: Partytown으로 3rd party 스크립트 Web Worker 격리, 이미지 CDN (static.devday.kr, wsrv.nl)
- **SEO**: OG 태그, Twitter Card, Google/Naver 사이트 인증, PWA manifest
- **광고**: Google AdSense
- **meta**: `keywords="데브데이,개발,뉴스,기술,프로그래밍,DevDay,개발자,IT,채용,기술블로그"`

---

### 1.3 NewCodes (newcodes.net)

**서비스 성격**: 기업 기술 블로그 + 유튜브 애그리게이터

#### UI/UX 패턴

| 항목 | 세부 내용 |
|------|----------|
| **레이아웃** | 좌측 로고 + 중앙 메뉴 + 우측 인증 메뉴, 이중 네비게이션 (데스크톱/모바일) |
| **네비게이션** | 홈, 블로그, 유튜브, 구독 기업, 좋아요, 피드백 |
| **카드 디자인** | 기업 로고 + 제목 + 썸네일 이미지, 좌우 슬라이드 캐러셀 |
| **색상 테마** | 초록색 (#22c55e, #16a34a) 메인, 흰색 배경, 라이트 그린 (#f0fdf4) |
| **다크모드** | X (라이트 전용) |
| **반응형** | O (768px, 576px 브레이크포인트, 모바일 드로어 메뉴) |

#### 핵심 기능

| 기능 | 구현 여부 | 상세 |
|------|----------|------|
| **뉴스 피드** | O | "이번 주 인기글" (순위 + 좋아요), "최신 기술 블로그", "Hacker News 인기글" |
| **유튜브 영상** | O | "최신 기업 영상" 별도 섹션 |
| **카테고리** | - | 기업별 분류가 주요 (네이버, 카카오, 토스, 우아한형제들 등) |
| **테마 큐레이션** | O | 수동 큐레이션 테마 ("AI 시대에서 개발자로 살아남기", "RAG" 등) |
| **검색** | O | Schema.org SearchAction, `/articles?keyword={term}` |
| **좋아요** | O | `/liked-articles` 경로, localStorage로 NEW 배지 상태 관리 |
| **구독 기업** | O | `/corporations` 기업별 구독 페이지 |
| **피드백** | O | 이름 + 이메일 + 유형 + 내용 수집 모달 |
| **댓글** | X | 미지원 |

#### 사용자 시스템

- **인증**: 쿠키 기반 세션 (`/api/user-info`, credentials: include)
- **역할**: 관리자(isAdmin) 구분, 관리자 메뉴(기업/글/테마 관리)
- **로그인 UI**: 로그인 전 "로그인" 버튼, 로그인 후 닉네임 + 드롭다운
- **마이페이지**: `/auth/profile`

#### 컨텐츠 구조

- **목록**: `[기업로고] 기업명 / [썸네일] / 글 제목 / 날짜 + 좋아요수`
- **상세 URL**: `/articles/{id}-{slug}` 형태
- **요약**: 목록에서는 제목만 (본문 미리보기 없음)
- **원본 링크**: 클릭 시 원본 기업 블로그로 이동
- **날짜 형식**: "2026-04-01 11:17" (YYYY-MM-DD HH:MM)
- **소스 표시**: CDN 기반 로고 + 기업명

#### 기술적 특징

- **프레임워크**: 바닐라 JavaScript + Bootstrap 클래스 (서버 사이드 렌더링 추정)
- **API**: REST (`/api/user-info`, `/api/auth/logout`, `/api/feedback`)
- **SEO**: Schema.org WebSite + SearchAction
- **추적**: Google Analytics 4 (G-5BTMF140HV)
- **이미지**: CloudFront CDN (d1g8228yawhpnq.cloudfront.net)

---

### 1.4 AI Trends (aitrends.kr)

**서비스 성격**: AI 뉴스 특화 큐레이션 + AI 분석 플랫폼

#### UI/UX 패턴

| 항목 | 세부 내용 |
|------|----------|
| **레이아웃** | 고정 상단 네비 (118px 모바일/81px 데스크톱) + 최대 6xl 중앙 정렬 + 3단 풋터 |
| **네비게이션** | 피드(/), 트렌딩(/trending), 커뮤니티(/community), 태그(/tags), 로그인 |
| **카드 디자인** | 텍스트 중심 카드 (이미지 없음), AI 생성 한국어 제목 + 소스 + 태그 |
| **색상 테마** | Tailwind CSS 기반, primary-500/400, gray-200/800 |
| **다크모드** | O (localStorage 기반 자동 전환, `prefers-color-scheme` 폴백) |
| **반응형** | 모바일 우선 (px-4 -> sm:px-6 -> md:px-8) |

#### 핵심 기능

| 기능 | 구현 여부 | 상세 |
|------|----------|------|
| **뉴스 피드** | O | 메인 피드(/) + 트렌딩(/trending) |
| **커뮤니티** | O | /community 별도 토론 공간 |
| **카테고리** | O | ai_category (announcement, showcase 등) |
| **태그** | O | entity_tags (Claude, GPT, FAISS 등) + entity_type (llm, library, dev-tool, company) |
| **AI 요약** | O | 매우 정교한 다층 분석: ai_summary_json, key_takeaways, hook_title_ko, practical_advice, background_terms |
| **소스 신뢰도** | O | display_tier (1-3), 소스 카테고리 분류 |
| **중복 감지** | O | duplicate_count 필드 |
| **증거 기반** | O | has_concrete_evidence 플래그 |
| **난이도 표시** | O | 입문/중급/고급 |
| **뉴스레터** | - | 명시적 CTA 없으나 구조 추정 |
| **후원** | O | /about#support |

#### 사용자 시스템

- 로그인 버튼 존재 (OAuth 추정)
- 다크모드 로컬 스토리지 저장
- 운영 정책(/editorial-policy), 개인정보 처리방침(/privacy)

#### 컨텐츠 구조

- **3단계 제목 시스템**: 원문 제목(title) + 한국어 번역(title_ko) + 훅 제목(hook_title_ko)
- **데이터 모델**:
  ```
  {
    id, title, title_ko, hook_title_ko, link, published_at,
    ai_category, content_type (reddit, rss),
    entity_tags, entity_type,
    sources: { name, category, tier, display_tier },
    ai_summary_json, key_takeaways, practical_advice, background_terms,
    summary_status, has_concrete_evidence, duplicate_count
  }
  ```
- **원본 링크**: 각 기사 `link` 필드로 Reddit/뉴스 원본 연결
- **소스**: Reddit, Hacker News, GitHub 등 글로벌 소스

#### 기술적 특징

- **프레임워크**: Next.js App Router (React Server Components + Suspense)
- **스타일**: Tailwind CSS (dark: 프리픽스 다크모드)
- **성능**: 청크 기반 JS 로딩, CSS 사전로딩, CSP nonce
- **SEO**: OG/Twitter 메타, Google/Naver/Microsoft 사이트 인증
- **추적**: Google Analytics (G-9ZTSG6T5LM)

---

## 2. 교차 비교 분석

### 기능 비교 매트릭스

| 기능 | Velopers | DevDay | NewCodes | AI Trends |
|------|----------|--------|----------|-----------|
| **프레임워크** | SvelteKit | Next.js | Vanilla JS + Bootstrap | Next.js |
| **다크모드** | X | O (기본) | X | O |
| **로그인** | X | O | O | O |
| **AI 요약** | 2줄 요약 | 상세 AI 분석 | X | 다층 AI 분석 |
| **댓글** | X | O | X | O (커뮤니티) |
| **카테고리** | 6개 | 난이도+유형+태그+Space | 기업별 | AI 카테고리+엔티티 |
| **검색** | O | O | O | O (태그) |
| **좋아요/북마크** | X | - | O | - |
| **피드 커스텀** | 블로그+태그 | O | 구독 기업 | 소스+태그 |
| **원문 링크** | O | O | O | O |
| **소스 로고** | O (기업) | O (기업) | O (기업) | O (커뮤니티) |
| **난이도 표시** | X | O | X | O |
| **관련 추천** | X | O (6개) | X | - |
| **뉴스레터** | X | - | - | - |
| **RSS** | O | - | - | - |
| **Chrome 익스텐션** | X | O | X | X |
| **유튜브 통합** | X | X | O | X |
| **피드백 수집** | O (Notion) | - | O (모달) | - |
| **테마 큐레이션** | X | X | O (수동) | X |
| **소스 신뢰도** | X | X | X | O (tier) |
| **중복 감지** | X | X | X | O |
| **PWA** | X | O (manifest) | X | X |

### 소스 범위 비교

| 사이트 | 소스 유형 |
|--------|----------|
| **Velopers** | 한국 기업 기술 블로그 (네이버, 카카오, AWS, 무신사, 여기어때 등) |
| **DevDay** | 한국 기업 블로그 + 해커뉴스 + Reddit |
| **NewCodes** | 한국 기업 블로그 + 유튜브 + Hacker News |
| **AI Trends** | Reddit, Hacker News, GitHub, RSS 등 글로벌 AI 소스 |

### UI/UX 스타일 비교

| 사이트 | 카드 스타일 | 정보 밀도 | 시각적 특징 |
|--------|-----------|----------|-----------|
| **Velopers** | 썸네일 + 텍스트 | 높음 (요약+태그+조회수) | 기업 로고 아이콘 강조 |
| **DevDay** | 대형 썸네일 중심 | 중간 (제목+소스) | 비주얼 임팩트, 다크모드 |
| **NewCodes** | 슬라이드 캐러셀 | 낮음 (제목+날짜) | 초록색 그라데이션 |
| **AI Trends** | 텍스트 중심 | 매우 높음 (다층 AI 분석) | 깔끔한 타이포그래피 |

---

## 3. 우리 서비스에 차용할 요소

### 반드시 차용 (Must Have)

| 출처 | 요소 | 이유 |
|------|------|------|
| **AI Trends** | 다층 AI 요약 (key_takeaways, practical_advice, background_terms) | 우리 서비스의 핵심 차별점. AI 요약이 단순 2줄이 아니라 실용적 조언까지 포함 |
| **AI Trends** | 3단계 제목 (원문/번역/훅) | 글로벌 소스 한국어 서비스에 필수 |
| **AI Trends** | 소스 신뢰도 tier 시스템 | 정보 품질 관리 및 사용자 신뢰 구축 |
| **DevDay** | 다크모드 (기본값 다크) | 개발자 타겟 서비스에 필수, localStorage 저장 |
| **DevDay** | AI 기반 기사 요약 상세 페이지 | 원문 읽기 전 핵심 파악 가능 |
| **DevDay** | 피드 설정 (소스 커스텀) | 사용자별 소스 필터링이 우리 서비스 핵심 |
| **Velopers** | 카테고리 필터 + 태그 + 소스 조합 검색 | 정교한 콘텐츠 발견에 필수 |
| **Velopers** | 기업/소스 로고 아이콘 표시 | 시각적 신뢰도 및 빠른 스캔 |

### 강력 권장 (Should Have)

| 출처 | 요소 | 이유 |
|------|------|------|
| **DevDay** | 난이도 표시 (입문/중급/고급) | 사용자 수준별 콘텐츠 접근성 |
| **DevDay** | 관련 추천 글 (6개) | 사용자 체류 시간 증가 |
| **DevDay** | 댓글 기능 | 커뮤니티 활성화 |
| **DevDay** | SEO-friendly 슬러그 URL | 검색 엔진 최적화 |
| **AI Trends** | entity_type 분류 (llm, library, dev-tool, company) | 태그의 의미론적 분류 |
| **AI Trends** | 중복 감지 (duplicate_count) | 같은 뉴스 다른 소스 통합 |
| **NewCodes** | 좋아요/북마크 기능 | 사용자 참여 및 개인화 |
| **NewCodes** | 피드백 수집 모달 | 소스 건의 기능의 기반 |
| **Velopers** | "오늘 새로운 게시글 N개" 알림 | 사용자 재방문 유도 |

### 고려 (Nice to Have)

| 출처 | 요소 | 이유 |
|------|------|------|
| **DevDay** | Chrome 익스텐션 | 사용자 접점 확대 (향후) |
| **NewCodes** | 유튜브 영상 통합 | 콘텐츠 다양성 (향후) |
| **NewCodes** | 테마 큐레이션 (수동) | 에디터 기반 큐레이션 (향후) |
| **Velopers** | RSS 피드 제공 | 오픈 표준 구독 (향후) |
| **AI Trends** | has_concrete_evidence 플래그 | 정보 신뢰성 강화 (향후) |
| **DevDay** | PWA 지원 | 네이티브 앱 경험 (향후) |

---

## 4. 기능 요구사항 정리

### 4.1 콘텐츠 수집 및 관리

| 요구사항 | 우선순위 | 비고 |
|---------|---------|------|
| RSS 14개 피드 자동 수집 | P0 | 기존 ai-newsletter-skills 기반 |
| GitHub Releases 6개 repo 수집 | P0 | 기존 인프라 활용 |
| Reddit 11개 subreddit 수집 | P0 | 기존 인프라 활용 |
| AI 기반 한국어 요약 생성 | P0 | key_takeaways + practical_advice 형태 |
| 3단계 제목 생성 (원문/번역/훅) | P0 | aitrends.kr 차용 |
| 중복 뉴스 감지 및 병합 | P1 | duplicate_count 기반 |
| 소스 신뢰도 tier 관리 | P1 | 1-3 tier 시스템 |
| 난이도 자동 분류 (입문/중급/고급) | P2 | AI 기반 자동 분류 |
| entity_tags 자동 추출 | P1 | 기술/도구/회사 태그 |

### 4.2 사용자 시스템

| 요구사항 | 우선순위 | 비고 |
|---------|---------|------|
| OAuth 로그인 (Google, GitHub) | P0 | DevDay/NewCodes 참고 |
| 소스 필터링 설정 (피드 커스텀) | P0 | 핵심 기능. 로그인 후 원하는 소스만 표시 |
| 다크모드 설정 저장 | P0 | localStorage + 서버 동기화 |
| 북마크/좋아요 | P1 | NewCodes 참고 |
| 소스 건의 기능 | P1 | NewCodes 피드백 모달 차용 |
| 알림 설정 (Telegram) | P1 | 기존 Telegram 인프라 활용 |
| 뉴스레터 구독 관리 | P1 | 이메일 기반 정기 발송 |
| 사용자 프로필/마이페이지 | P2 | 설정, 북마크, 구독 관리 통합 |

### 4.3 프론트엔드 UI

| 요구사항 | 우선순위 | 비고 |
|---------|---------|------|
| 뉴스 피드 (추천순/최신순) | P0 | DevDay 참고 |
| 카드 디자인 (소스 로고 + AI 제목 + 요약 + 태그) | P0 | Velopers + DevDay 하이브리드 |
| 카테고리 필터 (AI, DevOps, Frontend, Backend 등) | P0 | Velopers 참고 |
| 태그 기반 검색/필터링 | P0 | AI Trends 참고 |
| 소스별 필터링 | P0 | DevDay 피드 설정 참고 |
| 다크모드 (기본값 다크) | P0 | DevDay + AI Trends 참고 |
| 반응형 디자인 (모바일 우선) | P0 | 전체 참고 |
| 기사 상세 페이지 (AI 요약 + 원문 링크 + 태그 + 관련 추천) | P0 | DevDay 상세 페이지 구조 차용 |
| 페이지네이션 또는 무한 스크롤 | P1 | Velopers(숫자) vs DevDay(스크롤) 중 택 |
| "오늘 새 글 N개" 알림 배너 | P1 | Velopers 참고 |
| 댓글 기능 | P2 | DevDay 참고 |
| 트렌딩 페이지 | P2 | AI Trends 참고 |

### 4.4 기술 아키텍처 요구사항

| 요구사항 | 우선순위 | 비고 |
|---------|---------|------|
| Next.js App Router (SSR + RSC) | P0 | DevDay + AI Trends 공통 사용, 생태계 성숙도 높음 |
| Tailwind CSS | P0 | AI Trends 참고, 다크모드 지원 용이 |
| SEO 최적화 (OG, Twitter Card, Schema.org) | P0 | DevDay 참고 |
| 이미지 CDN | P1 | CloudFront 또는 wsrv.nl |
| Google Analytics | P1 | 전체 사이트 공통 |
| CSP 보안 정책 | P2 | DevDay 참고 (nonce 기반) |
| PWA 지원 | P3 | DevDay 참고 (manifest) |

### 4.5 우리 서비스만의 차별점

| 차별점 | 상세 |
|--------|------|
| **개인화 소스 필터링** | 4개 사이트 중 DevDay만 피드 설정 가능. 우리는 소스 레벨까지 세밀한 커스텀 |
| **소스 건의 시스템** | 사용자가 직접 소스를 추가할 수는 없지만, 건의 후 관리자 검토를 거쳐 추가 |
| **다층 AI 요약** | AI Trends의 정교한 분석 구조를 차용하되, UI를 더 직관적으로 |
| **Telegram 알림** | 기존 인프라 활용, 관심 키워드 기반 실시간 알림 |
| **뉴스레터** | 개인화된 소스 필터링 기반 정기 이메일 발송 |
| **소스 신뢰도 시각화** | tier 배지로 공식/커뮤니티/개인 소스 구분 명시 |

---

## 부록: 사이트별 URL 구조 참고

| 사이트 | 홈 | 상세 | 검색 | 설정 |
|--------|-----|------|------|------|
| Velopers | `/` | `/post/{id}` | `?page=&category=&query=&blogs=&tags=` | - |
| DevDay | `/` | `/article/{slug}` | `/search?level=&type=&tag=` | `/settings` |
| NewCodes | `/` | `/articles/{id}-{slug}` | `/articles?keyword=` | `/corporations` |
| AI Trends | `/` | `/articles/{id}` | `/tags` | - |

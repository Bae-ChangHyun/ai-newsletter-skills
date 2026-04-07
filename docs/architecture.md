# AI Trends Web - 기술 아키텍처 설계

> 작성일: 2026-04-07
> 기반: 참고 사이트 분석(site-analysis.md) + 기존 수집기 시스템 분석

---

## 1. 기술 스택 선정 및 근거

### 프론트엔드
| 기술 | 선정 근거 |
|------|-----------|
| **Next.js 15 (App Router)** | DevDay, AI Trends 모두 사용. SSR/RSC로 SEO 최적화, API Routes로 별도 백엔드 불필요 |
| **TypeScript** | 타입 안전성, Drizzle ORM과의 End-to-End 타입 공유 |
| **Tailwind CSS v4** | AI Trends가 사용 중. 다크모드 `dark:` 프리픽스, 빠른 프로토타이핑 |
| **shadcn/ui** | 커스터마이징 가능한 컴포넌트, Tailwind 기반, 의존성 최소화 |

### 백엔드 / 데이터
| 기술 | 선정 근거 |
|------|-----------|
| **Next.js Route Handlers + Server Actions** | 프론트엔드와 동일 프로젝트, 배포 단순화 |
| **PostgreSQL (Supabase)** | 관계형 모델링 + JSONB(AI 요약) + 풀텍스트 검색 + Array 타입(태그) |
| **Drizzle ORM** | TypeScript-first, SQL에 가까운 쿼리 빌더, 마이그레이션 내장 |
| **Auth.js v5 (NextAuth)** | OAuth(Google/GitHub) + 이메일 로그인, Next.js 네이티브 지원 |

### 수집 레이어
| 기술 | 선정 근거 |
|------|-----------|
| **기존 Python 수집기 유지** | 7개 플랫폼 수집기가 안정적으로 동작, 재작성 불필요 |
| **Python ingest_to_db.py** | JSONL → PostgreSQL 적재 브릿지 |
| **cron (기존 manage_cron.py)** | 검증된 스케줄링 메커니즘 유지 |

### AI 요약 파이프라인
| 기술 | 선정 근거 |
|------|-----------|
| **Claude API (Anthropic SDK)** | 다층 AI 요약 생성: 한국어 제목 번역, 훅 제목, key_takeaways, practical_advice |
| **비동기 처리** | DB 적재 후 백그라운드에서 AI 요약 생성, 점진적 강화 |

### 인프라 / 배포
| 기술 | 선정 근거 |
|------|-----------|
| **Vercel** (프론트엔드) | Next.js 최적 호스팅, 무료 티어, 자동 배포 |
| **Supabase** (PostgreSQL) | 관리형 PostgreSQL, 무료 티어, Row Level Security, Realtime 가능, Auth 연동 |
| **Docker Compose** (로컬 개발) | 일관된 개발 환경, DB + 앱 통합 실행 |

---

## 2. 전체 시스템 아키텍처 다이어그램

```
┌──────────────────────────────────────────────────────────────────────┐
│                         사용자 브라우저                                 │
│          (Next.js SSR/CSR - 다크모드 기본, 반응형 모바일 우선)            │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │ HTTPS
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       Next.js 15 App Router                          │
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐                 │
│  │ Pages (RSC)  │  │ API Routes  │  │ Server       │                 │
│  │ 피드, 상세,   │  │ /api/v1/*   │  │ Actions      │                 │
│  │ 트렌딩, 검색  │  │ /api/auth/* │  │ (뮤테이션)    │                 │
│  └──────┬──────┘  └──────┬──────┘  └──────┬───────┘                 │
│         └────────────────┴────────────────┘                          │
│                          │                                           │
│                    Drizzle ORM                                       │
└──────────────────────────┼───────────────────────────────────────────┘
                           │ TCP/SSL
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    PostgreSQL (Supabase)                         │
│                                                                      │
│  ┌───────────┐ ┌────────┐ ┌────────────────┐ ┌──────────┐ ┌────────┐│
│  │ articles  │ │ users  │ │ source_        │ │ tags     │ │comments││
│  │ (뉴스+    │ │(OAuth) │ │ categories     │ │(엔티티   │ │(댓글)  ││
│  │ AI요약)   │ │        │ │  → sources     │ │  태그)   │ │        ││
│  └─────┬─────┘ └────────┘ └────────────────┘ └──────────┘ └────────┘│
│        │  + bookmarks, user_source_preferences, notifications, ...   │
└────────┼─────────────────────────────────────────────────────────────┘
         │ INSERT/UPSERT
         │
┌────────┴─────────────────────────────────────────────────────────────┐
│                   수집 + AI 파이프라인                                  │
│                                                                      │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────────┐         │
│  │ run_all.py  │───>│ JSONL 상태   │───>│ ingest_to_db.py  │         │
│  │ (수집기x7)  │    │ 파일 (기존)   │    │ (DB 적재)        │         │
│  └─────────────┘    └──────────────┘    └────────┬─────────┘         │
│                                                   │                   │
│                                          ┌────────▼─────────┐        │
│                                          │ ai_enrich.py     │        │
│                                          │ (Claude API)     │        │
│                                          │ - 한국어 번역     │        │
│                                          │ - 훅 제목 생성    │        │
│                                          │ - 요약/태그/난이도 │        │
│                                          └──────────────────┘        │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                          알림 레이어                                   │
│  ┌──────────────────┐  ┌──────────────────┐                          │
│  │ Telegram Bot      │  │ 이메일 뉴스레터    │                          │
│  │ (기존 send_       │  │ (Resend, 향후)    │                          │
│  │  telegram.py)     │  │                  │                          │
│  └──────────────────┘  └──────────────────┘                          │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 3. DB 스키마 설계

### 핵심 테이블

```sql
-- =========================================================
-- 소스 카테고리 (사이드바 필터 그룹)
-- =========================================================
CREATE TABLE source_categories (
    id            SERIAL PRIMARY KEY,
    slug          VARCHAR(50) UNIQUE NOT NULL,       -- 'corporate-blog', 'community', 'release' 등
    name          VARCHAR(100) NOT NULL,             -- '기업 블로그', '커뮤니티 / 애그리게이터' 등
    display_order SMALLINT NOT NULL DEFAULT 0,       -- 사이드바 표시 순서
    icon          VARCHAR(50),                       -- 아이콘 식별자 (lucide 아이콘명 등)
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 시드 데이터:
-- | slug             | name                      | display_order |
-- |------------------|---------------------------|---------------|
-- | corporate-blog   | 기업 블로그                 | 1             |
-- | indie-blog       | 인기 블로그 / 개인           | 2             |
-- | community        | 커뮤니티 / 애그리게이터       | 3             |
-- | release          | 기술스택 / 릴리즈            | 4             |
-- | kr-community     | 한국 커뮤니티               | 5             |

-- =========================================================
-- 뉴스 소스 (RSS 피드, API, 스크래핑 대상)
-- =========================================================
CREATE TABLE sources (
    id            SERIAL PRIMARY KEY,
    slug          VARCHAR(50) UNIQUE NOT NULL,       -- 'hn', 'reddit', 'openai-blog' 등
    name          VARCHAR(100) NOT NULL,             -- 'Hacker News', 'OpenAI Blog' 등
    type          VARCHAR(20) NOT NULL DEFAULT 'rss',-- 'rss', 'api', 'scrape'
    category_id   INTEGER REFERENCES source_categories(id), -- FK: 카테고리
    display_tier  SMALLINT NOT NULL DEFAULT 2,       -- 1=공식/1차, 2=커뮤니티, 3=개인
    url           TEXT,                              -- 소스 홈 URL
    icon_url      TEXT,                              -- 소스 파비콘/아이콘
    description   TEXT,
    is_active     BOOLEAN NOT NULL DEFAULT true,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_sources_category_id ON sources(category_id);

-- 소스 시드 데이터:
-- | slug              | name               | category         | tier |
-- |-------------------|--------------------|------------------|------|
-- | openai-blog       | OpenAI Blog        | corporate-blog   | 1    |
-- | google-ai-blog    | Google AI Blog     | corporate-blog   | 1    |
-- | huggingface-blog  | HuggingFace Blog   | corporate-blog   | 1    |
-- | meta-engineering  | Meta Engineering   | corporate-blog   | 1    |
-- | ms-research       | MS Research        | corporate-blog   | 1    |
-- | apple-ml          | Apple ML           | corporate-blog   | 1    |
-- | amazon-science    | Amazon Science     | corporate-blog   | 1    |
-- | nvidia-blog       | NVIDIA Blog        | corporate-blog   | 1    |
-- | simon-willison    | Simon Willison     | indie-blog       | 2    |
-- | langchain-blog    | LangChain Blog     | indie-blog       | 2    |
-- | hn                | Hacker News        | community        | 2    |
-- | geeknews          | GeekNews           | community        | 2    |
-- | producthunt       | Product Hunt       | community        | 2    |
-- | tldr              | TLDR AI            | community        | 2    |
-- | reddit            | Reddit             | community        | 2    |
-- | gh-pytorch        | PyTorch Releases   | release          | 1    |
-- | gh-transformers   | Transformers       | release          | 1    |
-- | gh-langchain      | LangChain          | release          | 1    |
-- | gh-ollama         | Ollama             | release          | 1    |
-- | velopers          | Velopers           | kr-community     | 2    |
-- | devday            | DevDay             | kr-community     | 2    |

-- =========================================================
-- 태그 (엔티티 기반, AI Trends의 entity_tags + entity_type 차용)
-- =========================================================
CREATE TABLE tags (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(100) UNIQUE NOT NULL,      -- 'Claude', 'GPT-4', 'React' 등
    slug          VARCHAR(100) UNIQUE NOT NULL,      -- 'claude', 'gpt-4', 'react'
    entity_type   VARCHAR(30),                       -- 'llm', 'library', 'dev-tool', 'company', 'concept'
    article_count INTEGER NOT NULL DEFAULT 0,        -- 역정규화: 빠른 정렬용
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_tags_entity_type ON tags(entity_type);
CREATE INDEX idx_tags_article_count ON tags(article_count DESC);

-- =========================================================
-- 수집된 뉴스 기사 (AI Trends 3단계 제목 + 다층 AI 요약)
-- =========================================================
CREATE TABLE articles (
    id              SERIAL PRIMARY KEY,
    source_id       INTEGER NOT NULL REFERENCES sources(id),

    -- 3단계 제목 시스템 (AI Trends 차용)
    title           VARCHAR(500) NOT NULL,           -- 원문 제목 (영어 등)
    title_ko        VARCHAR(500),                    -- 한국어 번역 제목
    hook_title_ko   VARCHAR(300),                    -- 훅 제목 (클릭 유도, 짧고 임팩트)

    url             TEXT NOT NULL,
    canonical_url   TEXT NOT NULL,                   -- 정규화된 URL (중복 방지)
    description     TEXT,                            -- 원문 요약/설명

    -- 메트릭
    score           INTEGER DEFAULT 0,
    comment_count   INTEGER DEFAULT 0,
    view_count      INTEGER DEFAULT 0,               -- 자체 조회수 (Velopers 참고)
    bookmark_count  INTEGER DEFAULT 0,               -- 역정규화: 인기도 표시용
    duplicate_count INTEGER DEFAULT 0,               -- 중복 감지 카운트 (AI Trends)

    -- 분류
    external_source VARCHAR(50),                     -- 원본 소스 라벨 (예: 'r/LocalLLaMA')
    state           VARCHAR(20) NOT NULL DEFAULT 'ingested',
    difficulty      VARCHAR(10),                     -- 'beginner', 'intermediate', 'advanced' (DevDay 난이도)
    ai_category     VARCHAR(30),                     -- 'announcement', 'tutorial', 'showcase' 등 (AI Trends)
    content_type    VARCHAR(20),                     -- 'reddit', 'rss', 'blog', 'news'

    -- AI 요약 (다층 구조, AI Trends + DevDay 차용)
    ai_summary_json JSONB,                           -- {
                                                     --   "key_takeaways": ["...", "..."],
                                                     --   "practical_advice": ["...", "..."],
                                                     --   "background_terms": {"term": "설명", ...},
                                                     --   "section_analysis": [{"title": "...", "content": "..."}]
                                                     -- }
    summary_status  VARCHAR(20) DEFAULT 'pending',   -- 'pending', 'processing', 'done', 'failed'
    has_concrete_evidence BOOLEAN,                   -- AI Trends: 구체적 증거 유무

    -- 타임스탬프
    published_at    TIMESTAMPTZ,                     -- 원본 게시 시각
    first_seen_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_articles_canonical_url UNIQUE (canonical_url)
);

CREATE INDEX idx_articles_source_id ON articles(source_id);
CREATE INDEX idx_articles_state ON articles(state);
CREATE INDEX idx_articles_published_at ON articles(published_at DESC);
CREATE INDEX idx_articles_created_at ON articles(created_at DESC);
CREATE INDEX idx_articles_score ON articles(score DESC);
CREATE INDEX idx_articles_difficulty ON articles(difficulty);
CREATE INDEX idx_articles_ai_category ON articles(ai_category);
CREATE INDEX idx_articles_summary_status ON articles(summary_status);

-- 풀텍스트 검색 (원문 + 한국어 제목 + 설명)
CREATE INDEX idx_articles_search ON articles
    USING GIN (to_tsvector('simple',
        coalesce(title, '') || ' ' ||
        coalesce(title_ko, '') || ' ' ||
        coalesce(hook_title_ko, '') || ' ' ||
        coalesce(description, '')
    ));

-- =========================================================
-- 기사-태그 연결 (다대다)
-- =========================================================
CREATE TABLE article_tags (
    article_id  INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    tag_id      INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (article_id, tag_id)
);

CREATE INDEX idx_article_tags_tag_id ON article_tags(tag_id);

-- =========================================================
-- 사용자
-- =========================================================
CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(255) UNIQUE,
    name            VARCHAR(100),
    image           TEXT,                            -- 프로필 이미지 URL
    provider        VARCHAR(20),                     -- 'google', 'github', 'email'
    provider_id     VARCHAR(255),
    role            VARCHAR(20) NOT NULL DEFAULT 'user',  -- 'user', 'admin'
    theme           VARCHAR(10) DEFAULT 'dark',      -- 'dark', 'light', 'system' (DevDay: 기본 다크)
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_users_provider UNIQUE (provider, provider_id)
);

-- =========================================================
-- 사용자별 소스 구독 (핵심 개인화 기능)
-- =========================================================
CREATE TABLE user_source_preferences (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    source_id   INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    is_enabled  BOOLEAN NOT NULL DEFAULT true,       -- false면 해당 소스 숨김
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_user_source UNIQUE (user_id, source_id)
);

-- =========================================================
-- 북마크 (NewCodes 좋아요 기능 참고)
-- =========================================================
CREATE TABLE bookmarks (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    article_id  INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_bookmark UNIQUE (user_id, article_id)
);

CREATE INDEX idx_bookmarks_user_id ON bookmarks(user_id);

-- =========================================================
-- 댓글 (DevDay 참고)
-- =========================================================
CREATE TABLE comments (
    id          SERIAL PRIMARY KEY,
    article_id  INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    parent_id   INTEGER REFERENCES comments(id) ON DELETE CASCADE,  -- 대댓글
    content     TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_comments_article_id ON comments(article_id);
CREATE INDEX idx_comments_user_id ON comments(user_id);

-- =========================================================
-- 소스 건의 (NewCodes 피드백 모달 참고)
-- =========================================================
CREATE TABLE source_suggestions (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER REFERENCES users(id) ON DELETE SET NULL,
    name        VARCHAR(200) NOT NULL,
    url         TEXT NOT NULL,
    reason      TEXT,
    status      VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending/approved/rejected
    admin_note  TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =========================================================
-- 알림 설정
-- =========================================================
CREATE TABLE notification_settings (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    channel         VARCHAR(20) NOT NULL,             -- 'telegram', 'email'
    is_enabled      BOOLEAN NOT NULL DEFAULT false,
    config          JSONB DEFAULT '{}',               -- channel별 설정 (chat_id 등)
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_notification UNIQUE (user_id, channel)
);

-- =========================================================
-- Auth.js 필수 테이블 (자동 관리)
-- accounts, sessions, verification_tokens
-- =========================================================
```

### ER 다이어그램 (텍스트)

```
source_categories ──1:N── sources ──1:N── articles ──N:M── tags (via article_tags)
                             │               │
                             │               ├──1:N── comments ──N:1── users
                             │               │
                             │               └──1:N── bookmarks ──N:1── users
                             │
                             └──N:M── user_source_preferences ──N:1── users
                                                                        │
                                                                        ├──1:N── notification_settings
                                                                        └──1:N── source_suggestions
```

---

## 4. API 엔드포인트 설계

### 인증 (Auth.js 내장)
| Method | Path | 설명 |
|--------|------|------|
| GET/POST | `/api/auth/*` | Auth.js 기본 핸들러 (로그인/로그아웃/콜백) |

### 뉴스 기사
| Method | Path | 설명 | 인증 |
|--------|------|------|------|
| GET | `/api/v1/articles` | 뉴스 목록 (페이지네이션, 필터, 정렬) | 선택 |
| GET | `/api/v1/articles/:id` | 뉴스 상세 (AI 요약 포함) | 선택 |
| GET | `/api/v1/articles/search` | 풀텍스트 검색 | 선택 |
| GET | `/api/v1/articles/trending` | 트렌딩 (AI Trends 참고) | 선택 |
| GET | `/api/v1/articles/weekly-top` | 주간 인기 (score+bookmark 기준 top N) | 선택 |
| GET | `/api/v1/articles/:id/related` | 관련 추천 글 (DevDay: 6개) | 선택 |

**쿼리 파라미터 (`/api/v1/articles`):**
- `page` (기본 1), `limit` (기본 20, 최대 50)
- `source` — 소스 slug (예: `hn,reddit`)
- `source_category` — 소스 카테고리 slug (예: `corporate-blog,community`)
- `tag` — 태그 slug (예: `claude,react`)
- `difficulty` — 난이도 (`beginner`, `intermediate`, `advanced`)
- `category` — AI 카테고리 (`announcement`, `tutorial`, `showcase`)
- `sort` — 정렬 (`latest`, `score`, `trending`, `comments`)
- `since` — ISO 날짜 이후 필터
- `q` — 검색어 (풀텍스트)

### 소스
| Method | Path | 설명 | 인증 |
|--------|------|------|------|
| GET | `/api/v1/sources` | 전체 소스 목록 (카테고리별 그룹핑, tier 포함) | 불필요 |
| GET | `/api/v1/sources/:slug` | 소스 상세 + 해당 소스 기사 수 | 불필요 |
| GET | `/api/v1/source-categories` | 소스 카테고리 목록 (사이드바 필터용) | 불필요 |

### 태그
| Method | Path | 설명 | 인증 |
|--------|------|------|------|
| GET | `/api/v1/tags` | 태그 목록 (entity_type별 그룹핑, count 정렬) | 불필요 |
| GET | `/api/v1/tags/:slug` | 태그 상세 + 관련 기사 | 불필요 |

### 사용자 설정 (인증 필수)
| Method | Path | 설명 |
|--------|------|------|
| GET | `/api/v1/me/preferences` | 나의 소스 구독 설정 조회 |
| PUT | `/api/v1/me/preferences` | 소스 구독 설정 변경 |
| GET | `/api/v1/me/bookmarks` | 나의 북마크 목록 |
| POST | `/api/v1/me/bookmarks` | 북마크 추가 |
| DELETE | `/api/v1/me/bookmarks/:articleId` | 북마크 삭제 |
| GET | `/api/v1/me/notifications` | 알림 설정 조회 |
| PUT | `/api/v1/me/notifications` | 알림 설정 변경 |
| PUT | `/api/v1/me/theme` | 테마 설정 (dark/light/system) |

### 댓글
| Method | Path | 설명 | 인증 |
|--------|------|------|------|
| GET | `/api/v1/articles/:id/comments` | 기사 댓글 목록 | 불필요 |
| POST | `/api/v1/articles/:id/comments` | 댓글 작성 | 필수 |
| PUT | `/api/v1/comments/:id` | 댓글 수정 | 필수 (본인) |
| DELETE | `/api/v1/comments/:id` | 댓글 삭제 | 필수 (본인/관리자) |

### 소스 건의
| Method | Path | 설명 | 인증 |
|--------|------|------|------|
| POST | `/api/v1/suggestions` | 새 소스 건의 | 필수 |
| GET | `/api/v1/suggestions` | 건의 목록 | 관리자 |
| PATCH | `/api/v1/suggestions/:id` | 건의 상태 변경 | 관리자 |

### 관리자
| Method | Path | 설명 | 인증 |
|--------|------|------|------|
| GET | `/api/v1/admin/stats` | 대시보드 통계 (수집 현황, 사용자 수, 인기 소스) | 관리자 |
| POST | `/api/v1/admin/collect` | 수동 수집 트리거 | 관리자 |
| POST | `/api/v1/admin/enrich` | AI 요약 일괄 생성 트리거 | 관리자 |

---

## 5. 프론트엔드 컴포넌트 구조

### 디자인 방향: 노션 스타일 미니멀

> 참고 사이트를 **베끼지 않는다**. 노션(Notion)의 미니멀한 인터페이스를 지향.

| 원칙 | 적용 |
|------|------|
| **깔끔한 타이포그래피** | Inter/Pretendard 폰트, 제목은 font-medium (bold 아님), 본문 text-sm |
| **넉넉한 여백** | 섹션 간 py-8~12, 항목 간 py-3~4, 콘텐츠 max-w-3xl 중앙 정렬 |
| **장식 최소화** | 그림자 없음, 보더 최소 (border-b만), 라운드 최소 (rounded-sm) |
| **모노톤 기반** | gray-50~950 팔레트 중심, 포인트 컬러 1개만 (링크/액션용 blue-600) |
| **리스트 뷰 중심** | 카드 그리드가 아닌 **1열 리스트** (노션 데이터베이스 테이블/갤러리 느낌) |
| **정보 밀도 조절** | 행당: 소스아이콘 + 제목 + 태그 + 메타(시간/점수) — 1~2줄로 압축 |
| **인터랙션** | hover:bg-gray-50/dark:hover:bg-gray-800 — 미세한 배경 변화만 |
| **다크모드** | 기본값 다크, 배경 gray-950, 텍스트 gray-100, 보더 gray-800 |

### 페이지 구조 (App Router)

```
app/
├── layout.tsx                    # 루트 레이아웃 (미니멀 헤더, 테마 프로바이더, 세션)
├── page.tsx                      # 홈 뉴스 피드 (리스트 뷰, 추천순/최신순 전환)
├── weekly/
│   └── page.tsx                  # 주간 인기 (score+bookmark 기준 top N)
├── trending/
│   └── page.tsx                  # 트렌딩 뉴스
├── search/
│   └── page.tsx                  # 풀텍스트 검색 결과
├── source/
│   └── [slug]/
│       └── page.tsx              # 소스별 뉴스 목록
├── tags/
│   ├── page.tsx                  # 전체 태그 브라우저
│   └── [slug]/
│       └── page.tsx              # 태그별 뉴스 목록
├── article/
│   └── [id]/
│       └── page.tsx              # 뉴스 상세 (AI 요약 + 관련 추천 + 댓글)
├── auth/
│   └── signin/page.tsx           # 로그인 (Google/GitHub OAuth)
├── settings/
│   ├── page.tsx                  # 사용자 설정 메인
│   ├── sources/page.tsx          # 소스 구독 관리
│   ├── notifications/page.tsx    # 알림 설정
│   └── bookmarks/page.tsx        # 북마크 목록
├── suggest/
│   └── page.tsx                  # 소스 건의 폼
└── admin/
    ├── layout.tsx                # 관리자 레이아웃
    ├── page.tsx                  # 대시보드
    └── suggestions/page.tsx      # 건의 관리
```

### UI 컴포넌트 계층

```
components/
├── layout/
│   ├── Header.tsx                # 미니멀 상단 바: 로고(텍스트) + 네비(피드/주간/트렌딩) + 검색 + 로그인
│   ├── Sidebar.tsx               # 좌측 사이드바: 소스 카테고리 그룹 → 개별 소스 체크 (노션 사이드바 느낌)
│   │                             #   - 기업 블로그 (접기/펼치기)
│   │                             #     - OpenAI Blog, Google AI Blog, ...
│   │                             #   - 인기 블로그 / 개인
│   │                             #     - Simon Willison, LangChain Blog
│   │                             #   - 커뮤니티 / 애그리게이터
│   │                             #     - Hacker News, GeekNews, Reddit, ...
│   │                             #   - 기술스택 / 릴리즈
│   │                             #     - PyTorch, Transformers, Ollama, ...
│   │                             #   - 한국 커뮤니티
│   │                             #     - Velopers, DevDay
│   ├── Footer.tsx                # 최소한의 하단 (정책 링크만)
│   ├── MobileNav.tsx             # 모바일: 하단 탭 바 (피드/주간/검색/설정)
│   └── ThemeToggle.tsx           # 다크/라이트 전환 (아이콘만, 미니멀)
├── article/
│   ├── ArticleRow.tsx            # **리스트 행** (노션 테이블 행 느낌):
│   │                             #   [소스아이콘] 훅제목 · 태그1 태그2 · 3h ago · 42pt
│   │                             #   hover: 배경 미세 변화 + 북마크 아이콘 표시
│   ├── ArticleList.tsx           # 1열 리스트 (border-b 구분, 카드 아님)
│   ├── ArticleDetail.tsx         # 뉴스 상세 (max-w-2xl 중앙 정렬, 여백 많이):
│   │                             #   1. 제목 (원문 + 한국어) + 소스 + 시간
│   │                             #   2. AI 요약 (key_takeaways 불릿)
│   │                             #   3. 섹션별 분석 (접기/펼치기)
│   │                             #   4. 배경 용어 (인라인 팝오버)
│   │                             #   5. 원문 읽기 버튼 (프라이머리)
│   │                             #   6. 태그 (회색 텍스트, 클릭 가능)
│   │                             #   7. 관련 추천 글 (6개, 심플 리스트)
│   │                             #   8. 댓글 영역
│   ├── ArticleMeta.tsx           # 메타 인라인: 소스 · 점수 · 댓글 수 · 시간
│   ├── AiSummary.tsx             # AI 요약 블록 (배경색 미세 구분, 불릿 중심)
│   ├── RelatedArticles.tsx       # 관련 추천 (6개, 제목+소스만 표시)
│   ├── BookmarkButton.tsx        # 북마크 토글 (아이콘만)
│   └── DifficultyBadge.tsx       # 난이도 (텍스트만: "입문" "중급" "고급", 색상 미세 구분)
├── source/
│   ├── SourceIcon.tsx            # 소스 아이콘 (16px, 없으면 이니셜 원형)
│   ├── SourceCategoryGroup.tsx   # 카테고리 그룹 (접기/펼치기 가능)
│   └── SourceToggle.tsx          # 소스 ON/OFF (설정 페이지, 심플 체크박스)
├── tag/
│   ├── TagInline.tsx             # 태그 인라인 텍스트 (#claude, 회색, 호버시 포인트)
│   └── TagList.tsx               # 태그 목록 (가로 나열, 줄바꿈)
├── comment/
│   ├── CommentList.tsx           # 댓글 목록 (대댓글 인덴트)
│   ├── CommentForm.tsx           # 댓글 입력 (미니멀 textarea)
│   └── CommentItem.tsx           # 댓글 항목 (이름 · 시간 / 내용)
├── search/
│   ├── SearchBar.tsx             # Cmd+K 검색 모달 (노션 스타일)
│   └── SearchResults.tsx         # 검색 결과 (리스트 행 재사용)
├── auth/
│   ├── SignInForm.tsx            # OAuth 버튼 (Google, GitHub) — 미니멀
│   └── UserMenu.tsx              # 아바타 클릭 → 드롭다운
├── feed/
│   ├── FeedSortToggle.tsx        # 최신순/추천순/주간 탭 (underline 스타일)
│   ├── NewArticleBanner.tsx      # "새 글 N개" 배너 (상단, 미세한 배경)
│   └── FeedEmptyState.tsx        # 빈 상태
└── common/
    ├── Pagination.tsx            # 숫자 페이지네이션 (미니멀)
    ├── Skeleton.tsx              # 로딩 스켈레톤 (라인 형태)
    ├── EmptyState.tsx            # 빈 상태
    └── TimeAgo.tsx               # "3h ago" 형태
```

### 핵심 UI 패턴 (노션 미니멀 + 참고 사이트 기능 차용)

| 패턴 | 적용 방식 |
|------|-----------|
| **리스트 뷰 기본** | 카드가 아닌 1열 리스트 행. border-b로 구분. 노션 데이터베이스 테이블 느낌 |
| **다크모드 기본값** | gray-950 배경, gray-100 텍스트. localStorage + `prefers-color-scheme` 폴백 |
| **타이포그래피 중심** | 큰 여백, 깔끔한 폰트 (Inter/Pretendard), 장식 최소화 |
| **모노톤 + 포인트 1색** | gray 팔레트 중심, 링크/액션만 blue-600. 소스/태그 색상 없음 |
| **3단계 제목 표시** | 목록: `hook_title_ko`, 상세: 원문 + 번역 모두 |
| **사이드바 카테고리 필터** | 소스 카테고리별 접기/펼치기 그룹, 체크박스로 소스 ON/OFF |
| **주간 인기** | /weekly 페이지, score+bookmark 기준 top N |
| **AI 요약 상세** | 불릿 중심 key_takeaways → 접기/펼치기 섹션 분석 → 인라인 배경 용어 |
| **Cmd+K 검색** | 노션 스타일 검색 모달, 풀텍스트 |
| **미세한 인터랙션** | hover:bg 변화만, 그림자/테두리 없음, 전환 애니메이션 최소 |

---

## 6. 기존 수집기 연동 방안

### 현재 아키텍처 (AS-IS)

```
cron → run_collect_cycle.py → run_all.py → collectors/*.py
                                              ↓
                                     {platform}_seen.jsonl (JSONL 파일)
                                              ↓
                            (Claude/Copilot이 큐레이션 → Telegram 전송)
```

### 목표 아키텍처 (TO-BE)

```
cron → run_collect_cycle.py → run_all.py → collectors/*.py
                                              ↓
                                     {platform}_seen.jsonl (기존 유지, 호환)
                                              ↓
                                     ingest_to_db.py (DB 브릿지)
                                              ↓
                                        PostgreSQL
                                              ↓
                                     ai_enrich.py (AI 요약 생성)
                                              ↓
                                      Next.js 웹 UI + Telegram 알림
```

### 연동 전략: 점진적 마이그레이션

**Phase 1 - 병렬 운영 (MVP)**
1. 기존 JSONL 파이프라인 유지 (Telegram 전송 기능 보존)
2. `ingest_to_db.py` 추가: JSONL → DB UPSERT (`canonical_url` 기준 중복 방지)
3. `ai_enrich.py` 추가: `summary_status='pending'` 기사에 대해 Claude API로 AI 요약 생성
4. cron: 수집 → DB 적재 → AI 요약 순차 실행

**Phase 2 - DB 중심 전환 (안정화 후)**
1. 수집기가 직접 DB에 기록하도록 `base_collector.py` 확장
2. Telegram 전송도 DB 기반으로 전환
3. JSONL은 백업/로그 용도로만 유지

### `ingest_to_db.py` 핵심 흐름

```python
# 1. 각 {platform}_seen.jsonl 읽기 (base_collector.load_seen 활용)
# 2. articles 테이블에 canonical_url 기준 UPSERT
# 3. 새 항목 → state='ingested', summary_status='pending'
# 4. 기존 항목 → score/comment_count 업데이트만
# 5. sources 테이블 매핑 (platform slug → source_id)
```

### `ai_enrich.py` 핵심 흐름

```python
# 1. summary_status='pending' 기사 N개 조회
# 2. Claude API 호출 → 구조화된 JSON 응답:
#    {
#      "title_ko": "한국어 번역",
#      "hook_title_ko": "훅 제목",
#      "difficulty": "intermediate",
#      "ai_category": "tutorial",
#      "entity_tags": ["Claude", "RAG"],
#      "key_takeaways": ["...", "..."],
#      "practical_advice": ["...", "..."],
#      "background_terms": {"RAG": "설명..."},
#      "section_analysis": [{"title": "...", "content": "..."}]
#    }
# 3. articles 업데이트 + tags 테이블에 태그 upsert + article_tags 연결
# 4. summary_status → 'done'
```

### 수집기 설정 통합

기존 `config.json`에 하위 호환으로 추가:
```json
{
  "platforms": ["hn", "reddit", "geeknews", "tldr", "threads", "velopers", "devday"],
  "subreddits": ["Anthropic", "ClaudeAI", "..."],
  "schedule": { "mode": "interval", "expression": "6h" },
  "telegram": { "bot_token": "...", "chat_id": "..." },
  "database": {
    "url": "postgresql://user:pass@host:5432/aitrends"
  },
  "ai": {
    "provider": "anthropic",
    "model": "claude-sonnet-4-6",
    "batch_size": 10,
    "max_daily_calls": 200
  }
}
```

---

## 7. 디렉토리 구조

```
worktree-ai-trends-web/
├── docs/                          # 프로젝트 문서
│   ├── architecture.md            # 본 문서
│   └── site-analysis.md           # 참고 사이트 분석
│
├── web/                           # Next.js 웹 애플리케이션
│   ├── app/                       # App Router 페이지
│   │   ├── layout.tsx             # 루트 레이아웃 (헤더, 테마, 세션)
│   │   ├── page.tsx               # 홈 뉴스 피드
│   │   ├── weekly/page.tsx         # 주간 인기
│   │   ├── trending/page.tsx      # 트렌딩
│   │   ├── search/page.tsx        # 검색
│   │   ├── source/[slug]/page.tsx # 소스별 목록
│   │   ├── tags/
│   │   │   ├── page.tsx           # 태그 브라우저
│   │   │   └── [slug]/page.tsx    # 태그별 목록
│   │   ├── article/[id]/page.tsx  # 뉴스 상세 (AI 요약 + 관련 + 댓글)
│   │   ├── auth/signin/page.tsx   # 로그인
│   │   ├── settings/
│   │   │   ├── page.tsx           # 설정 메인
│   │   │   ├── sources/page.tsx   # 소스 구독 관리
│   │   │   ├── notifications/page.tsx
│   │   │   └── bookmarks/page.tsx
│   │   ├── suggest/page.tsx       # 소스 건의
│   │   ├── admin/                 # 관리자 페이지
│   │   └── api/
│   │       ├── auth/[...nextauth]/route.ts
│   │       └── v1/
│   │           ├── articles/
│   │           │   ├── route.ts                # GET 목록
│   │           │   ├── search/route.ts         # GET 검색
│   │           │   ├── trending/route.ts       # GET 트렌딩
│   │           │   ├── weekly-top/route.ts    # GET 주간 인기
│   │           │   └── [id]/
│   │           │       ├── route.ts            # GET 상세
│   │           │       ├── related/route.ts    # GET 관련 추천
│   │           │       └── comments/route.ts   # GET/POST 댓글
│   │           ├── sources/route.ts
│   │           ├── source-categories/route.ts
│   │           ├── tags/route.ts
│   │           ├── me/
│   │           │   ├── preferences/route.ts
│   │           │   ├── bookmarks/route.ts
│   │           │   ├── notifications/route.ts
│   │           │   └── theme/route.ts
│   │           ├── suggestions/route.ts
│   │           ├── comments/[id]/route.ts
│   │           └── admin/
│   │               ├── stats/route.ts
│   │               ├── collect/route.ts
│   │               └── enrich/route.ts
│   ├── components/                # React 컴포넌트 (5장 참조)
│   │   ├── layout/
│   │   ├── article/
│   │   ├── source/
│   │   ├── tag/
│   │   ├── comment/
│   │   ├── search/
│   │   ├── auth/
│   │   ├── feed/
│   │   └── common/
│   ├── lib/
│   │   ├── db/
│   │   │   ├── schema.ts          # Drizzle 스키마 (3장의 SQL 매핑)
│   │   │   ├── index.ts           # DB 연결
│   │   │   └── migrations/
│   │   ├── auth.ts                # Auth.js v5 설정
│   │   ├── api.ts                 # API 클라이언트 유틸
│   │   └── utils.ts
│   ├── public/
│   │   └── source-icons/          # 소스 파비콘/아이콘
│   ├── drizzle.config.ts
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── package.json
│
├── shared/                        # 기존 공유 리소스 (변경 최소화)
│   └── newsletter/
│       ├── .data/                 # 런타임 데이터 (config.json, JSONL)
│       ├── scripts/
│       │   ├── base_collector.py  # (기존) 수집 베이스 클래스
│       │   ├── run_all.py         # (기존) 수집 오케스트레이터
│       │   ├── run_collect_cycle.py # (기존) 수집 사이클
│       │   ├── send_telegram.py   # (기존) Telegram 전송
│       │   ├── manage_cron.py     # (기존) cron 관리
│       │   ├── ingest_to_db.py    # (신규) JSONL → DB 브릿지
│       │   ├── ai_enrich.py       # (신규) AI 요약 생성 파이프라인
│       │   └── collectors/        # (기존) 7개 플랫폼 수집기
│       │       ├── hn.py
│       │       ├── reddit.py
│       │       ├── geeknews.py
│       │       ├── tldr.py
│       │       ├── threads.py
│       │       ├── velopers.py
│       │       └── devday.py
│       └── prompts/
│
├── scripts/                       # 설치/운영 스크립트 (기존)
├── targets/                       # 배포 타겟 템플릿 (기존)
├── tests/                         # 테스트
│
├── docker-compose.yml             # 로컬 개발 (PostgreSQL + Next.js)
├── .env.example                   # 환경 변수 템플릿
└── README.md
```

---

## 부록 A: 구현 우선순위 (MVP → 확장)

### Phase 1 - MVP (P0)
- Next.js 프로젝트 셋업 + Drizzle + Supabase PostgreSQL
- DB 스키마 생성 (source_categories + sources + articles) + `ingest_to_db.py` 브릿지
- 노션 스타일 미니멀 UI (리스트 뷰, 모노톤, 여백 많이)
- 뉴스 피드 (추천순/최신순) + 사이드바 소스 카테고리 필터
- 뉴스 상세 페이지 (원문 링크)
- 풀텍스트 검색 (Cmd+K)
- 주간 인기 페이지 (score + bookmark 기준)
- 북마크/즐겨찾기 기능
- OAuth 로그인 (Google/GitHub)
- 소스 구독 설정 (카테고리별 ON/OFF)
- 다크모드 (기본값 다크)
- 반응형 디자인

### Phase 2 - AI 강화 (P1)
- `ai_enrich.py` AI 요약 파이프라인
- 3단계 제목 표시
- 태그 시스템 (entity_type 분류)
- 소스 건의 기능
- 트렌딩 페이지
- 알림 설정 (Telegram 연동)

### Phase 3 - 커뮤니티 (P2)
- 댓글 기능
- 난이도 분류 표시
- 관련 추천 글
- 관리자 대시보드
- "오늘 새 글 N개" 배너
- 이메일 뉴스레터

### Phase 4 - 확장 (P3)
- PWA 지원
- Chrome 익스텐션
- RSS 피드 제공
- 유튜브 영상 통합
- 테마 큐레이션 (에디터 기반)

---

## 부록 B: 참고 사이트 벤치마크 요약

| 사이트 | 핵심 차용 요소 |
|--------|--------------|
| **Velopers** | 카드 정보 밀도, 카테고리+태그+소스 조합 필터, 소스 로고, 숫자 페이지네이션, "새 글 N개" 알림 |
| **DevDay** | 다크모드 기본, AI 요약 상세 페이지, 피드 설정, 난이도 배지, 관련 추천 6개, 댓글, SEO 슬러그 URL |
| **NewCodes** | 좋아요/북마크, 피드백 수집 모달 (소스 건의), 사용자 인증 시스템 |
| **AI Trends** | 3단계 제목, 다층 AI 요약 (key_takeaways, practical_advice), 소스 tier, entity_tags, 중복 감지, 트렌딩 |

> 상세 분석: [docs/site-analysis.md](./site-analysis.md)

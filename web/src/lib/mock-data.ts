import type { ArticleListItem } from "@/components/article/ArticleList";

export const mockSourceCategories = [
  {
    name: "기업 블로그",
    slug: "corporate-blog",
    sources: [
      { name: "OpenAI Blog", slug: "openai-blog", iconUrl: null },
      { name: "Google AI Blog", slug: "google-ai-blog", iconUrl: null },
      { name: "HuggingFace Blog", slug: "huggingface-blog", iconUrl: null },
      { name: "Meta Engineering", slug: "meta-engineering", iconUrl: null },
    ],
  },
  {
    name: "인기 블로그 / 개인",
    slug: "indie-blog",
    sources: [
      { name: "Simon Willison", slug: "simon-willison", iconUrl: null },
      { name: "LangChain Blog", slug: "langchain-blog", iconUrl: null },
    ],
  },
  {
    name: "커뮤니티 / 애그리게이터",
    slug: "community",
    sources: [
      { name: "Hacker News", slug: "hn", iconUrl: null },
      { name: "GeekNews", slug: "geeknews", iconUrl: null },
      { name: "Reddit", slug: "reddit", iconUrl: null },
      { name: "Product Hunt", slug: "producthunt", iconUrl: null },
      { name: "TLDR AI", slug: "tldr", iconUrl: null },
    ],
  },
  {
    name: "기술스택 / 릴리즈",
    slug: "release",
    sources: [
      { name: "PyTorch Releases", slug: "gh-pytorch", iconUrl: null },
      { name: "Transformers", slug: "gh-transformers", iconUrl: null },
      { name: "LangChain", slug: "gh-langchain", iconUrl: null },
      { name: "Ollama", slug: "gh-ollama", iconUrl: null },
    ],
  },
  {
    name: "한국 커뮤니티",
    slug: "kr-community",
    sources: [
      { name: "Velopers", slug: "velopers", iconUrl: null },
      { name: "DevDay", slug: "devday", iconUrl: null },
    ],
  },
];

export const mockArticles: ArticleListItem[] = [
  {
    id: 1,
    title:
      "Claude Code is unusable for complex engineering tasks with the Feb updates",
    hookTitleKo: "클로드 코드(Claude Code)의 성능 저하, 사고 과정 축소가 문제?",
    sourceName: "Hacker News",
    score: 872,
    commentCount: 234,
    publishedAt: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
    difficulty: "intermediate",
    tags: [
      { name: "Claude", slug: "claude" },
      { name: "AI Agent", slug: "ai-agent" },
    ],
  },
  {
    id: 2,
    title: "OpenAI announces GPT-5 with enhanced reasoning capabilities",
    hookTitleKo: "OpenAI, 향상된 추론 기능의 GPT-5 발표",
    sourceName: "OpenAI Blog",
    score: 1250,
    commentCount: 567,
    publishedAt: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
    difficulty: "beginner",
    tags: [
      { name: "GPT", slug: "gpt" },
      { name: "OpenAI", slug: "openai" },
    ],
  },
  {
    id: 3,
    title:
      "Building Production RAG Applications with LangChain and Pinecone",
    hookTitleKo:
      "LangChain + Pinecone으로 프로덕션 RAG 애플리케이션 구축하기",
    sourceName: "LangChain Blog",
    score: 345,
    commentCount: 89,
    publishedAt: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(),
    difficulty: "advanced",
    tags: [
      { name: "RAG", slug: "rag" },
      { name: "LangChain", slug: "langchain" },
      { name: "Pinecone", slug: "pinecone" },
    ],
  },
  {
    id: 4,
    title: "무신사, AI 기반 테스트 자동화로 커버리지 8배 향상",
    hookTitleKo:
      "AI와 함께 iOS 테스트 커버리지 8배 향상! 무신사 개발팀의 비결",
    sourceName: "DevDay",
    score: 156,
    commentCount: 23,
    publishedAt: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
    tags: [
      { name: "Testing", slug: "testing" },
      { name: "AI", slug: "ai" },
    ],
  },
  {
    id: 5,
    title: "PyTorch 2.6 Released with improved compile performance",
    hookTitleKo: "PyTorch 2.6 출시 — 컴파일 성능 대폭 개선",
    sourceName: "PyTorch Releases",
    score: 423,
    commentCount: 67,
    publishedAt: new Date(Date.now() - 16 * 60 * 60 * 1000).toISOString(),
    difficulty: "intermediate",
    tags: [
      { name: "PyTorch", slug: "pytorch" },
      { name: "Release", slug: "release" },
    ],
  },
  {
    id: 6,
    title: "How we reduced LLM inference latency by 60% at scale",
    hookTitleKo: "대규모 LLM 추론 지연시간을 60% 줄인 방법",
    sourceName: "Google AI Blog",
    score: 678,
    commentCount: 145,
    publishedAt: new Date(Date.now() - 20 * 60 * 60 * 1000).toISOString(),
    difficulty: "advanced",
    tags: [
      { name: "LLM", slug: "llm" },
      { name: "Inference", slug: "inference" },
      { name: "Performance", slug: "performance" },
    ],
  },
  {
    id: 7,
    title: "r/LocalLLaMA: Best practices for running Llama 3.2 locally",
    hookTitleKo: "Llama 3.2 로컬 실행 베스트 프랙티스 정리",
    sourceName: "Reddit",
    score: 534,
    commentCount: 198,
    publishedAt: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    difficulty: "intermediate",
    tags: [
      { name: "Llama", slug: "llama" },
      { name: "Local LLM", slug: "local-llm" },
    ],
  },
  {
    id: 8,
    title: "GeekNews Weekly: AI 에이전트 프레임워크 비교 분석",
    hookTitleKo:
      "AI 에이전트 프레임워크 비교: LangGraph vs CrewAI vs AutoGen",
    sourceName: "GeekNews",
    score: 289,
    commentCount: 56,
    publishedAt: new Date(Date.now() - 28 * 60 * 60 * 1000).toISOString(),
    tags: [
      { name: "AI Agent", slug: "ai-agent" },
      { name: "Framework", slug: "framework" },
    ],
  },
  {
    id: 9,
    title: "Ollama 0.6 released: support for Gemma 3, Qwen 3, and QAT quantization",
    hookTitleKo: "Ollama 0.6 출시 — Gemma 3, Qwen 3, QAT 양자화 지원",
    sourceName: "Ollama",
    score: 612,
    commentCount: 134,
    publishedAt: new Date(Date.now() - 32 * 60 * 60 * 1000).toISOString(),
    difficulty: "beginner",
    tags: [
      { name: "Ollama", slug: "ollama" },
      { name: "Release", slug: "release" },
    ],
  },
  {
    id: 10,
    title: "Simon Willison: How I use LLMs as a developer in 2026",
    hookTitleKo: "시몬 윌리슨: 2026년 개발자가 LLM을 활용하는 방법",
    sourceName: "Simon Willison",
    score: 445,
    commentCount: 92,
    publishedAt: new Date(Date.now() - 36 * 60 * 60 * 1000).toISOString(),
    tags: [
      { name: "LLM", slug: "llm" },
      { name: "Developer", slug: "developer" },
    ],
  },
];

export const mockTags = {
  llm: [
    { name: "Claude", slug: "claude", count: 342 },
    { name: "GPT", slug: "gpt", count: 567 },
    { name: "Llama", slug: "llama", count: 234 },
    { name: "Gemini", slug: "gemini", count: 189 },
    { name: "Mistral", slug: "mistral", count: 156 },
  ],
  library: [
    { name: "LangChain", slug: "langchain", count: 456 },
    { name: "PyTorch", slug: "pytorch", count: 389 },
    { name: "Transformers", slug: "transformers", count: 312 },
    { name: "Ollama", slug: "ollama", count: 198 },
    { name: "vLLM", slug: "vllm", count: 134 },
  ],
  concept: [
    { name: "RAG", slug: "rag", count: 278 },
    { name: "AI Agent", slug: "ai-agent", count: 345 },
    { name: "Fine-tuning", slug: "fine-tuning", count: 167 },
    { name: "Inference", slug: "inference", count: 145 },
    { name: "MCP", slug: "mcp", count: 123 },
  ],
  "dev-tool": [
    { name: "VS Code", slug: "vs-code", count: 234 },
    { name: "Docker", slug: "docker", count: 189 },
    { name: "Cursor", slug: "cursor", count: 156 },
    { name: "Claude Code", slug: "claude-code", count: 98 },
  ],
  company: [
    { name: "OpenAI", slug: "openai", count: 534 },
    { name: "Anthropic", slug: "anthropic", count: 412 },
    { name: "Google", slug: "google", count: 389 },
    { name: "Meta", slug: "meta", count: 267 },
  ],
};

export const mockArticleDetail = {
  id: 1,
  title: "Next.js App Router에서 프록시 레이어를 둔 이유",
  titleKo:
    "Next.js App Router에서 API 프록시 레이어를 구축하여 CORS, 보안 문제를 해결",
  hookTitleKo:
    "Next.js App Router에서 API 프록시 레이어를 구축하여 CORS, 보안 문제를 해결",
  url: "https://story.pxd.co.kr/1889",
  sourceName: "피엑스디",
  sourceIconUrl: null,
  score: 156,
  commentCount: 12,
  publishedAt: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
  difficulty: "intermediate" as const,
  aiSummary: {
    key_takeaways: [
      "Next.js App Router의 API Routes를 활용하여 CORS 문제와 환경 변수 보안 문제를 해결",
      "httpOnly 쿠키를 사용하여 인증 토큰(JWT)을 안전하게 관리, XSS 공격 방지",
      "catch-all 라우트([...path]/route.ts)로 모든 API 요청을 중앙 처리",
      "프록시 레이어 도입으로 클라이언트 코드 단순화 및 OAuth 콜백 흐름 개선",
    ],
    practical_advice: [
      "프론트엔드와 백엔드가 분리된 프로젝트에서 CORS 이슈가 반복된다면 API 프록시 패턴을 고려하세요",
      "인증 토큰은 localStorage 대신 httpOnly 쿠키에 저장하여 XSS 공격으로부터 보호하세요",
    ],
    background_terms: {
      CORS: "Cross-Origin Resource Sharing. 브라우저가 다른 출처의 리소스 요청을 제한하는 보안 메커니즘",
      "httpOnly Cookie":
        "JavaScript에서 접근할 수 없는 쿠키로, XSS 공격으로부터 안전한 토큰 저장소",
      "Catch-all Route":
        "Next.js의 [...path] 패턴으로 동적 경로의 모든 세그먼트를 캡처하는 라우팅 방식",
    },
    section_analysis: [
      {
        title: "API 프록시 레이어의 핵심 아키텍처",
        content:
          "catch-all 라우트를 통해 모든 API 요청을 중앙에서 처리하고, Access-Control-Allow-Origin 설정을 일괄 관리하여 CORS 설정을 간소화합니다.",
      },
      {
        title: "httpOnly 쿠키를 활용한 토큰 관리",
        content:
          "Google OAuth 인증 후 발급된 JWT 토큰을 httpOnly 쿠키에 저장하고, 프록시 레이어에서 자동으로 Authorization 헤더에 추가합니다.",
      },
    ],
  },
  tags: [
    { name: "Next.js", slug: "nextjs" },
    { name: "FastAPI", slug: "fastapi" },
    { name: "JavaScript", slug: "javascript" },
    { name: "Frontend", slug: "frontend" },
  ],
  relatedArticles: [
    {
      id: 2,
      title: "AI 코딩 에이전트용 샌드박스",
      hookTitleKo: "0.7초 만에 VM 생성! 코딩 에이전트용 샌드박스 등장",
      sourceName: "Hacker News",
      sourceIconUrl: null,
    },
    {
      id: 3,
      title: "Stack Overflow 디자인 변경",
      hookTitleKo: "Stack Overflow, 디자인 변경에 대한 개발자들의 생각은?",
      sourceName: "Reddit",
      sourceIconUrl: null,
    },
    {
      id: 4,
      title: "AI 코딩 하네스 분석",
      hookTitleKo:
        "AI 코딩, 이제 하네스 시대: OpenCode와 OMO로 개발 생산성 UP!",
      sourceName: "요즘IT",
      sourceIconUrl: null,
    },
    {
      id: 5,
      title: "OSINT 대시보드 공개",
      hookTitleKo:
        "전 세계 정보를 한눈에: 실시간 OSINT 대시보드 Shadowbroker 공개!",
      sourceName: "Hacker News",
      sourceIconUrl: null,
    },
    {
      id: 6,
      title: "AI 시대 개발자 생존 전략",
      hookTitleKo: "AI 시대, 개발자 생존 전략은?",
      sourceName: "Reddit",
      sourceIconUrl: null,
    },
    {
      id: 7,
      title: "Iceberg와 Flink로 데이터 파이프라인 12배 향상",
      hookTitleKo: "Iceberg와 Flink로 데이터 파이프라인 성능 12배 향상!",
      sourceName: "라인",
      sourceIconUrl: null,
    },
  ],
};

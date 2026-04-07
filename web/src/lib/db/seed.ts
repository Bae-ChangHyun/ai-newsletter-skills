import { db } from "./index";
import { sourceCategories, sources } from "./schema";

const SEED_CATEGORIES = [
  { slug: "corporate-blog", name: "기업 블로그", displayOrder: 1, icon: "building" },
  { slug: "indie-blog", name: "인기 블로그 / 개인", displayOrder: 2, icon: "user" },
  { slug: "community", name: "커뮤니티 / 애그리게이터", displayOrder: 3, icon: "users" },
  { slug: "release", name: "기술스택 / 릴리즈", displayOrder: 4, icon: "package" },
  { slug: "kr-community", name: "한국 커뮤니티", displayOrder: 5, icon: "globe" },
];

const SEED_SOURCES = [
  // Corporate blogs
  { slug: "openai-blog", name: "OpenAI Blog", type: "rss", categorySlug: "corporate-blog", displayTier: 1, url: "https://openai.com/blog" },
  { slug: "google-ai-blog", name: "Google AI Blog", type: "rss", categorySlug: "corporate-blog", displayTier: 1, url: "https://blog.google/technology/ai/" },
  { slug: "huggingface-blog", name: "HuggingFace Blog", type: "rss", categorySlug: "corporate-blog", displayTier: 1, url: "https://huggingface.co/blog" },
  { slug: "meta-engineering", name: "Meta Engineering", type: "rss", categorySlug: "corporate-blog", displayTier: 1, url: "https://engineering.fb.com" },
  { slug: "ms-research", name: "MS Research", type: "rss", categorySlug: "corporate-blog", displayTier: 1, url: "https://www.microsoft.com/en-us/research/blog/" },
  { slug: "apple-ml", name: "Apple ML", type: "rss", categorySlug: "corporate-blog", displayTier: 1, url: "https://machinelearning.apple.com" },
  { slug: "amazon-science", name: "Amazon Science", type: "rss", categorySlug: "corporate-blog", displayTier: 1, url: "https://www.amazon.science" },
  { slug: "nvidia-blog", name: "NVIDIA Blog", type: "rss", categorySlug: "corporate-blog", displayTier: 1, url: "https://blogs.nvidia.com" },
  // Indie blogs
  { slug: "simon-willison", name: "Simon Willison", type: "rss", categorySlug: "indie-blog", displayTier: 2, url: "https://simonwillison.net" },
  { slug: "langchain-blog", name: "LangChain Blog", type: "rss", categorySlug: "indie-blog", displayTier: 2, url: "https://blog.langchain.dev" },
  // Community / Aggregators
  { slug: "hn", name: "Hacker News", type: "api", categorySlug: "community", displayTier: 2, url: "https://news.ycombinator.com" },
  { slug: "geeknews", name: "GeekNews", type: "scrape", categorySlug: "community", displayTier: 2, url: "https://news.hada.io" },
  { slug: "producthunt", name: "Product Hunt", type: "api", categorySlug: "community", displayTier: 2, url: "https://www.producthunt.com" },
  { slug: "tldr", name: "TLDR AI", type: "rss", categorySlug: "community", displayTier: 2, url: "https://tldr.tech/ai" },
  { slug: "reddit", name: "Reddit", type: "api", categorySlug: "community", displayTier: 2, url: "https://www.reddit.com" },
  // Release tracking
  { slug: "gh-pytorch", name: "PyTorch Releases", type: "api", categorySlug: "release", displayTier: 1, url: "https://github.com/pytorch/pytorch" },
  { slug: "gh-transformers", name: "Transformers", type: "api", categorySlug: "release", displayTier: 1, url: "https://github.com/huggingface/transformers" },
  { slug: "gh-langchain", name: "LangChain", type: "api", categorySlug: "release", displayTier: 1, url: "https://github.com/langchain-ai/langchain" },
  { slug: "gh-ollama", name: "Ollama", type: "api", categorySlug: "release", displayTier: 1, url: "https://github.com/ollama/ollama" },
  // Korean community
  { slug: "velopers", name: "Velopers", type: "rss", categorySlug: "kr-community", displayTier: 2, url: "https://www.velopers.kr" },
  { slug: "devday", name: "DevDay", type: "scrape", categorySlug: "kr-community", displayTier: 2, url: "https://devday.kr" },
];

async function seed() {
  console.log("Seeding source categories...");

  for (const cat of SEED_CATEGORIES) {
    await db
      .insert(sourceCategories)
      .values(cat)
      .onConflictDoNothing();
  }

  console.log("Seeding sources...");

  // Get category ID mapping
  const cats = await db.select().from(sourceCategories);
  const catMap = new Map(cats.map((c) => [c.slug, c.id]));

  for (const src of SEED_SOURCES) {
    const categoryId = catMap.get(src.categorySlug);
    await db
      .insert(sources)
      .values({
        slug: src.slug,
        name: src.name,
        type: src.type,
        categoryId: categoryId ?? null,
        displayTier: src.displayTier,
        url: src.url,
      })
      .onConflictDoNothing();
  }

  console.log(`Seeded ${SEED_CATEGORIES.length} categories, ${SEED_SOURCES.length} sources.`);
}

seed()
  .then(() => process.exit(0))
  .catch((err) => {
    console.error("Seed error:", err);
    process.exit(1);
  });

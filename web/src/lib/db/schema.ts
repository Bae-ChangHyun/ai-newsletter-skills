import {
  pgTable,
  serial,
  varchar,
  text,
  integer,
  boolean,
  smallint,
  timestamp,
  jsonb,
  uniqueIndex,
  index,
  primaryKey,
} from "drizzle-orm/pg-core";
import { relations } from "drizzle-orm";

// =========================================================
// Source Categories
// =========================================================
export const sourceCategories = pgTable("source_categories", {
  id: serial("id").primaryKey(),
  slug: varchar("slug", { length: 50 }).unique().notNull(),
  name: varchar("name", { length: 100 }).notNull(),
  displayOrder: smallint("display_order").notNull().default(0),
  icon: varchar("icon", { length: 50 }),
  createdAt: timestamp("created_at", { withTimezone: true })
    .notNull()
    .defaultNow(),
});

export const sourceCategoriesRelations = relations(
  sourceCategories,
  ({ many }) => ({
    sources: many(sources),
  })
);

// =========================================================
// Sources
// =========================================================
export const sources = pgTable(
  "sources",
  {
    id: serial("id").primaryKey(),
    slug: varchar("slug", { length: 50 }).unique().notNull(),
    name: varchar("name", { length: 100 }).notNull(),
    type: varchar("type", { length: 20 }).notNull().default("rss"),
    categoryId: integer("category_id").references(() => sourceCategories.id),
    displayTier: smallint("display_tier").notNull().default(2),
    url: text("url"),
    iconUrl: text("icon_url"),
    description: text("description"),
    isActive: boolean("is_active").notNull().default(true),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (table) => [index("idx_sources_category_id").on(table.categoryId)]
);

export const sourcesRelations = relations(sources, ({ one, many }) => ({
  category: one(sourceCategories, {
    fields: [sources.categoryId],
    references: [sourceCategories.id],
  }),
  articles: many(articles),
}));

// =========================================================
// Tags
// =========================================================
export const tags = pgTable(
  "tags",
  {
    id: serial("id").primaryKey(),
    name: varchar("name", { length: 100 }).unique().notNull(),
    slug: varchar("slug", { length: 100 }).unique().notNull(),
    entityType: varchar("entity_type", { length: 30 }),
    articleCount: integer("article_count").notNull().default(0),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (table) => [
    index("idx_tags_entity_type").on(table.entityType),
    index("idx_tags_article_count").on(table.articleCount),
  ]
);

export const tagsRelations = relations(tags, ({ many }) => ({
  articleTags: many(articleTags),
}));

// =========================================================
// Articles
// =========================================================
export const articles = pgTable(
  "articles",
  {
    id: serial("id").primaryKey(),
    sourceId: integer("source_id")
      .notNull()
      .references(() => sources.id),

    // 3-tier title system
    title: varchar("title", { length: 500 }).notNull(),
    titleKo: varchar("title_ko", { length: 500 }),
    hookTitleKo: varchar("hook_title_ko", { length: 300 }),

    url: text("url").notNull(),
    canonicalUrl: text("canonical_url").notNull().unique(),
    description: text("description"),

    // Metrics
    score: integer("score").default(0),
    commentCount: integer("comment_count").default(0),
    viewCount: integer("view_count").default(0),
    bookmarkCount: integer("bookmark_count").default(0),
    duplicateCount: integer("duplicate_count").default(0),

    // Classification
    externalSource: varchar("external_source", { length: 50 }),
    state: varchar("state", { length: 20 }).notNull().default("ingested"),
    difficulty: varchar("difficulty", { length: 10 }),
    aiCategory: varchar("ai_category", { length: 30 }),
    contentType: varchar("content_type", { length: 20 }),

    // AI Summary (multi-layer)
    aiSummaryJson: jsonb("ai_summary_json"),
    summaryStatus: varchar("summary_status", { length: 20 }).default(
      "pending"
    ),
    hasConcreteEvidence: boolean("has_concrete_evidence"),

    // Timestamps
    publishedAt: timestamp("published_at", { withTimezone: true }),
    firstSeenAt: timestamp("first_seen_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (table) => [
    index("idx_articles_source_id").on(table.sourceId),
    index("idx_articles_state").on(table.state),
    index("idx_articles_published_at").on(table.publishedAt),
    index("idx_articles_created_at").on(table.createdAt),
    index("idx_articles_score").on(table.score),
    index("idx_articles_difficulty").on(table.difficulty),
    index("idx_articles_ai_category").on(table.aiCategory),
    index("idx_articles_summary_status").on(table.summaryStatus),
  ]
);

export const articlesRelations = relations(articles, ({ one, many }) => ({
  source: one(sources, {
    fields: [articles.sourceId],
    references: [sources.id],
  }),
  articleTags: many(articleTags),
  bookmarks: many(bookmarks),
  comments: many(comments),
}));

// =========================================================
// Article-Tag junction
// =========================================================
export const articleTags = pgTable(
  "article_tags",
  {
    articleId: integer("article_id")
      .notNull()
      .references(() => articles.id, { onDelete: "cascade" }),
    tagId: integer("tag_id")
      .notNull()
      .references(() => tags.id, { onDelete: "cascade" }),
  },
  (table) => [
    primaryKey({ columns: [table.articleId, table.tagId] }),
    index("idx_article_tags_tag_id").on(table.tagId),
  ]
);

export const articleTagsRelations = relations(articleTags, ({ one }) => ({
  article: one(articles, {
    fields: [articleTags.articleId],
    references: [articles.id],
  }),
  tag: one(tags, {
    fields: [articleTags.tagId],
    references: [tags.id],
  }),
}));

// =========================================================
// Users
// =========================================================
export const users = pgTable(
  "users",
  {
    id: serial("id").primaryKey(),
    email: varchar("email", { length: 255 }).unique(),
    name: varchar("name", { length: 100 }),
    image: text("image"),
    provider: varchar("provider", { length: 20 }),
    providerId: varchar("provider_id", { length: 255 }),
    role: varchar("role", { length: 20 }).notNull().default("user"),
    theme: varchar("theme", { length: 10 }).default("dark"),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (table) => [
    uniqueIndex("uq_users_provider").on(table.provider, table.providerId),
  ]
);

export const usersRelations = relations(users, ({ many }) => ({
  sourcePreferences: many(userSourcePreferences),
  bookmarks: many(bookmarks),
  comments: many(comments),
  notificationSettings: many(notificationSettings),
}));

// =========================================================
// User Source Preferences
// =========================================================
export const userSourcePreferences = pgTable(
  "user_source_preferences",
  {
    id: serial("id").primaryKey(),
    userId: integer("user_id")
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    sourceId: integer("source_id")
      .notNull()
      .references(() => sources.id, { onDelete: "cascade" }),
    isEnabled: boolean("is_enabled").notNull().default(true),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (table) => [
    uniqueIndex("uq_user_source").on(table.userId, table.sourceId),
  ]
);

export const userSourcePreferencesRelations = relations(
  userSourcePreferences,
  ({ one }) => ({
    user: one(users, {
      fields: [userSourcePreferences.userId],
      references: [users.id],
    }),
    source: one(sources, {
      fields: [userSourcePreferences.sourceId],
      references: [sources.id],
    }),
  })
);

// =========================================================
// Bookmarks
// =========================================================
export const bookmarks = pgTable(
  "bookmarks",
  {
    id: serial("id").primaryKey(),
    userId: integer("user_id")
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    articleId: integer("article_id")
      .notNull()
      .references(() => articles.id, { onDelete: "cascade" }),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (table) => [
    uniqueIndex("uq_bookmark").on(table.userId, table.articleId),
    index("idx_bookmarks_user_id").on(table.userId),
  ]
);

export const bookmarksRelations = relations(bookmarks, ({ one }) => ({
  user: one(users, {
    fields: [bookmarks.userId],
    references: [users.id],
  }),
  article: one(articles, {
    fields: [bookmarks.articleId],
    references: [articles.id],
  }),
}));

// =========================================================
// Comments
// =========================================================
export const comments = pgTable(
  "comments",
  {
    id: serial("id").primaryKey(),
    articleId: integer("article_id")
      .notNull()
      .references(() => articles.id, { onDelete: "cascade" }),
    userId: integer("user_id")
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    parentId: integer("parent_id"),
    content: text("content").notNull(),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (table) => [
    index("idx_comments_article_id").on(table.articleId),
    index("idx_comments_user_id").on(table.userId),
  ]
);

export const commentsRelations = relations(comments, ({ one }) => ({
  article: one(articles, {
    fields: [comments.articleId],
    references: [articles.id],
  }),
  user: one(users, {
    fields: [comments.userId],
    references: [users.id],
  }),
}));

// =========================================================
// Source Suggestions
// =========================================================
export const sourceSuggestions = pgTable("source_suggestions", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").references(() => users.id, {
    onDelete: "set null",
  }),
  name: varchar("name", { length: 200 }).notNull(),
  url: text("url").notNull(),
  reason: text("reason"),
  status: varchar("status", { length: 20 }).notNull().default("pending"),
  adminNote: text("admin_note"),
  createdAt: timestamp("created_at", { withTimezone: true })
    .notNull()
    .defaultNow(),
});

// =========================================================
// Notification Settings
// =========================================================
export const notificationSettings = pgTable(
  "notification_settings",
  {
    id: serial("id").primaryKey(),
    userId: integer("user_id")
      .notNull()
      .references(() => users.id, { onDelete: "cascade" }),
    channel: varchar("channel", { length: 20 }).notNull(),
    isEnabled: boolean("is_enabled").notNull().default(false),
    config: jsonb("config").default({}),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (table) => [
    uniqueIndex("uq_notification").on(table.userId, table.channel),
  ]
);

export const notificationSettingsRelations = relations(
  notificationSettings,
  ({ one }) => ({
    user: one(users, {
      fields: [notificationSettings.userId],
      references: [users.id],
    }),
  })
);

// =========================================================
// Type exports
// =========================================================
export type SourceCategory = typeof sourceCategories.$inferSelect;
export type Source = typeof sources.$inferSelect;
export type Tag = typeof tags.$inferSelect;
export type Article = typeof articles.$inferSelect;
export type User = typeof users.$inferSelect;
export type Bookmark = typeof bookmarks.$inferSelect;
export type Comment = typeof comments.$inferSelect;
export type SourceSuggestion = typeof sourceSuggestions.$inferSelect;
export type NotificationSetting = typeof notificationSettings.$inferSelect;

export type AiSummary = {
  key_takeaways: string[];
  practical_advice: string[];
  background_terms: Record<string, string>;
  section_analysis: { title: string; content: string }[];
};

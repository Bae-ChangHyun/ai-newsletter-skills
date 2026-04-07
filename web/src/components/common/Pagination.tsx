"use client";

import Link from "next/link";
import { cn } from "@/lib/utils";

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  baseUrl: string;
}

export function Pagination({
  currentPage,
  totalPages,
  baseUrl,
}: PaginationProps) {
  if (totalPages <= 1) return null;

  const pages: (number | "...")[] = [];
  const delta = 2;

  for (let i = 1; i <= totalPages; i++) {
    if (
      i === 1 ||
      i === totalPages ||
      (i >= currentPage - delta && i <= currentPage + delta)
    ) {
      pages.push(i);
    } else if (pages[pages.length - 1] !== "...") {
      pages.push("...");
    }
  }

  const separator = baseUrl.includes("?") ? "&" : "?";

  return (
    <nav className="flex items-center justify-center gap-1 py-6">
      {pages.map((page, i) =>
        page === "..." ? (
          <span
            key={`ellipsis-${i}`}
            className="px-2 text-sm text-muted-foreground"
          >
            ...
          </span>
        ) : (
          <Link
            key={page}
            href={`${baseUrl}${separator}page=${page}`}
            className={cn(
              "px-2.5 py-1 text-sm rounded-sm transition-colors",
              page === currentPage
                ? "text-foreground bg-muted"
                : "text-muted-foreground hover:text-foreground hover:bg-muted"
            )}
          >
            {page}
          </Link>
        )
      )}
    </nav>
  );
}

import Link from "next/link";
import { cn } from "@/lib/utils";

interface TagInlineProps {
  name: string;
  slug: string;
  className?: string;
}

export function TagInline({ name, slug, className }: TagInlineProps) {
  return (
    <Link
      href={`/tags/${slug}`}
      className={cn(
        "text-xs text-muted-foreground hover:text-accent transition-colors",
        className
      )}
    >
      #{name}
    </Link>
  );
}

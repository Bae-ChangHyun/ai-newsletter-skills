import { cn } from "@/lib/utils";

interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className }: SkeletonProps) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-sm bg-muted",
        className
      )}
    />
  );
}

export function ArticleRowSkeleton() {
  return (
    <div className="py-3 border-b border-border space-y-2">
      <Skeleton className="h-4 w-3/4" />
      <div className="flex items-center gap-2">
        <Skeleton className="w-4 h-4 rounded-sm" />
        <Skeleton className="h-3 w-20" />
        <Skeleton className="h-3 w-12" />
        <Skeleton className="h-3 w-16" />
      </div>
    </div>
  );
}

export function ArticleListSkeleton({ count = 10 }: { count?: number }) {
  return (
    <div>
      {Array.from({ length: count }).map((_, i) => (
        <ArticleRowSkeleton key={i} />
      ))}
    </div>
  );
}

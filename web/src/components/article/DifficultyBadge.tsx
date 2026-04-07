import { cn } from "@/lib/utils";

const labels: Record<string, string> = {
  beginner: "입문",
  intermediate: "중급",
  advanced: "고급",
};

const colors: Record<string, string> = {
  beginner: "text-green-600 dark:text-green-400",
  intermediate: "text-yellow-600 dark:text-yellow-400",
  advanced: "text-red-600 dark:text-red-400",
};

interface DifficultyBadgeProps {
  difficulty: string;
  className?: string;
}

export function DifficultyBadge({ difficulty, className }: DifficultyBadgeProps) {
  return (
    <span
      className={cn(
        "text-xs font-medium",
        colors[difficulty] || "text-muted-foreground",
        className
      )}
    >
      {labels[difficulty] || difficulty}
    </span>
  );
}

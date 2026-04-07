import { cn } from "@/lib/utils";

interface SourceIconProps {
  name: string;
  iconUrl?: string | null;
  size?: "sm" | "md";
  className?: string;
}

export function SourceIcon({
  name,
  iconUrl,
  size = "sm",
  className,
}: SourceIconProps) {
  const sizeClass = size === "sm" ? "w-4 h-4" : "w-5 h-5";
  const textSize = size === "sm" ? "text-[9px]" : "text-[11px]";

  if (iconUrl) {
    return (
      <img
        src={iconUrl}
        alt=""
        className={cn(sizeClass, "rounded-sm", className)}
      />
    );
  }

  return (
    <span
      className={cn(
        sizeClass,
        "rounded-sm bg-muted flex items-center justify-center font-medium",
        textSize,
        className
      )}
    >
      {name[0]?.toUpperCase()}
    </span>
  );
}

"use client";

import { Moon, Sun, Monitor } from "lucide-react";
import { useTheme } from "./ThemeProvider";
import { cn } from "@/lib/utils";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  const next = theme === "dark" ? "light" : theme === "light" ? "system" : "dark";
  const Icon = theme === "dark" ? Moon : theme === "light" ? Sun : Monitor;

  return (
    <button
      onClick={() => setTheme(next)}
      className={cn(
        "p-1.5 rounded-sm text-muted-foreground",
        "hover:text-foreground hover:bg-muted transition-colors"
      )}
      aria-label={`Switch to ${next} theme`}
    >
      <Icon className="w-4 h-4" />
    </button>
  );
}

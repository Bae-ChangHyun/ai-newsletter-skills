"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Search, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface SearchModalProps {
  open: boolean;
  onClose: () => void;
}

export function SearchModal({ open, onClose }: SearchModalProps) {
  const [query, setQuery] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  useEffect(() => {
    if (open) {
      setQuery("");
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [open]);

  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape" && open) {
        onClose();
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [open, onClose]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (query.trim()) {
      router.push(`/search?q=${encodeURIComponent(query.trim())}`);
      onClose();
    }
  }

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[100]">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative max-w-lg mx-auto mt-[20vh] px-4">
        <form
          onSubmit={handleSubmit}
          className="bg-background border border-border rounded-sm shadow-lg overflow-hidden"
        >
          <div className="flex items-center px-4 gap-3">
            <Search className="w-4 h-4 text-muted-foreground shrink-0" />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="기사 검색..."
              className="flex-1 py-3 text-sm bg-transparent focus:outline-none text-foreground placeholder:text-muted-foreground"
            />
            <button
              type="button"
              onClick={onClose}
              className="p-1 text-muted-foreground hover:text-foreground transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
          <div className="px-4 py-2 border-t border-border text-xs text-muted-foreground flex items-center justify-between">
            <span>Enter로 검색</span>
            <kbd className={cn(
              "px-1.5 py-0.5 rounded-sm text-[10px] font-mono",
              "bg-muted border border-border"
            )}>
              ESC
            </kbd>
          </div>
        </form>
      </div>
    </div>
  );
}

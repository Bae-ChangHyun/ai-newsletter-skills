"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Search, Menu, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { ThemeToggle } from "./ThemeToggle";
import { SearchModal } from "@/components/search/SearchModal";
import { useState, useEffect, useCallback } from "react";

const navItems = [
  { href: "/", label: "피드" },
  { href: "/weekly", label: "주간" },
  { href: "/trending", label: "트렌딩" },
  { href: "/tags", label: "태그" },
];

export function Header() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);

  const closeSearch = useCallback(() => setSearchOpen(false), []);

  // Cmd+K / Ctrl+K shortcut
  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setSearchOpen(true);
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  return (
    <>
      <header className="sticky top-0 z-50 bg-background/80 backdrop-blur-sm border-b border-border">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between h-12">
            {/* Logo */}
            <Link
              href="/"
              className="text-sm font-semibold tracking-tight text-foreground"
            >
              AI Trends
            </Link>

            {/* Desktop Nav */}
            <nav className="hidden sm:flex items-center gap-1">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "px-3 py-1.5 text-sm rounded-sm transition-colors",
                    pathname === item.href
                      ? "text-foreground bg-muted"
                      : "text-muted-foreground hover:text-foreground hover:bg-muted"
                  )}
                >
                  {item.label}
                </Link>
              ))}
            </nav>

            {/* Right actions */}
            <div className="flex items-center gap-1">
              {/* Search button with Cmd+K hint */}
              <button
                onClick={() => setSearchOpen(true)}
                className="flex items-center gap-1.5 p-1.5 rounded-sm text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
                aria-label="Search (Cmd+K)"
              >
                <Search className="w-4 h-4" />
                <kbd className="hidden sm:inline-flex px-1 py-0.5 text-[10px] font-mono bg-muted border border-border rounded-sm">
                  /K
                </kbd>
              </button>
              <ThemeToggle />
              <Link
                href="/auth/signin"
                className="hidden sm:inline-flex px-3 py-1 text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                로그인
              </Link>

              {/* Mobile menu toggle */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="sm:hidden p-1.5 rounded-sm text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
              >
                {mobileMenuOpen ? (
                  <X className="w-4 h-4" />
                ) : (
                  <Menu className="w-4 h-4" />
                )}
              </button>
            </div>
          </div>

          {/* Mobile Nav */}
          {mobileMenuOpen && (
            <nav className="sm:hidden py-2 border-t border-border">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={cn(
                    "block px-3 py-2 text-sm rounded-sm transition-colors",
                    pathname === item.href
                      ? "text-foreground bg-muted"
                      : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  {item.label}
                </Link>
              ))}
              <Link
                href="/auth/signin"
                onClick={() => setMobileMenuOpen(false)}
                className="block px-3 py-2 text-sm text-muted-foreground hover:text-foreground"
              >
                로그인
              </Link>
            </nav>
          )}
        </div>
      </header>

      <SearchModal open={searchOpen} onClose={closeSearch} />
    </>
  );
}

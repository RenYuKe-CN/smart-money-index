"use client";
import React from "react";
import Link from "next/link";
import { Search, Settings, AlertTriangle } from "lucide-react";

export default function Topbar({ onSearch }: { onSearch?: (q: string) => void }) {
  const handleKey = (e: React.KeyboardEvent) => { if (e.key === "Enter" && onSearch) onSearch((e.target as HTMLInputElement).value.toUpperCase()); };
  return (
    <header className="h-14 border-b border-[#1f2937] flex items-center justify-between px-6 bg-[#0a0e17]">
      <div className="flex items-center gap-3 flex-1 max-w-md">
        <Search size={16} className="text-[#4a5568]" />
        <input onKeyDown={handleKey} placeholder="搜索股票代码 (AAPL)..." className="w-full bg-transparent border-none text-sm text-[#e2e8f0] placeholder-[#4a5568] focus:outline-none" />
      </div>
      <div className="flex items-center gap-3">
        <Link href="/settings" className="text-[#7c8db5] hover:text-[#e2e8f0] transition-colors">
          <Settings size={18} />
        </Link>
      </div>
    </header>
  );
}
